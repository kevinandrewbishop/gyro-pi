from __future__ import division
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import datetime
from tornado import gen
import pifacedigitalio as p

piface = p.PiFaceDigital()
OUTPUT_PIN = 7

from tornado.options import define, options
define("port", default=8080, help="run on the given port", type=int)

client_message = 0
class Counter():
    def __init__(self):
        self.count = 0
        self.motor = True

    def increment(self):
        self.count += 1
        if self.count > 10:
            self.count = 1
        if self.count/10 > client_message:
            self.motor = False
        else:
            self.motor = True
        if self.motor:
            piface.output_pins[OUTPUT_PIN].value = 1
        else:
            piface.output_pins[OUTPUT_PIN].value = 0
        #print for debugging purposes. Comment this out when ready print Self count is %s and client_message is %s and motor is %s" %(self.count, client_message, self.motor)


counter = Counter()

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    client_message = 4
    def open(self):
        print 'new connection'
        self.write_message("connected")

    def on_message(self, message):
        print 'message received %s' % message
        self.write_message('message received %s' % message)
        global client_message
        if message == 'kill':
            client_message = 0
            piface.output_pins[OUTPUT_PIN].value = 0
        client_message = float(message)

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
    tornado.ioloop.PeriodicCallback(counter.increment, 2).start()
    main_loop.start()
