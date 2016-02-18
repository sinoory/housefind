import os.path

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import json,urllib
from tornado.options import define, options

from ctrl.houseMgoOp import HouseJobDbOpr
import pymongo
define("port", default=8800, help="run on the given port", type=int)


def getQuerryParam(param):
    print "getQuerryParam param=%s" %param
    js=eval(param)
    print js
    listSorts=[]
    if js.has_key('sort'):
        for si in js['sort']:
            listSorts.append((si['sortBy'],pymongo.ASCENDING if si['sortType']=='ascd' else pymongo.DESCENDING))
    print listSorts
    return js,listSorts


class WeatherQuerry(tornado.web.RequestHandler):
    htmlpage=""
    def get(self):
        self.render(self.htmlpage)
    def post(self):
        js,listSorts=getQuerryParam(self.request.body)
        print "post param json=%s" %js
        #res=wdb.querry(js['querry'],[])
        #self.write(json.dumps({"code":res}))

class PickHouseIndex(tornado.web.RequestHandler):
    htmlpage="pick.html"
    def get(self):
        self.render(self.htmlpage,start_id=0,total_rcd=wdb.count())

class PickHouse(tornado.web.RequestHandler):
    def get(self,houseId):
        print "houseId=%s" %houseId 
        print "totalcnt=%d" %wdb.count()
        res=wdb.get(int(houseId))
        print res
        self.write(json.dumps({"res":res}))
        


class QuerryHouse(WeatherQuerry):
    htmlpage="q.html"


class CityWeather(WeatherQuerry):
    htmlpage="city.html"

class Tst(WeatherQuerry):
    htmlpage="tst.html"

if __name__ == '__main__':
    wdb=HouseJobDbOpr()
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[(r'/', PickHouse), 
                  (r'/pick',PickHouseIndex),
                  (r'/q',QuerryHouse),
                  (r'/pick/(\d+)',PickHouse),
                 ],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "statics"),
        debug=True
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
