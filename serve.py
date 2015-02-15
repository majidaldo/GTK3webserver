import tornado
from tornado import websocket
import tornado.ioloop
import tornado.web
import atexit
import time
#from time import sleep
from random import getrandbits

polltime= 0*3600 +0*60  +10  # seconds chks usr active
responsetime= 5 #seconds response time given to usr

class alive(tornado.websocket.WebSocketHandler):
    clients={} #id:thisinst
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
            self.clients[self.id]=self
            #todo chk the id is the same one that was given
            #if self.id in application.handlers.dispalyhandler
            #    .self.clients[self.id]=self
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
display_spec={'gedit':['gedit'], 'bo':['boweb']
          ,'boNgedit':['bo','gedit']
		  }


#https for the websockets?
import uuid
import display
class DisplayHandler(tornado.web.RequestHandler):
    apps=[]
    clients={} # id:hdlrinst
    def prepare(self):
        self.id=uuid.uuid4()
        self.clients[self.id]=self
        self.display_num,self.display_port=display.add() #display.get_openport
        #problem: if browser didnt get back?
	    #tst by corrupting html
        display.app('gedit',self.display_num)
        hn=tornado.httpserver.socket.gethostname()
        self.html=open('broadway.html').read()\
	        .replace('$BROADWAY_SERVER'
	            ,"'http://"+hn+':'+str(self.display_port)+"/'")\
            .replace('$REQ_ID',str(self.id))
	    #need that last slash in url localhost:8080/        
    def get(self):
        self.write((self.html)) #no need for unicode?
    #make func: is my assoc ws alive??
    def on_finish(self):
        self.clients.pop(self.id)

#def make_DisplayHandler(display_spec):
#    class dh(DisplayHandler

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
	
