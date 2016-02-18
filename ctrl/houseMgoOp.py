#!/usr/bin/env python
#coding=utf-8
import sys

import pymongo
from pymongo import MongoClient

from bson import BSON 
from bson import json_util as jsonb
import json
#from m import JobDbOpr

class AbsDbOpr():
    def __init__(self):
        self.init()
    def init(self):
        client = MongoClient('localhost', 27017)
        self.db=client.houseDb
        self.tb=self.db.house58tb
        #As the is no auto increase id , and no cursor.prev() method
        #and cursor.skip() must >0 , so add auto increase id manually
        self.addIndex=self.tb.find({}).count()
    def isExist(self,jobDict,compareKey):
        cursor=self.tb.find({compareKey:jobDict[compareKey]})
        #cursor=self.tb.find({'houseUrl':jobDict['houseUrl']})
        return cursor.count()>0

    def querry(self,querryDic,sortList):
        dcursor=self.tb.find(querryDic)
        if len(sortList)>0:
            dcursor=dcursor.sort(sortList)

        return dcursor
            #print str((dcursor.count()))
            #return jsonb.dumps(list(dcursor))


    def add(self,jobDict):
        jobDict["mId"]=self.addIndex  #add auto increase id manually
        self.tb.insert(jobDict)
        self.addIndex+=1
    def rmAll(self):
        self.tb.remove({})
    def count(self):
        return self.tb.find({}).count()

    def get(self,rcdId):
        res=jsonb.dumps(list(self.tb.find({"mId":rcdId}))[0])
        print "HouseJobDbOpr.get(%s)=%s" %(rcdId,res)
        return res

class ReviewDbOpr(AbsDbOpr):
    pass
class SavedDbOpr():
    pass
class HouseJobDbOpr(ReviewDbOpr):
    pass


def sortDb():
    dbo=ReviewDbOpr()
    #w.querry({'yearmonth':"20134",'avgbWendu':{"$gte":10},'avgWencha':{"$lte":5}},[('tqqing', 1)])
    dc=dbo.querry({'distance':{"$lte":1000},'rooms':{"$lte":1},'size':{"$gte":15},'money':{"$lte":1200,"$gte":1000},'floor':{"$gte":5}},[('distance',1),('size',0),('money',1),('rooms',1)])
    cnt=0
    total=dc.count()
    for j in dc :
        if cnt>100 :
            break;
        cnt+=1
        print "=========="+str(cnt)+"================"
        info="\ndistance:"+str(j['distance'])+" price:"+str(j['money'])+" room"+str(j['rooms'])
        info+=(" South" if j['direct']==1 else " North")+" tel: "+j['tel']
        info+="\n"+j['houseTitle']
        info+="\n"+j['whole']
        info+="\n"+j['saleout']
        info+="\n"+j['houseUrl']
        print info
        print ""
    print "total:"+str(total)

def dctStr2Int(d,key):
    d[key]=int(d[key])

def test():
    dbo=HouseJobDbOpr()
    jobDict={'houseUrl':'http://sh.58.com/hezu/18576769395973x.shtml'}
    dbo.add(jobDict)
    print str(dbo.isExist(jobDict,"houseUrl"))
    dbo.rmAll()
    print str(dbo.isExist(jobDict,"houseUrl"))

def testIndex():
    dbo=HouseJobDbOpr()

def testf():
    class A():
        v="classA"
    ca=A()
    var="out"
    def inf(var,ca):
        var="in"
        ca.v="changedA.v"
    print var,ca.v
    inf(var,ca)
    print var,ca.v

def testdb():
    dbo=HouseJobDbOpr()
    print "totoal="+str(dbo.count())
    (dbo.get(9))
if __name__=="__main__":
    #testdb()
    if sys.argv[1] == "d" :
        test()
    elif sys.argv[1] == "s" :
        sortDb()
    elif sys.argv[1] == "t" :
        testf()
    else :
        print "Usage:"
        print "main d: test delete db"
        print "main s: sort db"

