#!/usr/bin/python
# -------_*_ coding: gbk _*_
'''
*
*  更新快频彩开奖结果
*
'''

import os
import getopt
import sys
import simplejson as json
import MySQLdb
from time import *

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
        
def Help():
    print "Usage: " + sys.argv[0] + " <lotteryId> [args:"
    print "\t -i : issue_no"
    sys.exit(-1)
    
def Warning(msg):
    os.system("/usr/local/agenttools/agent/agentRepStr 631765 '" + msg + "'")
        
def UpdateIssueTable(lotId, issueNo, resultOnly):
    '''将抓去结果写到DB, 没有考虑期号不存在的情况'''
    dbInfo = dict()
    dbInfo = InitDB()    
    if(dbInfo.has_key("error")):
        return(-1)
    try:
        lot_conn=MySQLdb.connect(host=dbInfo["host"],user=dbInfo["user"],passwd=dbInfo["pwd"],db=dbInfo["db"],port=int(dbInfo["port"]))
        lot_cur=lot_conn.cursor()
        #取得开奖信息表里的一条数据,要求:一 有效的 二 优先级高的
        sql = "select Fdraw_result,Fint1,Fdraw_info,Fchar1 from t_lottery_draw_result where Flottery_id='"+ lotId +"' and Fissue_no='"+ issueNo +"' and Fstatus in (0,2) and Fstate = 1 ORDER BY Fpriority DESC limit 1"
        #print sql
        src_count = lot_cur.execute(sql)
        if 0 == src_count:
            #没有有效数据，返回
            lot_cur.close()
            lot_conn.close()
            print "No draw result in t_lottery_draw_result currently,wait..."
            return (-1)
        src_data = lot_cur.fetchall()[0]
        src_draw_result = src_data[0].strip()
        src_draw_info = src_data[2].strip()
        src_lucky_ball = src_data[3].strip()

        #取得原扩展信息
        lot_json = dict()
        this_draw_time = "99999999999"
        sql = 'select Fext_info,fdraw_time from t_lottery_issue where Flottery_id="'+ lotId +'" and Fissue_no="'+ issueNo +'"'
        #print sql
        if 0 < lot_cur.execute(sql):
            rows = lot_cur.fetchall()
            src_ext_info = str(rows[0][0]).strip()
            this_draw_time = str(rows[0][1]).strip()
            if len(src_ext_info) > 1:
                lot_json = json.loads(src_ext_info)        
        
        if(len(src_draw_info) > 1):
            src_json = dict()
            src_json = json.loads(src_draw_info)
            if src_json.has_key("officialRetainAmount"):
                lot_json["officialRetainAmount"] = src_json["officialRetainAmount"]    
            if src_json.has_key("officialSellAmount"):
                lot_json["officialSellAmount"] = src_json["officialSellAmount"]
            if src_json.has_key("officialPrizeList"):
                lot_json["officialPrizeList"] = src_json["officialPrizeList"]    
            if src_json.has_key("official12SellAmount"):
                lot_json["official12SellAmount"] = src_json["official12SellAmount"] 
        else:
            #慢频彩抓开奖详情，开奖结果表里还未就绪，继续循环,快频彩就直接放过吧，实际上快频彩也不会有这种情况
            if(resultOnly == False):
                lot_cur.close()
                lot_conn.close()
                print "No draw info in t_lottery_draw_result currently,wait..."
                return (-1)

        sql = "UPDATE t_lottery_issue SET Fdraw_result='"+ src_draw_result +"'"
        sql = sql + ", Fext_info='"+ json.dumps(lot_json) + "'" 
        sql = sql + ", Flast_update_time=FROM_UNIXTIME("+ str(int(time())) + ")" 
        ##################################sql = "UPDATE t_lottery_issue SET Fchar1='"+ src_draw_result +"'"
        ##################################sql = sql + ", Fchar2='"+ json.dumps(lot_json) + "'" 
        if (len(src_lucky_ball) > 0):
            sql = sql + ", Fchar1='" + str(src_lucky_ball) + "'"
        sql = sql + " where Flottery_id='"+ lotId +"' and Fissue_no='"+ issueNo +"'"
        print sql
        n = lot_cur.execute(sql)
        print "Update t_lottery_issue num=" + str(n)
        
	#双色球和大乐透需要更新下一期的滚存
        if n > 0 and lot_json.has_key("officialRetainAmount"):
            #找到下一期
            sql = 'select fissue_id,fext_info from t_lottery_issue where flottery_id="%s" and fdraw_time>"%s" order by fdraw_time' % (lotId,this_draw_time)
	    lot_cur.execute(sql)
            rows = lot_cur.fetchall()
            if len(rows) > 0:
                src_ext = str(rows[0][1]).strip()
                src_ext_json = json.loads(src_ext)
                src_ext_json["officialRetainAmount"] = lot_json["officialRetainAmount"]
                sql = "update t_lottery_issue set Fext_info='%s' where fissue_id=%s" % (json.dumps(src_ext_json), str(rows[0][0]).strip())
		##################################sql = "update t_lottery_issue set fchar2='%s' where fissue_id=%s" % (json.dumps(src_ext_json), str(rows[0][0]).strip())
                lot_cur.execute(sql)
                print "update next issue succ,lottery_ud: %s, issue_id:%s" % (lotId,rows[0][0])
            else:
                print "error in find next issue_no,sql:",sql

	if n > 0:
            #更新t_lottery_draw_result的状态
            sql = "UPDATE t_lottery_draw_result SET Fstatus = Fstatus + 1 "
            sql = sql + " where Flottery_id='"+ lotId +"' and Fissue_no='"+ issueNo +"' and Fstatus in (0,2) and Fstate = 1 "
            #print sql
            n = lot_cur.execute(sql)

        lot_conn.commit()
        lot_cur.close()
        lot_conn.close()
        print "UpdateIssueTable SUCC for [%s %s] at %s" % (lotId,issueNo,strftime("%Y-%m-%d %H:%M:%S",localtime(int(time()))))
    except Exception, e:
        printExe("UpdateIssueTable FAIL for [%s %s]" % (lotId,issueNo))
        return(-1)        

# 返回数组：[抓取次数, sleep时间戳]        
def GetUpdateCnt(lotId):
    #普通彩30秒抓一次，一小时告警
    aNormalCntInfo = [120,30]    
    #快频彩10秒抓1次，5分钟告警
    aKPCCntInfo = [30,10]
    if(lotId == 'SSQ'):
        return aNormalCntInfo
    elif(lotId == 'QLC'):
        return aNormalCntInfo
    else:
        return [];    
        
#取未同步到期号表的抓取期号数据
def CountIssueNo(lotId):
    '''将抓去结果写到DB, 没有考虑期号不存在的情况'''
    dbInfo = dict()
    dbInfo = InitDB()
    issueNo = '';    
    if(dbInfo.has_key("error")):
        return(-1)
    try:
        print dbInfo["host"]
        lot_conn=MySQLdb.connect(host=dbInfo["host"],user=dbInfo["user"],passwd=dbInfo["pwd"],db=dbInfo["db"],port=int(dbInfo["port"]))
        lot_cur=lot_conn.cursor()
        sql = 'select DISTINCT Fissue_no from t_lottery_draw_result where Fstatus in (0,2) and Fstate = 1 and Flottery_id = "%s"' % (lotId)
        lot_cur.execute(sql)
        rows = lot_cur.fetchall()
        if len(rows) > 0:
            issueNo = str(rows[0][0]).strip()
            print "issue_no:%s" % (issueNo)
        else:
	    issueNo = -1
            print "no issue_no found,sql:",sql
        lot_conn.commit()
        lot_cur.close()
        lot_conn.close()
        print "CountIssueNo SUCC for [%s %s] at %s" % (lotId,issueNo,strftime("%Y-%m-%d %H:%M:%S",localtime(int(time()))))
	return issueNo
    except Exception, e:
        printExe("UpdateIssueTable FAIL for [%s %s]" % (lotId,issueNo))
        return(-1) 


    
    
#慢频彩更新开奖信息：SSQ\DLT\SD    
def UpdateUntilSucc(lotId, issueNo, resultOnly):
    ret = -1
    aCntInfo = GetUpdateCnt(lotId)
    if(len(aCntInfo) != 2):
        print "GetUpdateCnt error!"
        return -1
    run_cnt = 0
    iSantchCnt = int(aCntInfo[0])
    iSantchSlpTs = int(aCntInfo[1])
    print "begin to update lottery[%s] issue[%s] draw result" % (lotId, issueNo)
    while ret == -1 and run_cnt < iSantchCnt:
        ret = UpdateIssueTable(lotId, issueNo, True)
        run_cnt = run_cnt + 1
        if ret != -1:
            break
        sleep(iSantchSlpTs)
    if(ret == -1):
        print ("Fail To Update Issue Draw Result. LotteryId:%s, IssueNo: %s" % (lotId, issueNo))
	Warning("更新彩种【%s】第【%s】期开奖结果失败，请相关运营开发同学处理" % (lotId, issueNo))
        sys.exit(-1)    
            
#供外部调用
def IssueDrawUpdate(lotId, issueNo, resultOnly):
    print '='*9, strftime("%Y-%m-%d %H:%M:%S",localtime(int(time()))), '='*9
     
    if issueNo == "":        
        issueNo = CountIssueNo(lotId)
    if issueNo == -1 or len(issueNo) == 0:
        print "issue no is null, no need to update lotteryId[%s] issue." % (lotId)
        sys.exit(-1)
        
    if("SSQ" == lotId):
        #if(len(issueNo) != 7):
        #    print "query issueNo Fail!"
        #    sys.exit(-1)
        print "Update [SSQ] for NO." + issueNo
        UpdateUntilSucc(lotId, issueNo, resultOnly)  
    elif("QLC" == lotId):
        if(len(issueNo) != 7):
            print "query issueNo Fail!"
            sys.exit(-1)
        print "Update [QLC] for NO." + issueNo
        UpdateUntilSucc(lotId, issueNo, resultOnly)
    else:
        print "lottery id is invalid, lotteryId[%s]." % (lotId)
        sys.exit(-1)
        
    sys.exit(0)            
    
if __name__ == "__main__":
    print '='*9, strftime("%Y-%m-%d %H:%M:%S",localtime(int(time()))), '='*9
    os.chdir(sys.path[0])

    if(len(sys.argv) < 2):
        Help()
    
    
    resultOnly = False 
    issue_no = ""
    
    opts, args = getopt.getopt(sys.argv[2:], 'ri:', ['only_result', 'issue_no='])
    for option, value in opts:
        if option in ['-r', '--only_result']:
            print "only result"
            resultOnly = True
        if option in ['-i', '--issue_no']:
            issue_no = value
            
    IssueDrawUpdate(sys.argv[1], issue_no, resultOnly)
