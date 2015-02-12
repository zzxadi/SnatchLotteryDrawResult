#!/usr/bin/python
# -------_*_ coding: gbk _*_

import os
import getopt
import sys
import re
import urllib2
import simplejson as json
from time import *
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
import traceback
import socket
import MySQLdb

def printExe(errmsg):
    print errmsg, sys.exc_info()[0], sys.exc_info()[1]

def InitDB():
    dbInfo = dict()
    try:
        f = open("db.conf", 'r')
        for line in f:
            a = line.split('\n')
            a = a[0].split('\r')
            kv = a[0].split('=')
            if(2 != len(kv)):
                print "read db conf fail: %s" % (a[1])
                dbInfo["error"] = 1
                return dbInfos
            dbInfo[kv[0]] = kv[1]
    except Exception, e:
        printExe("Init DB fail: ")
        dbInfo["error"] = 1
    return dbInfo


def InsertGDSYXWDrawResult(lotId, issueNo, drawRet,srcNo):   
    print "InsertGDSYXWDrawResult begin!"
    dbInfo = dict()
    dbInfo = InitDB()    
    if(dbInfo.has_key("error")):
        return
    try:
        lot_conn=MySQLdb.connect(host=dbInfo["host"],user=dbInfo["user"],passwd=dbInfo["pwd"],db=dbInfo["db"],port=int(dbInfo["port"]),charset='gbk')
        lot_cur=lot_conn.cursor()
        
        sql = "SELECT * FROM t_lottery_draw_result WHERE lotteryId = '" + lotId + "' and issueNo = '" + issueNo + "';"
        n = lot_cur.execute(sql)
        if n > 0:
            sys.exit(0)
            
        sql = "INSERT INTO t_lottery_draw_result(lotteryId,issueNo,drawResult,createTime) "
        sql = sql + "VALUES('"+lotId+"','"+issueNo+"','"+drawRet['draw_result']+"',now());"
        print sql
        n = lot_cur.execute(sql)   
        lot_conn.commit()
        
        for item in range(12):
            print "item --> %s" % item
            levelSql = "INSERT INTO t_lottery_draw_level(lotteryId,issueNo,level,levelName,money,totalCount,createTime) "
            levelSql = levelSql + "VALUES('"+lotId+"','"+issueNo+"',"+ str(item) +",'"
            if item == 1: 
               levelSql = levelSql + "任选二" + "'," + str(600)
            elif item == 2:
               levelSql = levelSql + "任选三" + "'," + str(1900)
            elif item == 3: 
               levelSql = levelSql + "任选四" + "'," + str(7800)
            elif item == 4:
               levelSql = levelSql + "任选五" + "'," + str(54000)
            elif item == 5:
               levelSql = levelSql + "任选六" + "'," + str(9000)
            elif item == 6: 
               levelSql = levelSql + "任选七" + "'," + str(2600)
            elif item == 7:
               levelSql = levelSql + "任选八" + "'," + str(900)
            elif item == 8:
               levelSql = levelSql + "前一直选" + "'," + str(1300)
            elif item == 9: 
               levelSql = levelSql + "前二直选" + "'," + str(13000)
            elif item == 10:
               levelSql = levelSql + "前二组选" + "'," + str(6500)
            elif item == 11:
               levelSql = levelSql + "前三直选" + "'," + str(117000)
            else:
               levelSql = levelSql + "前三组选" + "'," + str(19500)
            levelSql = levelSql + "," + str(0) + ", now());"
            print "levelSql --> %s" % levelSql
            lot_cur.execute('SET NAMES gbk')
            lot_cur.execute(levelSql)   
            lot_conn.commit()

        lot_cur.close()
        lot_conn.close()
        print "InsertGDSYXWDrawResult SUCC for [%s %s %s] at %s" % (lotId,issueNo,drawRet['draw_result'],strftime("%Y-%m-%d %H:%M:%S",localtime(int(time()))))
        return 0
    except Exception, e:
        printExe("InsertGDSYXWDrawResult FAIL for [%s %s %s]" % (lotId,issueNo,drawRet['draw_result']))
        return(-1)


def SnatchGDSYXWDataFrom500(lotType, lotNo, resultOnly = False):
    date = strftime('%Y%m%d', localtime())
    #五百万的网站格式
    WURLFARMAT = 'http://kaijiang.500.com/static/info/kaijiang/xml/%s/%s.xml?ts=' + str(time())
    catchUrl = WURLFARMAT % (lotType, date)
    print "catchUrl :" + catchUrl
    
    try:   
        request = urllib2.Request(catchUrl, headers={"Accept" : "application/xml"})
        f = urllib2.urlopen(request)
        tree = ET.parse(f)
        root = tree.getroot()
        childCount = 0
        for child in root:
            childCount = childCount + 1 
        issueNo = root[childCount - 1].attrib['expect']
        drawResult = root[childCount - 1].attrib['opencode']

        ret = dict()
        ret['lot_id'] = lotType
        ret['issue_no'] = "20" + issueNo
        ret['draw_result'] = drawResult

        print 'ret --->', ret
       
        return ret
    except Exception, e:
        printExe("some error occurred!")
        return(-1)

# 返回数组：[抓取次数, sleep时间戳]        
def GetSnatchCnt(lotId):
    #普通彩30秒抓一次，一小时告警
    aNormalCntInfo = [120,30]    
    #快频彩10秒抓1次，5分钟告警
    aKPCCntInfo = [30,10]
    if(lotId == 'GDSYXW'):
        return aKPCCntInfo
    else:
        return []    


#抓奖：GDSYXW   
def SnatchMpcData(lotId, issueNo, resultOnly):
    
    ret = -1
    aCntInfo = GetSnatchCnt(lotId)
    if(len(aCntInfo) != 2):
        print "GetSnatchCnt error!"
        return -1
    run_cnt = 0
    iSantchCnt = int(aCntInfo[0])
    iSantchSlpTs = int(aCntInfo[1])
    print "begin to snatch lottery[%s] issue[%s] draw result" % (lotId, issueNo)
    while ret == -1 and run_cnt < iSantchCnt:
        if(lotId == 'GDSYXW'):
            ret = SnatchGDSYXWDataFrom500('gdsyxw', issueNo, resultOnly)
        else:
            break
        run_cnt = run_cnt + 1
        if ret != -1:
            break
        sleep(iSantchSlpTs)
    if(ret == -1):
        print ("Fail To Snatch Lottey Draw Result. LotteryId:%s, IssueNo: %s" % (lotId, issueNo))
        Warning("抓取彩种【%s】第【%s】期开奖结果失败，请相关运营开发同学处理" % (lotId, issueNo))
        sys.exit(-1)   
    #慢频彩现在都从500抓
    #InsertOrUpdateDrawResult(lotId, issueNo, ret, '500')
    issueNo = ret["issue_no"]
    print "issueNo %s" % issueNo
    InsertGDSYXWDrawResult(lotId, issueNo, ret, '500')

#供外部调用
def IssueDrawSnatch(lotId, issueNo, resultOnly):
    print '='*9, strftime("%Y-%m-%d %H:%M:%S",localtime(int(time()))), '='*9
    if lotId != "":
        SnatchMpcData(lotId, issueNo, resultOnly)
    else:
        print "lottery id is invalid, lotteryId[%s]." % (lotId)
        sys.exit(-1)

if __name__ == "__main__":
    print '='*9, strftime("%Y-%m-%d %H:%M:%S",localtime(int(time()))), '='*9
    os.chdir(sys.path[0])

    # if(len(sys.argv) < 2):
    #     Help()
    
    
    resultOnly = False 
    issue_no = ""
    
    # opts, args = getopt.getopt(sys.argv[2:], 'ri:', ['only_result', 'issue_no='])
    # for option, value in opts:
    #     if option in ['-r', '--only_result']:
    #         print "only result"
    #         resultOnly = True
    #     if option in ['-i', '--issue_no']:
    #         issue_no = value
    # print "resultOnly=" + str(resultOnly)
    IssueDrawSnatch(sys.argv[1], issue_no, resultOnly)