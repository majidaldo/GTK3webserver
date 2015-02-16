import tornado
from tornado import websocket
import tornado.ioloop
import tornado.web
import atexit
#from time import sleep
from random import getrandbits

#user
user_polltime= 0*3600 +0*60  +60  # seconds chks usr active
user_responsetime= 60 #seconds response time given to usr
#system
responsetime=10

class alive(tornado.websocket.WebSocketHandler):
    clients={} # id:this_instance . these are the the ids
    #..that were recd. not necessarily the one given on the
    #http request
    def check_origin(self,origin):return True #for ver 4

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
        print(message)
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
        print("WebSocket closed2")

apps={'boweb':  {'cmd':'python bo.py'},
      'gedit': {'cmd':'gedit'}
      }
display_spec={
            'gedit':{
                'apps':['gedit']
                ,'nicename':'gedit text editor'
                }
            , 'bo':{
                'apps':['boweb']
                ,'nicename':'bayesian optimization demo game'
                }
            ,'twoapps':{
                'apps':['bo','gedit']
                ,'nicename':'two apps at the same time'
                }
}


#https for the websockets?
import uuid
import display #for security the display connection..
#...needs to be rerouted or proxied. you could just scan
#the server and find an open port. also maybe can use
#secure websocket wss
#if you know a running port you can connect a client. so
#you could do a port scan. insecure.

import tornado.httpserver
hostname=tornado.httpserver.socket.gethostname()

id2displaynum={} # remove id on ws close . this is here
# incase the DisplayHandler gets garbage collected
#todo could add a periodc callback to rem inactive displays
#just in case

display_handlers={} # id: display handlers

class DisplayHandler(tornado.web.RequestHandler):
    apps=[]
    clients={} # id:hdlrinst. might be redundant..
    #..but everytime something goes in or out of clients
    #same action should be done to display_handlers
    #i put a global_display handlers to make it possible to 
    #have different classes of DisplayHandlers. so if you just
    #Know a reqid.. you wouldnt know which class of 
    #DisplayHandler it came from
    def prepare(self):
        self.tryn=0
        self.id=unicode(uuid.uuid4())
        self.clients[self.id]=self
        display_handlers[self.id]=self
  
 
    def get(self):
        #hacky but who cares..but see cant write a 'proper'
        #callback b/c idk what id i'm going to get back
        self.display_num,self.display_port=display.add() 
        #display.get_openport
        #problem: if browser didnt get back?
        #tst by corrupting html
        display.app('python bo.py',self.display_num)
        id2displaynum[self.id]=self.display_num
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

    #todo remove display on break connecton
    
    def on_finish(self):pass#i dont think this persists
      
#def make_DisplayHandler(display_spec):
#    class dh(DisplayHandler

#def get_DisplayHandler(id, #

application = tornado.web.Application([
    (r"/", DisplayHandler) 
    ,(r'/wsalive',alive)
]
,debug=True
)

def printstuff():
    stuff=[id2displaynum
	,display_handlers
	,alive.clients
	,DisplayHandler.clients
	]
    for at in stuff: print(at)

atexit.register( display.kill_all )

if __name__ == "__main__":
    lp=8888
    application.listen(lp)
    iolp=tornado.ioloop.IOLoop.instance()
    tornado.ioloop.PeriodicCallback(printstuff,2*1000)
    iolp.start()
    
