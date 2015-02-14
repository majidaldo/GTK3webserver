import tornado
from tornado import websocket
import tornado.ioloop
import tornado.web

import time
from time import sleep
class alive(tornado.websocket.WebSocketHandler):
    def check_origin(self,origin):return True

    def open(self):
        self.pt=tornado.ioloop.PeriodicCallback(self.poll,7000);
        self.pt.start() # PollTimer
        print('opened ws')
        #self.write_message(u"confirmcontinue")
        pass

    def on_message(self, message):
        print(message)
        if message=="pleasedontclose": self.pt.start()
        else:  self.close()
        #self.write_message(u"You said2: " + message)

    def poll(self):
        self.pt.stop()
        self.write_message(u"confirmcontinue")
        #response timer
        self.rt=iolp.call_later(3,lambda : self.on_message('close'))
        

    def on_close(self):
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
	
