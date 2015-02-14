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
        pass

		
    def on_message(self, message):
        if message=='pleasedontclose':
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
        self.rt=iolp.call_later(3
                ,self.closeifdue
				)

    def on_close(self): #but not wehen this obj closes
        self.dueclose=True
        print("WebSocket closed2")

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

if __name__ == "__main__":
    application.listen(8888)
    iolp=tornado.ioloop.IOLoop.instance()
    iolp.start()
	
