import tornado
from tornado import websocket
import tornado.ioloop
import tornado.web
import atexit
#from time import sleep

#should have used more obj oriented approach
#todo implement reset btn
#todo dont ask for confirmation if user is interacting

import display
display.port2display_function=display.sequence #might make ...
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
user_polltime= 0*3600 +5*60  +0  # seconds chks usr active
user_responsetime= 10 #seconds response time given to usr
#system
responsetime=5 #seconds. user should come back with a response
#to the request within this time

class alive(tornado.websocket.WebSocketHandler):
    """this just tracks and makes sure the user is active...
    because we need to stop the processes the start"""
    clients={} # id:this_instance . these are the the ids
    #..that were recd. not necessarily the one given on the
    #http request
    def check_origin(self,origin): return True #for tornado v4

    def open(self):
        self.id=None 
        self.dueclose=True
        self.pt=tornado.ioloop.PeriodicCallback(self.poll
             ,1000*( user_polltime ));
        self.pt.start() # PollTimer
        iolp.call_later(responsetime, self.closeif_noid)
        pass

    def closeif_noid(self):
        #also some housekeeping
        if self.id in display_handlers:
            for adisplayclassname in dh_classes:
                if self.id in dh_classes[adisplayclassname].clients:
                    dh_classes[adisplayclassname].clients\
                    .pop(self.id)
            display_handlers.pop(self.id)
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
        try: display_handlers.pop(self.id)
        except:pass
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
        #todo: should handle exceptions here
        self.display_num, self.display_port = \
                display.add(portgetter=display.webports) 
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
                .replace('$REQ_ID',str(self.id))\
                .replace('$BW_PORT',str(self.display_port))
                 #todo replace response time
                 # makint the timer for reset btn
                 #title
        #need that last slash in url localhost:8080/ 
        self.chkid=iolp.call_later(5,self.chk_id)
        self.write((self.html)) #no need for unicode?
        #self.chkid=tornado.ioloop.PeriodicCallback(\
        #                               self.chk_id,100)
        #self.chkid.start()
        
    def chk_id(self):#after a delay 
        """chks to see if reqid given back"""
        #self.tryn+=1
        #if self.tryn>3: self.chkid.stop(); return
        if self.id not in alive.clients:
            display.stop(self.display_num);
            try: id2displaynum.pop(self.id)
            except: pass
            display_handlers.pop(self.id)
            self.clients.pop(self.id)
            #self.chkid.stop()
        else: #pass # correct reqid came back
            #self.chkid.stop()
            self.clients.pop(self.id)
            display_handlers.pop(self.id)
        if self.id not in alive.clients: 
            #some more housekeeping
            try: self.clients.pop(self.id)
            except: pass
            try: display_handlers.pop(self.id)
            except: pass
            try: id2displaynum.pop(self.id)
            except: pass

    #def on_validid(self):pass 

    def morehousekeeping(self):
        try: self.clients.pop(self.id)
        except: pass
        try: display_handlers.pop(self.id)
        except: pass
    def on_finish(self):#pass#i dont think the obj persists
        #id2displaynum.pop(self.id)
        #self.clients.pop(self.id)
        #display_handlers.pop(self.id)
        self.hk=iolp.call_later(10,self.morehousekeeping)




def make_DisplayHandler(display_spec):
    class dh(DisplayHandler): clients={} ; 
    for aspec in display_spec:
        if aspec != 'kwargs':
            setattr(dh, aspec, display_spec[aspec])
    return dh



apps={'bo':  {'cmd':'/usr/bin/python bo.py'}

      }
display_specs={

            'bo':{
                'apps':['bo']
                ,'title':'bayesian optimization demo game'
                }

}

dh_classes=dict(
[(ads, make_DisplayHandler(display_specs[ads]))
for ads in display_specs])




def printstuff():
    stuff={
     'displays': display.display2port
     ,'id2displaynum':id2displaynum
    ,'display_handlers':display_handlers
    ,'alive.clients':alive.clients
    ,'DisplayHandler.clients':DisplayHandler.clients #only if..
    #...requesting root
    ,'boDisplayHnadler':dh_classes['bo'].clients
    }
    for at in stuff: print(at,stuff[at])
    print("")


atexit.register( display.kill_all )

if __name__ == "__main__":
    lp=8000 #listening port
    debug=False

    from collections import defaultdict as dd
    application = tornado.web.Application([
        #(r"/", DisplayHandler) ,
        (r'/wsalive',alive) ]
       +[(r'/'+adhc, dh_classes[adhc]
          , dd(lambda:{},display_specs[adhc])['kwargs'] )
          # {} if no kwargs available  
          for adhc in dh_classes]

    ,debug=debug
    )


    application.listen(lp)
    iolp=tornado.ioloop.IOLoop.instance()
    if debug is True:
        tornado.ioloop.PeriodicCallback(printstuff,5*1000).start()
    iolp.start()
