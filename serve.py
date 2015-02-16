import tornado
from tornado import websocket
import tornado.ioloop
import tornado.web
import atexit
#from time import sleep
from random import getrandbits

polltime= 0*3600 +0*60  +10  # seconds chks usr active
responsetime= 5 #seconds response time given to usr

class alive(tornado.websocket.WebSocketHandler):
    clients={} #id:this_instance
    def check_origin(self,origin):return True #for ver 4
    
    def open(self):
        self.dueclose=True
        self.pt=tornado.ioloop.PeriodicCallback(self.poll
             ,1000*( polltime ));
        self.pt.start() # PollTimer
        pass

    def on_message(self, message):
        print(message)
        if 'REQ_ID='==message[:7]:
            self.id=message[7:] 
            self.clients[self.id]=self;
            if self.id not in display_handlers:
                self.close(); self.on_close();
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
        self.rt=iolp.call_later(responsetime
                ,self.closeifdue
                )

    def on_close(self): #but not wehen this obj closes
        self.dueclose=True
        self.clients.pop(self.id) #pop other 'clientdicts too
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
				,'nicename':'bayesina optimization demo game'
				}
			,'twoapps':{
				'apps':['bo','gedit']
				,'nicename':'two apps at the same time'
				}
}

display_handlers={}
#



#https for the websockets?
import uuid
import display #for security the display connection..
#...needs to be rerouted or proxied. you could just scan
#the server and find an open port. also maybe can use
#secure websocket wss

import tornado.httpserver
hostname=tornado.httpserver.socket.gethostname()

class DisplayHandler(tornado.web.RequestHandler):
    apps=[]
    clients={} # id:hdlrinst
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
        display.app('gedit',self.display_num)
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
        self.chkid=tornado.ioloop.PeriodicCallback(           self.on_gotbackid,1000)
        self.chkid.start()
        
    def on_gotbackid(self):#after a delay unicode
        """chks to see if reqid given back"""
        self.tryn+=1
        if self.tryn>300: self.chkid.stop(); return
        if self.id not in alive.clients:
            display.stop(self.display_num) 
        else: # reqid came back
            self.chkid.stop()
            self.clients.pop(self.id)
            display_handlers.pop(self.id)


    #todo remove display on break connecton
    
    def on_finish(self):pass
        #hopefully this isn't called before chk_gotbackid?
        #does this persist?
      
#def make_DisplayHandler(display_spec):
#    class dh(DisplayHandler

#def get_DisplayHandler(id, #

application = tornado.web.Application([
    (r"/", DisplayHandler) 
    ,(r'/wsalive',alive)
]
,debug=True
)

def printstuff():pass

atexit.register( display.kill_all )

if __name__ == "__main__":
    lp=8888
    application.listen(lp)
    iolp=tornado.ioloop.IOLoop.instance()
    tornado.ioloop.PeriodicCallback(printstuff,10*1000)
    iolp.start()
    
