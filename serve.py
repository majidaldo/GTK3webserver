import tornado
from tornado import websocket
import tornado.ioloop
import tornado.web
import atexit
#from time import sleep

import display
display.port2display_function=display.sequence #will make..
#..use of the info that it's a sequence

#https for the websockets?
import uuid
import display #for security the display connection..
#...needs to be rerouted or proxied. you could just scan
#the server and find an open port. also maybe can use
#secure websocket wss. maybe a soln is to somehow intercept
#the connection request before the broadway server gets it
# and authenticate /that/ before passing on to the broadway
#server. 
#broadwayd has a unix port option. or maybe have broawayd
#only listen on localhost while the incoming gets proxied
#to it
#also DisplahHandler could be https

#if you know a running port you can connect a client. so
#you could do a port scan. insecure.

import tornado.httpserver
hostname=tornado.httpserver.socket.gethostname()

id2displaynum={} # remove id on ws close . this is here
# incase the DisplayHandler gets garbage collected
#todo could add a periodc callback to rem inactive displays
#just in case

display_handlers={} # id: display handlers


#todo would be nice to add a logger

#todo change title

#for devel make the following times short and debug=True

#user
user_polltime= 0*3600 +0*60  +10  # seconds chks usr active
user_responsetime= 5 #seconds response time given to usr
#system
responsetime=3 #seconds. user should come back with a response
#to the request within this time

class alive(tornado.websocket.WebSocketHandler):
    """this just tracks and makes sure the user is active...
    because we need to stop the processes the start"""
    clients={} # id:this_instance . these are the the ids
    #..that were recd. not necessarily the one given on the
    #http request
    def check_origin(self,origin): return True #for ver 4

    def closeif_noid(self):
        if self.id is None: self.close()

    def open(self):
        self.id=None 
        self.dueclose=True
        self.pt=tornado.ioloop.PeriodicCallback(self.poll
             ,1000*( user_polltime ));
        self.pt.start() # PollTimer
        iolp.call_later(responsetime, self.closeif_noid)
        pass

    def closeif_noid(self):
        if self.id is None: self.close()

    def on_message(self, message):
        #print(message)
        if 'REQ_ID='==message[:7]:
            self.id=message[7:] 
            self.clients[self.id]=self;
            if self.id not in display_handlers:
                self.close();
                #self.clients.pop(self.id)
                #self.pt.stop()
            #todo chk the id is the same one that was given
            #if self.id not in display_handlers: self.close()
        elif message=='pleasedontclose':
            #should rename dueclose to signify that it
            #blocks the response timer callback. but since
            #it works as is, i dont care! it was a pain
            #to program!
            self.dueclose=False; self.pt.start()
        else: self.dueclose==True ; self.closeifdue()

    def closeifdue(self):
        if self.dueclose==True: self.close()
        
    def poll(self):
        #print('poll')
        self.dueclose=True
        self.pt.stop()
        self.write_message(u"confirmcontinue")
        #response timer
        self.rt=iolp.call_later(user_responsetime
                ,self.closeifdue
                )

    def on_close(self): 
        self.dueclose=True
        self.pt.stop()
        if self.id is not None: self.clients.pop(self.id)
        try: display.stop(id2displaynum[self.id])
        except: pass
        try: id2displaynum.pop(self.id)
        except: pass # warning: invalid reqid recvd or None
        #print("WebSocket closed2")





class DisplayHandler(tornado.web.RequestHandler):
    apps=[]
    clients={} # id:hdlrinst. might be redundant..
    #..but everytime something goes in or out of clients
    #same action should be done to display_handlers
    #i put a global_display handlers to make it possible to 
    #have different classes of DisplayHandlers. so if you just
    #know a reqid.. you wouldnt know which class of 
    #DisplayHandler it came from
    def prepare(self):
        #self.tryn=0
        self.id=unicode(uuid.uuid4())
        self.clients[self.id]=self
        display_handlers[self.id]=self

    def start_apps(self):
        #ideally this starts when an adequate reponse comes
        #back..but then again the broadway server has to 
        #be ready before the request comes in?
        self.display_num, self.display_port = display.add() 
        #display.get_openport
        #problem: if browser didnt get back?
        #tst by corrupting html
        id2displaynum[self.id]=self.display_num
        for ap in self.apps:
            display.app(apps[ap]['cmd'],self.display_num)

    def get(self):
        self.start_apps()

        hn=hostname
        #todo use tornado templates?
        self.html=open('broadway.html').read()\
                 .replace('$BROADWAY_SERVER'
                 ,"'http://"+hn+':'+str(self.display_port)+"/'")\
                .replace('$REQ_ID',str(self.id))\
                .replace('$APP_PRT',str(lp)) #wasteful
                 #todo replace response time
                 # makint the timer for reset btn
                 #title
        #need that last slash in url localhost:8080/    
        self.write((self.html)) #no need for unicode?
        self.chkid=iolp.call_later(5,self.chk_id)
        #self.chkid=tornado.ioloop.PeriodicCallback(\
        #                               self.chk_id,100)
        #self.chkid.start()
        
    def chk_id(self):#after a delay 
        """chks to see if reqid given back"""
        #self.tryn+=1
        #if self.tryn>3: self.chkid.stop(); return
        if self.id not in alive.clients:
            display.stop(self.display_num);
            #self.chkid.stop()
            #id2displaynum.pop(self.id)
        else: # correct reqid came back
            #self.chkid.stop()
            self.clients.pop(self.id)
            display_handlers.pop(self.id)

    def on_validid(self):pass

    
    def on_finish(self):pass#i dont think the obj persists



apps={'bo':  {'cmd':'python bo.py'},
      'gedit': {'cmd':'gedit'}
      }
display_specs={
            'gedit':{#could have "kwargs":...
                'apps':['gedit']
                ,'title':'gedit text editor'
                }
            , 'bo':{
                'apps':['bo']
                ,'title':'bayesian optimization demo game'
                }
            ,'twoapps':{
                'apps':['bo','gedit']
                ,'title':'two apps at the same time'
                }
}


def make_DisplayHandler(display_spec):
    class dh(DisplayHandler): pass
    for aspec in display_spec:
        if aspec != 'kwargs':
            setattr(dh, aspec, display_spec[aspec])
    return dh

dh_classes=dict(
[(ads, make_DisplayHandler(display_specs[ads]))
for ads in display_specs])



from collections import defaultdict as dd
application = tornado.web.Application([
    (r"/", DisplayHandler) 
    ,(r'/wsalive',alive) ]
   +[(r'/'+adhc, dh_classes[adhc]
      , dd(lambda:{},display_specs[adhc])['kwargs'] )
      # {} if no kwargs available  
      for adhc in dh_classes]

,debug=True
)

#another check todo
#since i'm just increasing the display number, remove any
#process that has a number lower than the current lowest 
#display number found in display


def printstuff():
    stuff={
	 'displays': display.display2port
     ,'id2displaynum':id2displaynum
    ,'display_handlers':display_handlers
    ,'alive.clients':alive.clients
    ,'DisplayHandler.clients':DisplayHandler.clients
    }
    for at in stuff: print(at,stuff[at])
    print("")

atexit.register( display.kill_all )

if __name__ == "__main__":
    lp=8888
    application.listen(lp)
    iolp=tornado.ioloop.IOLoop.instance()
    tornado.ioloop.PeriodicCallback(printstuff,5*1000).start()
    iolp.start()
