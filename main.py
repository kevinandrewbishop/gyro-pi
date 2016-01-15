from __future__ import division
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import datetime
from tornado import gen

from tornado.options import define, options
define("port", default=8080, help="run on the given port", type=int)

alpha = 50
class Counter():
    def __init__(self):
        self.count = 0
        self.motor = True

    def increment(self):
        self.count += 1
        if self.count > 20:
            self.count = 1
        if self.count/20 > alpha/100:
            self.motor = False
        else:
            self.motor = True
        #print for debugging purposes. Comment this out when ready
        print "Self count is %s and alpha is %s and motor is %s" %(self.count, alpha, self.motor) 


counter = Counter()

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    alpha = 4
    def open(self):
        print 'new connection'
        self.write_message("connected")

    def on_message(self, message):
        print 'message received %s' % message
        self.write_message('message received %s' % message)
        self.alpha = int(message)
        global alpha
        alpha = int(message)

    def on_close(self):
        print 'connection closed'

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r"/", IndexHandler),
            (r"/ws", WebSocketHandler)
        ]
    )
    httpServer = tornado.httpserver.HTTPServer(app)
    httpServer.listen(options.port,address='0.0.0.0')
    print "Listening on port:", options.port
    main_loop = tornado.ioloop.IOLoop.instance()
    #main_loop.add_timeout(datetime.timedelta(seconds=2), test)
    tornado.ioloop.PeriodicCallback(counter.increment, 100).start()
    main_loop.start()
