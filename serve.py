import tornado
from tornado import websocket
import tornado.ioloop
import tornado.web

import time
from time import sleep

polltime= 0*3600 +0*60  +10  # seconds chks usr active
responsetime= 5 #seconds response time given to usr

class alive(tornado.websocket.WebSocketHandler):
    def check_origin(self,origin):return True #for ver 4

    def open(self):
        self.dueclose=True
        self.pt=tornado.ioloop.PeriodicCallback(self.poll
		     ,1000*( polltime ));
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
        self.rt=iolp.call_later(responsetime
                ,self.closeifdue
				)

    def on_close(self): #but not wehen this obj closes
        self.dueclose=True
        print("WebSocket closed2")

#tornado.httpserver.socket.gethostname()
#def put_broadwayaddr
#need that last slash like localhost:8080/
#open('broadway.html').read().replace('$BROADWAY_SERVER',WITH)

import display
class MainHandler(tornado.web.RequestHandler):
    def get(self):
       dn,prt=display.add()
       #problem: if browser didnt get back?
	   #tst by corrupting html
       svr=tornado.httpserver.socket.gethostname()
       html=self.write(open('broadway.html').read().\
	   replace('$BROADWAY_SERVER'
	   ,"'http://"+svr+':'+str(lp)+"/'"))
       self.write(unicode(html))
    #make func: is my assoc ws alive??
	   
application = tornado.web.Application([
    (r"/", MainHandler)
    ,(r'/wsalive',alive)
]
,debug=True
)

from random import randint

if __name__ == "__main__":
    lp=8888
    application.listen(lp)
    iolp=tornado.ioloop.IOLoop.instance()
    iolp.start()
	
