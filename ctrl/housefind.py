# -*- coding:utf-8 -*-
#!/usr/bin/python
import sys
reload(sys)
sys.setdefaultencoding('utf8')

sys.path.append("/home/sin/wkspace/soft/python/pub/web/")
sys.path.append("/home/sin/wkspace/soft/python/pub/utility/")
from getPage import HtmlReader
from QtPage import Render,WebkitRender
from uty import *
from houseMgoOp import HouseJobDbOpr
import urllib

from bs4 import BeautifulSoup

#from jangopub import ormsettingconfig


if __name__=='__main__':
    print "config "
    #ormsettingconfig()

import re

class BadUrl():
    def __init__(self,url,reason,title=""):
        self.url=url
        self.reason=reason
        self.urltitle=title
    def toStr(self):
        return "BadUrl<%s , %s , %s>" %(self.url,self.reason,self.urltitle)

    def __unicode__(self):
        return "BadUrl<%s , %s>" %(self,url,self.reason)

USER_STOPED=-1
UNDEFINDED=-2

class JobStrategy():
    def isJobSuilt(self,jobstr,keysDict):
        for k in keysDict:
            if jobstr.find(k.upper()) != -1:
                return True
        return False

class HtmlGetStrategy():
    mExtralInfo={'jobDescribe':'','companyDesc':''}
    lastDescConame=[]
    def load(self,url):
        r=HtmlReader(url,timeout=120)
        r.run()
        self.outdata=r.outdata
    def data(self):
        return self.outdata


class RenderHtmlGetStrategy(HtmlGetStrategy):
    def load(self,url):
        wr=WebkitRender(url,60,5)
        wr.load()
        self.date="%s" %wr.data()
    def data(self):
        return self.date
gLinesconf={
    "7":{
        "on":1,
        "urls":[
            {
                "url":"l579495/s579615_579566_579527_579528_579494",
                "desc":"高科西路站 杨高南路站 锦绣路站 芳华路站 花木路站",
                "on":1
            },
        ]
    },
    "2":{
        "on":1,
        "urls":[
            {
                "url":"l236722/s579487_579492_579496_579622_579675",
                "desc":"广兰路站 张江高科站 龙阳路站 世纪公园站 上海科技馆站",
                "on":1
            },
            {
                "url":"l236722/s579489_579684_579682",
                "desc":"世纪大道 金科路站 东昌路站",
                "on":1
            },

        ]
    },
    "9":{
        "on":1,
        "urls":[
            {
                "url":"l236728/s579704_579664_579665_579657_579656",
                "desc":"杨高中路站 陆家浜路站 马当路站 打浦桥站 嘉善路站",
                "on":1
            },
        ]
    },
    "4":{
        "on":1,
        "urls":[
            {
                "url":"l236724/s579676_579674_236926_579667_236928",
                "desc":"浦电路站 蓝村路站 塘桥 南浦大桥站 西藏南路",
                "on":1
            },
            {
                "url":"l236724/s579543_579709_579713_236922_598286",
                "desc":"海伦路站 临平路站 大连路站 杨树浦路 浦东大道站",
                "on":1
            },

        ]
    },
    "6":{
        "on":1,
        "urls":[
            {
                "url":"l236726/s579672_236958_645295_236959_579614",
                "desc":"民生路站 源深体育中心  上海儿童医学中心 浦电路站 临沂新村站",
                "on":1
            },
        ]
    },

}



def getLInt(s,sep):
    d=""
    sepindex=s.index(sep)
    while True:
        c=s[sepindex-1:sepindex]
        if c.isdigit() or c=="." :
            d+=c
            sepindex-=1
        else :
            break
    d=d[::-1]
    if d.find(".")!=-1:
        return d[:d.index(".")]
    return d



class HouseBusyness():
    def setLines(self,ls):
        self.mLines=ls
    def isValid(self,infodic,qurryDict):
        return True
    def getPageUrl(self,pageIndex,qurryDict):
        return self.mLines.getPageUrl(pageIndex,{})
    def describe(self,infodic):
        res= "第"+str(infodic['floor'])+"层"+" 面积"+str(infodic['size'])+"m"+" 朝向"+("南" if infodic['direct']==1 else "北")
        res=str(infodic['money'])+"/月 "+res+" "+str(infodic['rooms'])+"室 "+infodic['tel']
        print res
    def getDetailInfo(self,houseDetailPageUrl,infodic):
        trycnt=0
        while trycnt<5:
            try:
                subreader=HtmlReader(houseDetailPageUrl,retrycnt=5)
                subreader.run()
                subs=BeautifulSoup(subreader.outdata,fromEncoding="utf-8")
                
                #detailDes=subs.findAll(name="div",attrs={"class":re.compile(r"col_sub.*")})[0]
                #detailDes=subs.findAll(name="div",attrs={"class":re.compile(r"sumary.*")})[0]
                #detailDes=subs.findAll(name="div",attrs={"class":re.compile(r"col_sub sumary")})[0]

                dt=subs.findAll(name="div",attrs={"class":'col_sub sumary'})
                if len(dt)==0 :
                    dt=subs.findAll(name="div",attrs={"class":'col_sub sumary '})
                detailDes=dt[0]
                break
            except Exception, e:
                trycnt=trycnt+1
                continue
        #try:
        mny=detailDes.findAll("span",{"class":"bigpri arial"})[0].get_text()
        if mny.find("面议")!=-1 or len(mny)<3:
            mny="9999"
        infodic['money']=int(mny)
        if len(detailDes.findAll(text="整体"))>0 :
            simpleDesc=rmSpace(detailDes.findAll(text="整体")[0].parent.nextSibling.nextSibling.get_text())
        elif len(detailDes.findAll(text="概况"))>0 :
            simpleDesc=rmSpace(detailDes.findAll(text="概况")[0].parent.nextSibling.nextSibling.get_text())
        infodic['whole']=simpleDesc
        print "simpleDesc: "+simpleDesc
        infodic['size']=int(getLInt(simpleDesc,"㎡")) if simpleDesc.find("㎡")>0 else 0
        howmayrooms=simpleDesc[simpleDesc.find("室")-1:simpleDesc.find("室")]
        infodic['rooms']=int(howmayrooms)
        if simpleDesc.find("层")>0 :
            floor=simpleDesc[simpleDesc.find("/")-2:simpleDesc.find("/")-1]
        else:
            simpleDesc=rmSpace(detailDes.findAll(text="楼层")[0].parent.nextSibling.nextSibling.get_text())
            floor=simpleDesc[simpleDesc.find("/")-2:simpleDesc.find("/")-1]
        infodic['floor']=int(floor)
        #fine the direct
        if len(detailDes.findAll(text="出租"))>0:
            simpleDesc=rmSpace(detailDes.findAll(text="出租")[0].parent.nextSibling.nextSibling.get_text())
        infodic['saleout']=simpleDesc
        infodic['direct']=1
        if simpleDesc.find("朝向北")>0 :
            infodic['direct']=0
        if infodic['size']==0:
            infodic['size']=int(getlDigital(simpleDesc,"㎡")) if simpleDesc.find("㎡")>0 else 0

        infodic['tel']=''
        if len(subs.findAll('span',{"id":"t_phone"}))>0:
            infodic['tel']=rmSpace(subs.findAll('span',{"id":"t_phone"})[0].get_text())
        self.describe(infodic)
        #except Exception, e:
        #    print e
        return infodic



class JobDbOpr():
    def isJobExist(self,jobDict):
        pass
    def isOutData(self,jobDict):
        pass
    def add(self,jobDict):
        pass
    def update(self,jobDict):
        pass

class StrategyFactory():
    def __init__(self,factype):
        if factype==1:
            self.htmlGetor=RenderHtmlGetStrategy()
            self.jobOpr=HouseJobDbOpr()
            print "StrategyFactory[RenderHtmlGetStrategy,JobCompScoreOpr]"
        else:
            self.htmlGetor=HtmlGetStrategy()
            self.jobOpr=HouseJobDbOpr()
            print "StrategyFactory[HtmlGetStrategy,JobDbOpr]"


def rmSpace(text):
    return text.replace(" ","").replace("\t","").replace("\r\n","").replace("\n","")

import datetime,time
def waitTime(lastTime,interval):
    if lastTime is None :
        lastTime=datetime.datetime.now()-datetime.timedelta(hours=10)
    now=datetime.datetime.now()
    if (now-lastTime).seconds<interval:
        tosleep=interval-((now-lastTime).seconds)
        print "waitTime need sleep "+str(tosleep)+"s"
        time.sleep(tosleep)

import re
def getlDigital(strl,before):
    res=re.findall(r"[0-9|.]+"+before,strl)
    if(len(res)==0):
        return 0;
    return float(res[0][:-len(before)])

def getlDigitalTest():
    print "res="+str(int(getlDigital("1室1厅1卫  35.3㎡  普通住宅  精装修  朝向南","㎡")))
    


class Job51Adder():
    unprocessedUrls=[]
    isRuning=False
    userStopped=False
    mJobStrategy=JobStrategy()
    busyness=HouseBusyness()
    mPageJobsNotEnought=0
    def init(self):
        self.unprocessedUrls=[]
        self.userStopped=False
        self.mHtmlGetStrategy.lastDescConame=[]
    def setQuerryDict(self,querryDict):
        self.mQuerryDic=querryDict
        print "setQuerryDict querryDict=%s" %querryDict
        self.mFilterKeys=querryDict.get("filterkeys").split(",")
        print "self.mFilterKeys type=%s l=%s" %(type(self.mFilterKeys),self.mFilterKeys)
        strategyFactory=StrategyFactory(int(self.mQuerryDic['serverActionType']))
        self.mJobOprStrategy=strategyFactory.jobOpr
        self.mHtmlGetStrategy=strategyFactory.htmlGetor

    def addJob(self,startpage=1,endpage=50):
        self.init()

        isRuning=True
        self.mFinishReason="FINISH_OK"
        gotcnt=0
        st=getCurTime() #from uty.py
        for l,v in gLinesconf.items():
            if v['on']!=1 :
                continue
            for urld in v['urls']:
                if urld['on']!=1 :
                    continue
                print "processing line%s %s" %(l,urld['desc'])
                loop=startpage
                lastPageTime=None
                jobs,urljobs=UNDEFINDED,0
                while(loop<=endpage or endpage==-1):
                    waitTime(lastPageTime,1)
                    url="http://sh.58.com/chuzu/sub/%s/%s?ClickID=1" %(urld['url'],"" if loop==1 else "/pn"+str(loop)+"/")
                    print "page url="+url
                    jobs,url,res=self.addOnePageJob(url)
                    lastPageTime=datetime.datetime.now()
                    if res=="FINISH_END" :
                        print "Finish current search,as ended in page "+url
                        self.mFinishReason="REACH_END"
                        break;            
                    elif res=="NEED_RETRY":
                        continue
                    elif jobs==USER_STOPED or self.userStopped:
                        print "user stopped,exit addJob"
                        self.mFinishReason="STOP"
                        exit()
                    loop+=1;
                    gotcnt+=jobs
                    urljobs+=jobs
                #end while
                urld['gotcnt']=urljobs
                print "====StartPage=%s===Loop=%s=EndPage=%s====jobs=%s=============" %(startpage,loop,endpage,jobs)
                print "============%s===>%s=======================================" %(st,getCurTime())
        print "Total got :"+str(gotcnt)
        for bu in self.unprocessedUrls:
            print bu.toStr()
        for l,v in gLinesconf.items():
            if v['on']!=1 :
                continue
            for urld in v['urls']:
                if urld['on']==1 :
                    print urld['desc']+" get "+str(urld['gotcnt'])+" jobs"
    def addOnePageJob(self,pagesearchurl):
        jbo = self.mJobOprStrategy #JobCompScoreOpr() #JobDbOpr()
        reader=HtmlReader(pagesearchurl,retrycnt=5)
        #reader=WebkitRender(pagesearchurl,timeout=10,retrycnt=5)
        reader.run()
        #print reader.outdata
        #exit()
        #BeautifulSoup will try to get encode from page  <meta  content="text/html; charset=gb2312">
        #here the data from HtmlReader is already utf8,not meta gb2312,so pass utf-8 to its construct to force encoding,
        #otherwise the BeautifulSoup can't work
        soup=BeautifulSoup(reader.outdata,fromEncoding="utf-8")
        print "process %s" %pagesearchurl
        #get item divs
        if len(soup.findAll("table",{"class":"tbimg"}))==0:
            print "Warning:"
            uinput=raw_input("maybe need enter authenticate code, press to continue ...\n")
            return 0,"","NEED_RETRY"
        olTag=soup.findAll("table",{"class":"tbimg"})[0].findAll("tr")
        cnt=0
        for j in olTag :
            infodic={}
            if self.userStopped :
                return USER_STOPED,pagesearchurl
            infodic['houseUrl']=j.findAll("h1")[0].findAll("a")[0].get('href')
            if len(j.findAll("span",{"class":"img_picCount"}))==0 :
                print "%s No picture ,ignore" %infodic['houseUrl']
                continue
            infodic['houseTitle']=j.findAll("h1")[0].findAll("a")[0].get_text()
            JuliDate=rmSpace(j.findAll("p",{"class":"qj-renaddr"})[0].get_text())
            print "JuliDate="+JuliDate
            if not (JuliDate.find("今天")>0 or JuliDate.find("小时")>0 or JuliDate.find("分钟")>0):
                print "not today,finish, "+JuliDate
                print infodic['houseUrl']
                return cnt,"","FINISH_END"
            if JuliDate.find("约")==-1 :
                print "Invalid JuliDate,no distence info,ignore"
                continue

            mny=j.findAll("b",{"class":"pri"})
            if len(mny)==0:
                print "No price info,ignore"
                continue
            mny=rmSpace(mny[0].get_text())
            mny=int(mny if mny.find('.')==-1 else mny[:mny.find('.')])
            if mny>1300 or mny<800 :
                print "Invalid price "+str(mny)+" ,out of [800,1300], ignore"
                continue
            infodic['distance']=int(getJuli(JuliDate))
            print "distance="+str(infodic['distance'])

            self.getDetailInfo(infodic['houseUrl'],infodic)

            if not self.busyness.isValid(infodic,self.mQuerryDic):
                continue
            if jbo.isExist(infodic,"houseUrl"):
                print "Ignore house %s,exist in db" %infodic['houseTitle']
                continue
            infodic['status']='null' #null get watch
            jbo.add(infodic)
            print "db record="+str(jbo.count())

            cnt+=1
        if len(olTag)<5:
            self.mPageJobsNotEnought+=1
            if self.mPageJobsNotEnought>3 :
                print "jobs in page less then 5, appear 4 times, may need finish"
                return cnt,"","FINISH_END"
        else :
            self.mPageJobsNotEnought=0
        #print "cnt=%d self.mPageJobsNotEnought=%d" %(cnt,self.mPageJobsNotEnought)
        return cnt,pagesearchurl,"FINISH_OK"

    def getDetailInfo(self,url,infodic):
        self.busyness.getDetailInfo(url,infodic)

    def rmHtmlTag(self,html):
        html=html.replace("<br>","\n").replace("</br>","")
        html=html.replace("<div>","\n").replace("</div>","")
        html=html.replace("<p>","\n").replace("</p>","")
        html=re.sub(r'</?\w+[^>]*>','',html)
        return html

def testf():
    x1="out"
    def innerf():
        x1="in"
    print x1
    innerf()
    print x1

import re
def getJuli(JuliDate):
    JuliDate=JuliDate.encode('utf-8')
    p=re.compile(r'.*约(\d+)米.*')
    m=p.search(JuliDate)
    return m.group(1)
        
def testJuli():
    JuliDate="紫薇景苑张江高科紫薇景苑800到18001室1厅1卫35平米租房-离金科路站约1090米/今天/随时入住"
    print getJuli(JuliDate)

if __name__=="__main__":
    jobadder=Job51Adder()
    qd={'filterkeys':'linux','keywordtype':'100','serverActionType':55}
    jobadder.setQuerryDict(qd)

    if len(sys.argv)<2 :
        print "Usage: param :"
        print "     t: test"
        print "     f: find"
        exit()
    if sys.argv[1] == "t" :
        #getlDigitalTest();
        testJuli()
        exit()
    if sys.argv[1] == "d" :
        jobadder.getDetailInfo('http://sh.58.com/hezu/21944223778186x.shtml',{})
        exit()

    #testLine()
    #jobadder.addOnePageJob(2)
    jobadder.addJob(1,-1)
    #jobadder.tst()
    #jobadder.getDetailInfo('http://sh.58.com/zufang/21897940955427x.shtml',{})
    #jobadder.getDetailInfo('http://sh.58.com/hezu/18709816762889x.shtml',{})
    #jobadder.getDetailInfo('http://sh.58.com/hezu/18676639081098x.shtml',{})
    #jobadder.getDetailInfo('http://sh.58.com/hezu/18570002733960x.shtml?PGTID=14051414899220.24612266244366765&ClickID=6',{})
