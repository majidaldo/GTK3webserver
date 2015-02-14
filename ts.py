import tornado
from tornado import websocket
import tornado.ioloop
import tornado.web

import time
from time import sleep

class alive(tornado.websocket.WebSocketHandler):
    def check_origin(self,origin):return True #for ver 4

    def open(self):
        self.dueclose=True
        self.pt=tornado.ioloop.PeriodicCallback(self.poll
		     ,1000*( 0*3600 +0*60  +7  ));
        self.pt.start() # PollTimer
        print('opened ws')
        #self.write_message(u"confirmcontinue")
        pass

		
    def on_message(self, message):
        print self.dueclose, message
        if message=='pleasedontclose':
            self.dueclose=False; self.pt.start()
        else: self.dueclose==True ; self.closeifdue()
        # if self.dueclose==True:
            # if message=='pleasedontclose':
                # self.pt.start(); self.dueclose=True; return
            # #elif: message=='close': self.pt.stop(); self.close(); return
            # else: self.pt.stop(); self.close(); return
        # else:#have to be explicit bc it was hard!
            # if message=='pleasedontclose':
                # self.pt.start(); self.dueclose=True; return
            # else: self.pt.stop(); self.close(); return
        #if already closed 
        #if self.closeswitch==True: return
            # if message=='pleasedontclose': return
            # else: 
        # if message=='close' and self.closeswitch==True:return
        # else: self.closeswitch=True
        # #now just respond to the switch
        # if self.closeswitch==False: self.pt.start();
        # else: self.pt.stop(); self.close()
        
        #onlyu responding to pleasedontclose
        #since i responded , now switch it back
        #if message=='pleasedontclose': self.closeswitch=True
        #else: self.closeswitch=False

            # if message!='pleasedontclose'
        # if self.lastmessage=='close':
            # message=
        # #now just respond to the switch
        # if self.lastmessage=='close': return #already closed
        # if ((self.lastmessage=='pleasedontclose' \
           # or self.lastmessage=='') \
            # and message=='close'): self.close()
        # if message=="pleasedontclose": self.pt.start()
        # else:  self.close()
        # #self.write_message(u"You said2: " + message)

    def closeifdue(self):
        if self.dueclose==True: self.close()
		
    def poll(self):
        self.dueclose=True
        #self.closeswitch=False #since im asking, dont close
        self.pt.stop()
        self.write_message(u"confirmcontinue")
        #response timer
        self.rt=iolp.call_later(3
		       #,lambda : self.on_message('close')
                ,self.closeifdue
				)

    def on_close(self): #but not wehen this obj closes
        self.dueclose=True
        print("WebSocket closed2")
        #self.pt.stop() ; del self.pt #do i need to del?

#tornado.httpserver.socket.gethostname()
#def put_broadwayaddr


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

application = tornado.web.Application([
    (r"/", MainHandler)
    ,(r'/wsalive',alive)
]
,debug=True
)

from random import randint
#def delay(): alive.write_message(u"confirmcontinue"); print(str(randint(1,100)))

if __name__ == "__main__":
    application.listen(8888)
    iolp=tornado.ioloop.IOLoop.instance()
    #iolp.add_callback( pc )
    iolp.start()
	
