#!/usr/bin/python
# -------_*_ coding: gbk _*_

import os
import getopt
import sys
import re
import urllib
import simplejson as json
from time import *
import xml.etree.cElementTree as ET
import traceback
import socket
import MySQLdb



def printExe(errmsg):
    print errmsg, sys.exc_info()[0], sys.exc_info()[1]
        
def Help():
    print "Usage: " + sys.argv[0] + " <lotteryId> [args:"
    print "\t -r : only for result num"
    print "\t -i : issue_no"
    sys.exit(-1)
    
def Warning(msg):
    os.system("/usr/local/agenttools/agent/agentRepStr 631765 '" + msg + "'")

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

################# SSQ #################
def CheckSSQResult(ret):
    print "mytest ret=" + str(ret)
    blueBall = int(ret['draw_result'].split('|')[1])
    #print "blueBall is :", blueBall
    if blueBall < 1 or blueBall > 16:
        print "error red ball : ", blueBall
        return False

    redBalls = ret['draw_result'].split('|')[0].split(',')
    print "red balls are :", str(redBalls)
    for redB in redBalls:
        if int(redB) < 1 or int(redB) > 33:
            print "error red ball: " , str(blueBalls)
            return False

    ext = ret['ext_info']
    #print json.dumps(ext['officialPrizeList'])
    #for node in ext['officialPrizeList']:
    #    if int(node['count']) < 1 or (int(node['prize']) < 500):
    #        print "error official prize list ", str(ext['officialPrizeList'])
    #        return False

    #if ext["officialRetainAmount"] < 10000:
    #    print "error officialRetainAmount :", ext["officialRetainAmount"]
    #    return False
    #if ext["officialSellAmount"] < 10000:
    #    print "error officialSellAmount :", ext["officialSellAmount"]
    #    return False

    return True

def HaveSSQFloat(_level1_count, _level1_prize, _level2_count, _level2_prize):
    if _level1_count != 0 and _level1_prize == 0 or _level2_count != 0 and _level2_prize == 0 or _level1_prize == 0 and _level2_prize == 0:
        return False
    return True

def SnatchSSQDataFrom500(lotType, lotNo, resultOnly = False):
    lot_no = lotNo[2:]
    #五百万的网站格式
    WURLFARMAT = 'http://kaijiang.500.com/shtml/%s/%s.shtml?ts=' + str(time())
    #开奖结果正则
    RE_RESULT_RED  = re.compile(r'<li class="ball_red">(\d+)</li>', re.I)
    RE_RESULT_BLUE = re.compile(r'<li class="ball_blue">(\d+)</li>', re.I)
    RE_DRAW_DAY    = re.compile(r'开奖日期：(?P<Y>\d+)年(?P<M>\d+)月(?P<D>\d+)', re.I)
    RE_SELL_AMOUNT = re.compile(r'本期销量：[^>]*>([\d,]*)元', re.I)
    RE_RETAIN_AMOUNT = re.compile(r'奖池滚存：[\s\S]*>([\d,]*)元', re.I)
    RE_ISSUE_NO = re.compile(r'双色球 第[\s\S]*>(\d+)</strong></font>[\s\S]*期', re.I)
    RE_LEVEL_1 = re.compile(r'一等奖</td>[^0-9/]*(?P<count>\d+)</td>[^0-9/]*(?P<prize>[\d,]*)</td>', re.I)
    RE_LEVEL_2 = re.compile(r'二等奖</td>[^0-9/]*(?P<count>\d+)</td>[^0-9/]*(?P<prize>[\d,]*)</td>', re.I)
    RE_LEVEL_3 = re.compile(r'三等奖</td>[^0-9/]*(?P<count>\d+)</td>[^0-9/]*(?P<prize>[\d,]*)</td>', re.I)
    RE_LEVEL_4 = re.compile(r'四等奖</td>[^0-9/]*(?P<count>\d+)</td>[^0-9/]*(?P<prize>[\d,]*)</td>', re.I)
    RE_LEVEL_5 = re.compile(r'五等奖</td>[^0-9/]*(?P<count>\d+)</td>[^0-9/]*(?P<prize>[\d,]*)</td>', re.I)
    RE_LEVEL_6 = re.compile(r'六等奖</td>[^0-9/]*(?P<count>\d+)</td>[^0-9/]*(?P<prize>[\d,]*)</td>', re.I)
    catchUrl = WURLFARMAT % (lotType, lot_no)
    print "catchUrl :" + catchUrl
    
    try:
        f = urllib.urlopen(catchUrl)
        html = f.read()
        #print str([item for item in RE_RESULT_RED.findall(html)])
        #print str([item for item in RE_RESULT_BLUE.findall(html)])
        #print str([item for item in RE_DRAW_DAY.findall(html)])
        #print str([item for item in RE_SELL_AMOUNT.findall(html)])
        #print str([item for item in RE_RETAIN_AMOUNT.findall(html)])
        #print str([item for item in RE_ISSUE_NO.findall(html)])
        #print str([item for item in RE_LEVEL_1.findall(html)])
        #print str([item for item in RE_LEVEL_2.findall(html)])
        #print str([item for item in RE_LEVEL_3.findall(html)])
        #print str([item for item in RE_LEVEL_4.findall(html)])
        #print str([item for item in RE_LEVEL_5.findall(html)])
        #print str([item for item in RE_LEVEL_6.findall(html)])
        redBalls = [item for item in RE_RESULT_RED.findall(html)]
        blueBalls = [item for item in RE_RESULT_BLUE.findall(html)]

        if(len(redBalls) != 6 or len(blueBalls) != 1):
            print "regular error!"
            return (-1)
            
        for redB in redBalls:
            if int(redB) < 1 or int(redB) > 33:
                print "error red ball: " , redB
                return -1
        if(int(blueBalls[0]) < 1 or int(blueBalls[0]) > 16):
            print "error blue ball:", blueBalls[0]
            return -1
        
        _result = ','.join(redBalls) + '|' + blueBalls[0]
        print "result : " + _result
        
        if (resultOnly == True):
            ret = dict()
            ret['draw_result'] = _result
            print "Snatch for result only, succ!"
            return ret
        drawDays = [item for item in RE_DRAW_DAY.findall(html)]
        #print "drawDays : " + str(drawDays)
        sellAmount = [item for item in RE_SELL_AMOUNT.findall(html)]
        print "sellAmount : " + str(sellAmount)
        retainAmount = [item for item in RE_RETAIN_AMOUNT.findall(html)]
        print "retainAmount : " + str(retainAmount)
        issueNo = [item for item in RE_ISSUE_NO.findall(html)]
        #print "issueNo : " + str(issueNo)
        level1 = [item for item in RE_LEVEL_1.findall(html)]
        level2 = [item for item in RE_LEVEL_2.findall(html)]
        level3 = [item for item in RE_LEVEL_3.findall(html)]
        level4 = [item for item in RE_LEVEL_4.findall(html)]
        level5 = [item for item in RE_LEVEL_5.findall(html)]
        level6 = [item for item in RE_LEVEL_6.findall(html)]
        #print "level1 : " + str(level1)

        try:
            _sellAmount = int(sellAmount[0].replace(",", "").replace("-","0")) * 100
            print "sellAmount : " + str(_sellAmount)
            _retainAmount = int(retainAmount[0].replace(",", "").replace("-","0")) * 100
            print "retainAmount : " + str(_retainAmount)
            _level1_count = int(level1[0][0].replace("-","0"))
            _level1_prize = int(level1[0][1].replace(",", "").replace("-","0")) * 100
            _level2_count = int(level2[0][0].replace("-","0"))
            _level2_prize = int(level2[0][1].replace(",", "").replace("-","0")) * 100
            _level3_count = int(level3[0][0].replace("-","0"))
            _level3_prize = int(level3[0][1].replace(",", "").replace("-","0")) * 100
            _level4_count = int(level4[0][0].replace("-","0"))
            _level4_prize = int(level4[0][1].replace(",", "").replace("-","0")) * 100
            _level5_count = int(level5[0][0].replace("-","0"))
            _level5_prize = int(level5[0][1].replace(",", "").replace("-","0")) * 100
            _level6_count = int(level6[0][0].replace("-","0"))
            _level6_prize = int(level6[0][1].replace(",", "").replace("-","0")) * 100
            #print "level6 count:" + str(_level6_count) + " prize: " + str(_level6_prize)
        except Exception, e:
            _sellAmount = 0
            _retainAmount = 0
            _level1_count = 0
            _level1_prize = 0
            _level2_count = 0
            _level2_prize = 0
            _level3_count = 0
            _level3_prize = 3000*100
            _level4_count = 0
            _level4_prize = 200*100
            _level5_count = 0
            _level5_prize = 10*100
            _level6_count = 0
            _level6_prize = 5*100

        lot_json = dict()
        lot_json['officialRetainAmount'] = _retainAmount
        lot_json['officialSellAmount'] = _sellAmount
        lot_json['officialPrizeList'] = [dict() for x in range(6)] 
        lot_json['officialPrizeList'][0]['level'] = 1
        lot_json['officialPrizeList'][0]['count'] = _level1_count
        lot_json['officialPrizeList'][0]['prize'] = _level1_prize
        lot_json['officialPrizeList'][1]['level'] = 2
        lot_json['officialPrizeList'][1]['count'] = _level2_count
        lot_json['officialPrizeList'][1]['prize'] = _level2_prize
        lot_json['officialPrizeList'][2]['level'] = 3
        lot_json['officialPrizeList'][2]['count'] = _level3_count
        lot_json['officialPrizeList'][2]['prize'] = _level3_prize
        lot_json['officialPrizeList'][3]['level'] = 4
        lot_json['officialPrizeList'][3]['count'] = _level4_count
        lot_json['officialPrizeList'][3]['prize'] = _level4_prize
        lot_json['officialPrizeList'][4]['level'] = 5
        lot_json['officialPrizeList'][4]['count'] = _level5_count
        lot_json['officialPrizeList'][4]['prize'] = _level5_prize
        lot_json['officialPrizeList'][5]['level'] = 6
        lot_json['officialPrizeList'][5]['count'] = _level6_count
        lot_json['officialPrizeList'][5]['prize'] = _level6_prize
        
        #print  json.dumps(lot_json)
        ret = dict()
        ret['ext_info'] = lot_json
        ret['lot_id'] = lotType
        ret['issue_no'] = lotNo
        ret['draw_result'] = _result
        ret['retain_amount'] = _retainAmount
        if HaveSSQFloat(_level1_count, _level1_prize, _level2_count, _level2_prize):
            #大奖已开出
            ret['float_flag'] = 1
        else:
            #大奖未开出
            ret['float_flag'] = 0
        if CheckSSQResult(ret):
            print lot_json
            return ret
        else:
            print "CheckSSQResult Fail!"
            return (-1)
    except Exception, e:
        printExe("some error occurred!")
        return(-1)


         
################# QLC #################      
def CheckQLCResult(ret):
    print "mytest ret=" + str(ret)
    blueBall = int(ret['draw_result'].split('|')[1])
    #print "blueBall is :", blueBall
    if blueBall < 1 or blueBall > 30:
        print "error red ball : ", blueBall
        return False
    
    redBalls = ret['draw_result'].split('|')[0].split(',')
    print "red balls are :", str(redBalls)
    for redB in redBalls:
        if int(redB) < 1 or int(redB) > 30:
            print "error red ball: " , str(blueBalls)
            return False

    ext = ret['ext_info']
    #print json.dumps(ext['officialPrizeList'])
    #for node in ext['officialPrizeList']:
    #    if int(node['count']) < 1 or (int(node['prize']) < 400):
    #        print "error official prize list ", str(ext['officialPrizeList'])
    #        return False
    
    #if ext["officialRetainAmount"] < 10000:
    #    print "error officialRetainAmount :", ext["officialRetainAmount"]
    #    return False
    #if ext["officialSellAmount"] < 10000:
    #    print "error officialSellAmount :", ext["officialSellAmount"]
    #    return False
    
    return True
  

def HaveQLCFloat(_level1_count, _level1_prize, _level2_count, _level2_prize, _level3_count, _level3_prize):
    if _level1_count != 0 and _level1_prize == 0 or _level2_count != 0 and _level2_prize == 0 or _level3_count != 0 and _level3_prize == 0 or _level1_prize == 0 and _level2_prize == 0 and _level3_prize == 0:
        return False
    return True

def SnatchQLCDataFrom500(lotType, lotNo, resultOnly = False):
    lot_no = lotNo[2:]
    #五百万的网站格式
    WURLFARMAT = 'http://kaijiang.500.com/shtml/%s/%s.shtml?ts=' + str(time())
    #开奖结果正则
    RE_RESULT_RED  = re.compile(r'<li class="ball_red">(\d+)</li>', re.I)
    RE_RESULT_BLUE = re.compile(r'<li class="ball_blue">(\d+)</li>', re.I)
    RE_DRAW_DAY    = re.compile(r'开奖日期：(?P<Y>\d+)年(?P<M>\d+)月(?P<D>\d+)', re.I)
    RE_SELL_AMOUNT = re.compile(r'本期销量：[^>]*>([\d,]*)元', re.I)
    RE_RETAIN_AMOUNT = re.compile(r'奖池滚存：[\s\S]*>([\d,]*)元', re.I)
    RE_ISSUE_NO = re.compile(r'七乐彩 第[\s\S]*>(\d+)</strong></font>[\s\S]*期', re.I)
    RE_LEVEL_1 = re.compile(r'一等奖</td>[^0-9/]*(?P<count>\d+)</td>[^0-9/]*(?P<prize>[\d,]*)</td>', re.I)
    RE_LEVEL_2 = re.compile(r'二等奖</td>[^0-9/]*(?P<count>\d+)</td>[^0-9/]*(?P<prize>[\d,]*)</td>', re.I)
    RE_LEVEL_3 = re.compile(r'三等奖</td>[^0-9/]*(?P<count>\d+)</td>[^0-9/]*(?P<prize>[\d,]*)</td>', re.I)
    RE_LEVEL_4 = re.compile(r'四等奖</td>[^0-9/]*(?P<count>\d+)</td>[^0-9/]*(?P<prize>[\d,]*)</td>', re.I)
    RE_LEVEL_5 = re.compile(r'五等奖</td>[^0-9/]*(?P<count>\d+)</td>[^0-9/]*(?P<prize>[\d,]*)</td>', re.I)
    RE_LEVEL_6 = re.compile(r'六等奖</td>[^0-9/]*(?P<count>\d+)</td>[^0-9/]*(?P<prize>[\d,]*)</td>', re.I)
    RE_LEVEL_7 = re.compile(r'七等奖</td>[^0-9/]*(?P<count>\d+)</td>[^0-9/]*(?P<prize>[\d,]*)</td>', re.I)
    catchUrl = WURLFARMAT % (lotType, lot_no)
    print "catchUrl :" + catchUrl
    
    try:
        f = urllib.urlopen(catchUrl)
        html = f.read()
        #print str([item for item in RE_RESULT_RED.findall(html)])
        #print str([item for item in RE_RESULT_BLUE.findall(html)])
        #print str([item for item in RE_DRAW_DAY.findall(html)])
        #print str([item for item in RE_SELL_AMOUNT.findall(html)])
        #print str([item for item in RE_RETAIN_AMOUNT.findall(html)])
        #print str([item for item in RE_ISSUE_NO.findall(html)])
        #print str([item for item in RE_LEVEL_1.findall(html)])
        #print str([item for item in RE_LEVEL_2.findall(html)])
        #print str([item for item in RE_LEVEL_3.findall(html)])
        #print str([item for item in RE_LEVEL_4.findall(html)])
        #print str([item for item in RE_LEVEL_5.findall(html)])
        #print str([item for item in RE_LEVEL_6.findall(html)])
        #print str([item for item in RE_LEVEL_7.findall(html)])
        redBalls = [item for item in RE_RESULT_RED.findall(html)]
        blueBalls = [item for item in RE_RESULT_BLUE.findall(html)]
        
        if(len(redBalls) != 7 or len(blueBalls) != 1):
            print "regular error!"
            return (-1)
            
        for redB in redBalls:
            if int(redB) < 1 or int(redB) > 30:
                print "error red ball: " , redB
                return -1
        if(int(blueBalls[0]) < 1 or int(blueBalls[0]) > 30):
            print "error blue ball:", blueBalls[0]
            return -1
        
        _result = ','.join(redBalls) + '|' + blueBalls[0]
        print "result : " + _result
        
        if (resultOnly == True):
            ret = dict()
            ret['draw_result'] = _result
            print "Snatch for result only, succ!"
            return ret
        
        drawDays = [item for item in RE_DRAW_DAY.findall(html)]
        print "drawDays : " + str(drawDays)
        sellAmount = [item for item in RE_SELL_AMOUNT.findall(html)]
        print "sellAmount : " + str(sellAmount)
        retainAmount = [item for item in RE_RETAIN_AMOUNT.findall(html)]
        print "retainAmount : " + str(retainAmount)
        issueNo = [item for item in RE_ISSUE_NO.findall(html)]
        #print "issueNo : " + str(issueNo)
        level1 = [item for item in RE_LEVEL_1.findall(html)]
        level2 = [item for item in RE_LEVEL_2.findall(html)]
        level3 = [item for item in RE_LEVEL_3.findall(html)]
        level4 = [item for item in RE_LEVEL_4.findall(html)]
        level5 = [item for item in RE_LEVEL_5.findall(html)]
        level6 = [item for item in RE_LEVEL_6.findall(html)]
        level7 = [item for item in RE_LEVEL_7.findall(html)]
        #print "level1 : " + str(level1)

        try:
            _sellAmount = int(sellAmount[0].replace(",", "").replace("-","0")) * 100
            print "sellAmount : " + str(_sellAmount)
            _retainAmount = int(retainAmount[0].replace(",", "").replace("-","0")) * 100
            print "retainAmount : " + str(_retainAmount)
            _level1_count = int(level1[0][0].replace("-","0"))
            _level1_prize = int(level1[0][1].replace(",", "").replace("-","0")) * 100
            _level2_count = int(level2[0][0].replace("-","0"))
            _level2_prize = int(level2[0][1].replace(",", "").replace("-","0")) * 100
            _level3_count = int(level3[0][0].replace("-","0"))
            _level3_prize = int(level3[0][1].replace(",", "").replace("-","0")) * 100
            _level4_count = int(level4[0][0].replace("-","0"))
            _level4_prize = int(level4[0][1].replace(",", "").replace("-","0")) * 100
            _level5_count = int(level5[0][0].replace("-","0"))
            _level5_prize = int(level5[0][1].replace(",", "").replace("-","0")) * 100
            _level6_count = int(level6[0][0].replace("-","0"))
            _level6_prize = int(level6[0][1].replace(",", "").replace("-","0")) * 100
            _level7_count = int(level7[0][0].replace("-","0"))
            _level7_prize = int(level7[0][1].replace(",", "").replace("-","0")) * 100
            #print "level7 count:" + str(_level7_count) + " prize: " + str(_level7_prize)
        except Exception, e:
            _sellAmount = 0
            _retainAmount = 0
            _level1_count = 0
            _level1_prize = 0
            _level2_count = 0
            _level2_prize = 0
            _level3_count = 0
            _level3_prize = 0
            _level4_count = 0
            _level4_prize = 200 * 100
            _level5_count = 0
            _level5_prize = 50 * 100
            _level6_count = 0
            _level6_prize = 10 * 100
            _level7_count = 0
            _level7_prize = 5 * 100
        

        lot_json = dict()
        lot_json['officialRetainAmount'] = _retainAmount
        lot_json['officialSellAmount'] = _sellAmount
        lot_json['officialPrizeList'] = [dict() for x in range(7)] 
        lot_json['officialPrizeList'][0]['level'] = 1
        lot_json['officialPrizeList'][0]['count'] = _level1_count
        lot_json['officialPrizeList'][0]['prize'] = _level1_prize
        lot_json['officialPrizeList'][1]['level'] = 2
        lot_json['officialPrizeList'][1]['count'] = _level2_count
        lot_json['officialPrizeList'][1]['prize'] = _level2_prize
        lot_json['officialPrizeList'][2]['level'] = 3
        lot_json['officialPrizeList'][2]['count'] = _level3_count
        lot_json['officialPrizeList'][2]['prize'] = _level3_prize
        lot_json['officialPrizeList'][3]['level'] = 4
        lot_json['officialPrizeList'][3]['count'] = _level4_count
        lot_json['officialPrizeList'][3]['prize'] = _level4_prize
        lot_json['officialPrizeList'][4]['level'] = 5
        lot_json['officialPrizeList'][4]['count'] = _level5_count
        lot_json['officialPrizeList'][4]['prize'] = _level5_prize
        lot_json['officialPrizeList'][5]['level'] = 6
        lot_json['officialPrizeList'][5]['count'] = _level6_count
        lot_json['officialPrizeList'][5]['prize'] = _level6_prize
        lot_json['officialPrizeList'][6]['level'] = 7
        lot_json['officialPrizeList'][6]['count'] = _level7_count
        lot_json['officialPrizeList'][6]['prize'] = _level7_prize
        
        #print  json.dumps(lot_json)
        ret = dict()
        ret['ext_info'] = lot_json
        ret['lot_id'] = lotType
        ret['issue_no'] = lotNo
        ret['draw_result'] = _result
        ret['retain_amount'] = _retainAmount
        if HaveQLCFloat(_level1_count, _level1_prize, _level2_count, _level2_prize, _level3_count, _level3_prize):
            #大奖已开出
            ret['float_flag'] = 1
        else:
            #大奖未开出
            ret['float_flag'] = 0

        if CheckQLCResult(ret):
            return ret
        else:
            print "CheckQLCResult Fail!"
            return (-1)
    except Exception, e:
        printExe("some error occurred!")
        return(-1)    

def SnatchDLTDataFrom500(lotType, lotNo, resultOnly = False):
    lot_no = lotNo[2:]
    
    WURLFARMAT = 'http://kaijiang.500.com/shtml/%s/%s.shtml?ts=' + str(time())
    
    RE_RESULT_RED  = re.compile(r'<li class="ball_red">(\d+)</li>', re.I)
    RE_RESULT_BLUE = re.compile(r'<li class="ball_blue">(\d+)</li>', re.I)
    RE_DRAW_DAY    = re.compile(r'开奖日期：(?P<Y>\d+)年(?P<M>\d+)月(?P<D>\d+)', re.I)
    RE_SELL_AMOUNT = re.compile(r'本期销量：[^>]*>([\d,]*)元', re.I)
    RE_RETAIN_AMOUNT = re.compile(r'奖池滚存：[\s\S]*>([\d,]*)元', re.I)
    RE_ISSUE_NO = re.compile(r'超级大乐透 第[\s\S]*>(\d+)</strong></font>[\s\S]*期', re.I)
    RE_LEVEL_1 = re.compile(r'一等奖</td>[\s\S]*?<td>基本</td>[^0-9/]*(?P<basecount>\d+)</td>[^0-9/]*(?P<baseprize>[\d,]*)</td>[\s\S]*?<td>追加</td>[^0-9/]*(?P<appendcount>\d+)</td>[^0-9/]*(?P<appendprize>[\d,]*)</td>', re.I)
    RE_LEVEL_2 = re.compile(r'二等奖</td>[\s\S]*?<td>基本</td>[^0-9/]*(?P<basecount>\d+)</td>[^0-9/]*(?P<baseprize>[\d,]*)</td>[\s\S]*?<td>追加</td>[^0-9/]*(?P<appendcount>\d+)</td>[^0-9/]*(?P<appendprize>[\d,]*)</td>', re.I)
    RE_LEVEL_3 = re.compile(r'三等奖</td>[\s\S]*?<td>基本</td>[^0-9/]*(?P<basecount>\d+)</td>[^0-9/]*(?P<baseprize>[\d,]*)</td>[\s\S]*?<td>追加</td>[^0-9/]*(?P<appendcount>\d+)</td>[^0-9/]*(?P<appendprize>[\d,]*)</td>', re.I)
    RE_LEVEL_4 = re.compile(r'四等奖</td>[\s\S]*?<td>基本</td>[^0-9/]*(?P<basecount>\d+)</td>[^0-9/]*(?P<baseprize>[\d,]*)</td>[\s\S]*?<td>追加</td>[^0-9/]*(?P<appendcount>\d+)</td>[^0-9/]*(?P<appendprize>[\d,]*)</td>', re.I)
    RE_LEVEL_5 = re.compile(r'五等奖</td>[\s\S]*?<td>基本</td>[^0-9/]*(?P<basecount>\d+)</td>[^0-9/]*(?P<baseprize>[\d,]*)</td>[\s\S]*?<td>追加</td>[^0-9/]*(?P<appendcount>\d+)</td>[^0-9/]*(?P<appendprize>[\d,]*)</td>', re.I)
    RE_LEVEL_6 = re.compile(r'六等奖</td>[^0-9/]*(?P<basecount>\d+)</td>[^0-9/]*(?P<baseprize>[\d,]*)</td>', re.I)
    catchUrl = WURLFARMAT % (lotType, lot_no)
    print "catchUrl :" + catchUrl
    
    try:
        f = urllib.urlopen(catchUrl)
        html = f.read()
        print str([item for item in RE_RESULT_RED.findall(html)])
        print str([item for item in RE_RESULT_BLUE.findall(html)])
        print str([item for item in RE_DRAW_DAY.findall(html)])
        print str([item for item in RE_SELL_AMOUNT.findall(html)])
        print str([item for item in RE_RETAIN_AMOUNT.findall(html)])
        print str([item for item in RE_ISSUE_NO.findall(html)])
        print str([item for item in RE_LEVEL_1.findall(html)])
        print str([item for item in RE_LEVEL_2.findall(html)])
        print str([item for item in RE_LEVEL_3.findall(html)])
        print str([item for item in RE_LEVEL_4.findall(html)])
        print str([item for item in RE_LEVEL_5.findall(html)])
        print str([item for item in RE_LEVEL_6.findall(html)])
        # print str([item for item in RE_LEVEL_7.findall(html)])
        redBalls = [item for item in RE_RESULT_RED.findall(html)]
        blueBalls = [item for item in RE_RESULT_BLUE.findall(html)]
        _result = ','.join(redBalls) + ':' + ','.join(blueBalls)

        print "draw result: ", _result

        if(len(redBalls) != 5 or len(blueBalls) != 2):
            print "regular error!"
            return (-1)
            
        for redB in redBalls:
            if int(redB) < 1 or int(redB) > 35:
                print "error red ball: " , redB
                return -1
        if(int(blueBalls[0]) < 1 or int(blueBalls[0]) > 12):
            print "error blue ball:", blueBalls[0]
            return -1      

        if (resultOnly == True):
            ret = dict()
            ret['draw_result'] = _result
            print "Snatch for result only, succ!"
            return ret
        drawDays = [item for item in RE_DRAW_DAY.findall(html)]
        #print "drawDays : " + str(drawDays)
        sellAmount = [item for item in RE_SELL_AMOUNT.findall(html)]
        print "sellAmount : " + str(sellAmount)
        retainAmount = [item for item in RE_RETAIN_AMOUNT.findall(html)]
        print "retainAmount : " + str(retainAmount)
        issueNo = [item for item in RE_ISSUE_NO.findall(html)]
        #print "issueNo : " + str(issueNo)
        level1 = [item for item in RE_LEVEL_1.findall(html)]
        level2 = [item for item in RE_LEVEL_2.findall(html)]
        level3 = [item for item in RE_LEVEL_3.findall(html)]
        level4 = [item for item in RE_LEVEL_4.findall(html)]
        level5 = [item for item in RE_LEVEL_5.findall(html)]
        level6 = [item for item in RE_LEVEL_6.findall(html)]

        try:
            _sellAmount = int(sellAmount[0].replace(",", "").replace("-","0")) * 100
            print "sellAmount : " + str(_sellAmount)
            _retainAmount = int(retainAmount[0].replace(",", "").replace("-","0")) * 100
            print "retainAmount : " + str(_retainAmount)
            _level1_basecount = int(level1[0][0].replace("-","0"))
            _level1_baseprize = int(level1[0][1].replace(",", "").replace("-","0")) * 100
            _level2_basecount = int(level2[0][0].replace("-","0"))
            _level2_baseprize = int(level2[0][1].replace(",", "").replace("-","0")) * 100
            _level3_basecount = int(level3[0][0].replace("-","0"))
            _level3_baseprize = int(level3[0][1].replace(",", "").replace("-","0")) * 100
            _level4_basecount = int(level4[0][0].replace("-","0"))
            _level4_baseprize = int(level4[0][1].replace(",", "").replace("-","0")) * 100
            _level5_basecount = int(level5[0][0].replace("-","0"))
            _level5_baseprize = int(level5[0][1].replace(",", "").replace("-","0")) * 100
            _level6_basecount = int(level6[0][0].replace("-","0"))
            _level6_baseprize = int(level6[0][1].replace(",", "").replace("-","0")) * 100
            _level1_appendcount = int(level1[0][2].replace("-","0"))
            _level1_appendprize = int(level1[0][3].replace(",", "").replace("-","0")) * 100
            _level2_appendcount = int(level2[0][2].replace("-","0"))
            _level2_appendprize = int(level2[0][3].replace(",", "").replace("-","0")) * 100
            _level3_appendcount = int(level3[0][2].replace("-","0"))
            _level3_appendprize = int(level3[0][3].replace(",", "").replace("-","0")) * 100
            _level4_appendcount = int(level4[0][2].replace("-","0"))
            _level4_appendprize = int(level4[0][3].replace(",", "").replace("-","0")) * 100
            _level5_appendcount = int(level5[0][2].replace("-","0"))
            _level5_appendprize = int(level5[0][3].replace(",", "").replace("-","0")) * 100
         
        except Exception, e:
            _sellAmount = 0
            _retainAmount = 0
            _level1_basecount = 0
            _level1_baseprize = 0
            _level2_basecount = 0
            _level2_baseprize = 0
            _level3_basecount = 0
            _level3_baseprize = 0
            _level4_basecount = 0
            _level4_baseprize = 200*100
            _level5_basecount = 0
            _level5_baseprize = 10*100
            _level6_basecount = 0
            _level6_baseprize = 5*100
            _level1_appendcount = 0
            _level1_appendprize = 0
            _level2_appendcount = 0
            _level2_appendprize = 0
            _level3_appendcount = 0
            _level3_appendprize = 0
            _level4_appendcount = 0
            _level4_appendprize = 100*100
            _level5_appendcount = 0
            _level5_appendprize = 5*100

        lot_json = dict()
        lot_json['officialRetainAmount'] = _retainAmount
        lot_json['officialSellAmount'] = _sellAmount
        lot_json['officialPrizeList'] = [dict() for x in range(11)] 

        lot_json['officialPrizeList'][0]['level'] = 1
        lot_json['officialPrizeList'][0]['count'] = _level1_basecount
        lot_json['officialPrizeList'][0]['prize'] = _level1_baseprize
        lot_json['officialPrizeList'][2]['level'] = 3
        lot_json['officialPrizeList'][2]['count'] = _level2_basecount
        lot_json['officialPrizeList'][2]['prize'] = _level2_baseprize
        lot_json['officialPrizeList'][4]['level'] = 5
        lot_json['officialPrizeList'][4]['count'] = _level3_basecount
        lot_json['officialPrizeList'][4]['prize'] = _level3_baseprize
        lot_json['officialPrizeList'][6]['level'] = 7
        lot_json['officialPrizeList'][6]['count'] = _level4_basecount
        lot_json['officialPrizeList'][6]['prize'] = _level4_baseprize
        lot_json['officialPrizeList'][8]['level'] = 9
        lot_json['officialPrizeList'][8]['count'] = _level5_basecount
        lot_json['officialPrizeList'][8]['prize'] = _level5_baseprize
        lot_json['officialPrizeList'][10]['level'] = 11
        lot_json['officialPrizeList'][10]['count'] = _level6_basecount
        lot_json['officialPrizeList'][10]['prize'] = _level6_baseprize
        lot_json['officialPrizeList'][1]['level'] = 2
        lot_json['officialPrizeList'][1]['count'] = _level1_appendcount
        lot_json['officialPrizeList'][1]['prize'] = _level1_appendprize
        lot_json['officialPrizeList'][3]['level'] = 4
        lot_json['officialPrizeList'][3]['count'] = _level2_appendcount
        lot_json['officialPrizeList'][3]['prize'] = _level2_appendprize
        lot_json['officialPrizeList'][5]['level'] = 6
        lot_json['officialPrizeList'][5]['count'] = _level3_appendcount
        lot_json['officialPrizeList'][5]['prize'] = _level3_appendprize
        lot_json['officialPrizeList'][7]['level'] = 8
        lot_json['officialPrizeList'][7]['count'] = _level4_appendcount
        lot_json['officialPrizeList'][7]['prize'] = _level4_appendprize
        lot_json['officialPrizeList'][9]['level'] = 10
        lot_json['officialPrizeList'][9]['count'] = _level5_appendcount
        lot_json['officialPrizeList'][9]['prize'] = _level5_appendprize
        
        print  json.dumps(lot_json)
        ret = dict()
        ret['ext_info'] = lot_json
        ret['lot_id'] = lotType
        ret['issue_no'] = issueNo
        ret['draw_result'] = _result
        ret['retain_amount'] = _retainAmount

        return ret
    except Exception, e:
        printExe("some error occurred!")
        return(-1)   

###### QXC ####
def SnatchQXCDataFrom500(lotType, lotNo, resultOnly = False):
    lot_no = lotNo[2:]
  
    WURLFARMAT = 'http://kaijiang.500.com/shtml/%s/%s.shtml?ts=' + str(time())
    
    RE_RESULT_ORANGE  = re.compile(r'<li class="ball_orange">(\d+)</li>', re.I)
    RE_DRAW_DAY    = re.compile(r'开奖日期：(?P<Y>\d+)年(?P<M>\d+)月(?P<D>\d+)', re.I)
    RE_SELL_AMOUNT = re.compile(r'本期销量：[^>]*>([\d,]*)元', re.I)
    RE_RETAIN_AMOUNT = re.compile(r'奖池滚存：[\s\S]*>([\d,]*)元', re.I)
    RE_ISSUE_NO = re.compile(r'七星彩 第[\s\S]*>(\d+)</strong></font>[\s\S]*期', re.I)
    RE_LEVEL_1 = re.compile(r'一等奖</td>[^0-9/]*(?P<count>\d+)</td>[^0-9/]*(?P<prize>[\d,]*)</td>', re.I)
    RE_LEVEL_2 = re.compile(r'二等奖</td>[^0-9/]*(?P<count>\d+)</td>[^0-9/]*(?P<prize>[\d,]*)</td>', re.I)
    RE_LEVEL_3 = re.compile(r'三等奖</td>[^0-9/]*(?P<count>\d+)</td>[^0-9/]*(?P<prize>[\d,]*)</td>', re.I)
    RE_LEVEL_4 = re.compile(r'四等奖</td>[^0-9/]*(?P<count>\d+)</td>[^0-9/]*(?P<prize>[\d,]*)</td>', re.I)
    RE_LEVEL_5 = re.compile(r'五等奖</td>[^0-9/]*(?P<count>\d+)</td>[^0-9/]*(?P<prize>[\d,]*)</td>', re.I)
    RE_LEVEL_6 = re.compile(r'六等奖</td>[^0-9/]*(?P<count>\d+)</td>[^0-9/]*(?P<prize>[\d,]*)</td>', re.I)
    catchUrl = WURLFARMAT % (lotType, lot_no)
    print "catchUrl :" + catchUrl
    
    try:
        f = urllib.urlopen(catchUrl)
        html = f.read()
        print str([item for item in RE_RESULT_ORANGE.findall(html)])
        print str([item for item in RE_DRAW_DAY.findall(html)])
        print str([item for item in RE_SELL_AMOUNT.findall(html)])
        print str([item for item in RE_RETAIN_AMOUNT.findall(html)])
        print str([item for item in RE_ISSUE_NO.findall(html)])
        print str([item for item in RE_LEVEL_1.findall(html)])
        print str([item for item in RE_LEVEL_2.findall(html)])
        print str([item for item in RE_LEVEL_3.findall(html)])
        print str([item for item in RE_LEVEL_4.findall(html)])
        print str([item for item in RE_LEVEL_5.findall(html)])
        print str([item for item in RE_LEVEL_6.findall(html)])
        # print str([item for item in RE_LEVEL_7.findall(html)])
        orangeBalls = [item for item in RE_RESULT_ORANGE.findall(html)]
        
        _result = ','.join(orangeBalls)

        print "draw result: ", _result

        if len(orangeBalls) != 7:
            print "regular error!"
            return (-1)
            
        for orangeB in orangeBalls:
            if int(orangeB) < 0 or int(orangeB) > 10:
                print "error orange ball: " , orangeB
                return -1     

        if (resultOnly == True):
            ret = dict()
            ret['draw_result'] = _result
            print "Snatch for result only, succ!"
            return ret
        drawDays = [item for item in RE_DRAW_DAY.findall(html)]
        #print "drawDays : " + str(drawDays)
        sellAmount = [item for item in RE_SELL_AMOUNT.findall(html)]
        print "sellAmount : " + str(sellAmount)
        retainAmount = [item for item in RE_RETAIN_AMOUNT.findall(html)]
        print "retainAmount : " + str(retainAmount)
        issueNo = [item for item in RE_ISSUE_NO.findall(html)]
        #print "issueNo : " + str(issueNo)
        level1 = [item for item in RE_LEVEL_1.findall(html)]
        level2 = [item for item in RE_LEVEL_2.findall(html)]
        level3 = [item for item in RE_LEVEL_3.findall(html)]
        level4 = [item for item in RE_LEVEL_4.findall(html)]
        level5 = [item for item in RE_LEVEL_5.findall(html)]
        level6 = [item for item in RE_LEVEL_6.findall(html)]

        try:
            _sellAmount = int(sellAmount[0].replace(",", "").replace("-","0")) * 100
            print "sellAmount : " + str(_sellAmount)
            _retainAmount = int(retainAmount[0].replace(",", "").replace("-","0")) * 100
            print "retainAmount : " + str(_retainAmount)
            _level1_count = int(level1[0][0].replace("-","0"))
            _level1_prize = int(level1[0][1].replace(",", "").replace("-","0")) * 100
            _level2_count = int(level2[0][0].replace("-","0"))
            _level2_prize = int(level2[0][1].replace(",", "").replace("-","0")) * 100
            _level3_count = int(level3[0][0].replace("-","0"))
            _level3_prize = int(level3[0][1].replace(",", "").replace("-","0")) * 100
            _level4_count = int(level4[0][0].replace("-","0"))
            _level4_prize = int(level4[0][1].replace(",", "").replace("-","0")) * 100
            _level5_count = int(level5[0][0].replace("-","0"))
            _level5_prize = int(level5[0][1].replace(",", "").replace("-","0")) * 100
            _level6_count = int(level6[0][0].replace("-","0"))
            _level6_prize = int(level6[0][1].replace(",", "").replace("-","0")) * 100
         
        except Exception, e:
            _sellAmount = 0
            _retainAmount = 0
            _level1_count = 0
            _level1_prize = 0
            _level2_count = 0
            _level2_prize = 0
            _level3_count = 0
            _level3_prize = 1800 * 100
            _level4_count = 0
            _level4_prize = 300 * 100
            _level5_count = 0
            _level5_prize = 20 * 100
            _level6_count = 0
            _level6_prize = 5 * 100

        lot_json = dict()
        lot_json['officialRetainAmount'] = _retainAmount
        lot_json['officialSellAmount'] = _sellAmount
        lot_json['officialPrizeList'] = [dict() for x in range(6)] 
        lot_json['officialPrizeList'][0]['level'] = 1
        lot_json['officialPrizeList'][0]['count'] = _level1_count
        lot_json['officialPrizeList'][0]['prize'] = _level1_prize
        lot_json['officialPrizeList'][1]['level'] = 2
        lot_json['officialPrizeList'][1]['count'] = _level2_count
        lot_json['officialPrizeList'][1]['prize'] = _level2_prize
        lot_json['officialPrizeList'][2]['level'] = 3
        lot_json['officialPrizeList'][2]['count'] = _level3_count
        lot_json['officialPrizeList'][2]['prize'] = _level3_prize
        lot_json['officialPrizeList'][3]['level'] = 4
        lot_json['officialPrizeList'][3]['count'] = _level4_count
        lot_json['officialPrizeList'][3]['prize'] = _level4_prize
        lot_json['officialPrizeList'][4]['level'] = 5
        lot_json['officialPrizeList'][4]['count'] = _level5_count
        lot_json['officialPrizeList'][4]['prize'] = _level5_prize
        lot_json['officialPrizeList'][5]['level'] = 6
        lot_json['officialPrizeList'][5]['count'] = _level6_count
        lot_json['officialPrizeList'][5]['prize'] = _level6_prize
        
        print  json.dumps(lot_json)
        ret = dict()
        ret['ext_info'] = lot_json
        ret['lot_id'] = lotType
        ret['issue_no'] = lotNo
        ret['draw_result'] = _result
        ret['retain_amount'] = _retainAmount

        return ret
    except Exception, e:
        printExe("some error occurred!")
        return(-1)               

###### PLS ####
def SnatchPLSDataFrom500(lotType, lotNo, resultOnly = False):
    lot_no = lotNo[2:]
  
    WURLFARMAT = 'http://kaijiang.500.com/shtml/%s/%s.shtml?ts=' + str(time())
    
    RE_RESULT_ORANGE  = re.compile(r'<li class="ball_orange">(\d+)</li>', re.I)
    RE_DRAW_DAY    = re.compile(r'开奖日期：(?P<Y>\d+)年(?P<M>\d+)月(?P<D>\d+)', re.I)
    RE_SELL_AMOUNT = re.compile(r'本期销量：[^>]*>([\d,]*)元', re.I)
    RE_ISSUE_NO = re.compile(r'排列三 第[\s\S]*>(\d+)</strong></font>[\s\S]*期', re.I)
    RE_LEVEL_1 = re.compile(r'排列三直选</td>[^0-9/]*(?P<count>\d+)</td>[^0-9/]*(?P<prize>[\d,]*)</td>', re.I)
    RE_LEVEL_2 = re.compile(r'排列三组六</td>[^0-9/]*(?P<count>\d+)</td>[^0-9/]*(?P<prize>[\d,]*)</td>', re.I)
    RE_LEVEL_3 = re.compile(r'排列三组三</td>[^0-9/]*(?P<count>\d+)</td>[^0-9/]*(?P<prize>[\d,]*)</td>', re.I)
    catchUrl = WURLFARMAT % (lotType, lot_no)
    print "catchUrl :" + catchUrl
    
    try:
        f = urllib.urlopen(catchUrl)
        html = f.read()
        print str([item for item in RE_RESULT_ORANGE.findall(html)])
        print str([item for item in RE_DRAW_DAY.findall(html)])
        print str([item for item in RE_SELL_AMOUNT.findall(html)])
        print str([item for item in RE_ISSUE_NO.findall(html)])
        print str([item for item in RE_LEVEL_1.findall(html)])
        print str([item for item in RE_LEVEL_2.findall(html)])
        print str([item for item in RE_LEVEL_3.findall(html)])

        orangeBalls = [item for item in RE_RESULT_ORANGE.findall(html)]
        
        _result = ','.join(orangeBalls)

        print "draw result: ", _result

        if len(orangeBalls) != 3:
            print "regular error!"
            return (-1)
            
        for orangeB in orangeBalls:
            if int(orangeB) < 0 or int(orangeB) > 10:
                print "error orange ball: " , orangeB
                return -1     

        if (resultOnly == True):
            ret = dict()
            ret['draw_result'] = _result
            print "Snatch for result only, succ!"
            return ret
        drawDays = [item for item in RE_DRAW_DAY.findall(html)]
        #print "drawDays : " + str(drawDays)
        sellAmount = [item for item in RE_SELL_AMOUNT.findall(html)]
        print "sellAmount : " + str(sellAmount)
        issueNo = [item for item in RE_ISSUE_NO.findall(html)]
        #print "issueNo : " + str(issueNo)
        level1 = [item for item in RE_LEVEL_1.findall(html)]
        level2 = [item for item in RE_LEVEL_2.findall(html)]
        level3 = [item for item in RE_LEVEL_3.findall(html)]
        if len(level2) == 0:
            level2 = [("0", "17300")]
        if len(level3) == 0:
            level3 = [("0", "34600")]

        try:
            _sellAmount = int(sellAmount[0].replace(",", "").replace("-","0")) * 100
            print "sellAmount : " + str(_sellAmount)
            _level1_count = int(level1[0][0].replace("-","0"))
            _level1_prize = int(level1[0][1].replace(",", "").replace("-","0")) * 100
            _level2_count = int(level2[0][0].replace("-","0"))
            _level2_prize = int(level2[0][1].replace(",", "").replace("-","0")) * 100
            _level3_count = int(level3[0][0].replace("-","0"))
            _level3_prize = int(level3[0][1].replace(",", "").replace("-","0")) * 100
            
        except Exception, e:
            _sellAmount = 0
            _level1_count = 0
            _level1_prize = 1040 * 100
            _level2_count = 0
            _level2_prize = 173 * 100
            _level3_count = 0
            _level3_prize = 346 * 100
           
        lot_json = dict()
        # lot_json['officialRetainAmount'] = _retainAmount
        lot_json['officialSellAmount'] = _sellAmount
        lot_json['officialPrizeList'] = [dict() for x in range(3)] 
        lot_json['officialPrizeList'][0]['level'] = 1
        lot_json['officialPrizeList'][0]['count'] = _level1_count
        lot_json['officialPrizeList'][0]['prize'] = _level1_prize
        lot_json['officialPrizeList'][1]['level'] = 2
        lot_json['officialPrizeList'][1]['count'] = _level2_count
        lot_json['officialPrizeList'][1]['prize'] = _level2_prize
        lot_json['officialPrizeList'][2]['level'] = 3
        lot_json['officialPrizeList'][2]['count'] = _level3_count
        lot_json['officialPrizeList'][2]['prize'] = _level3_prize
        
        
        print  json.dumps(lot_json)
        ret = dict()
        ret['ext_info'] = lot_json
        ret['lot_id'] = lotType
        ret['issue_no'] = lotNo
        ret['draw_result'] = _result

        return ret
    except Exception, e:
        printExe("pls some error occurred!")
        return(-1)     

###### PLW ####
def SnatchPLWDataFrom500(lotType, lotNo, resultOnly = False):
    lot_no = lotNo[2:]
  
    WURLFARMAT = 'http://kaijiang.500.com/shtml/%s/%s.shtml?ts=' + str(time())
    
    RE_RESULT_ORANGE  = re.compile(r'<li class="ball_orange">(\d+)</li>', re.I)
    RE_DRAW_DAY    = re.compile(r'开奖日期：(?P<Y>\d+)年(?P<M>\d+)月(?P<D>\d+)', re.I)
    RE_SELL_AMOUNT = re.compile(r'本期销量：[^>]*>([\d,]*)元', re.I)
    RE_ISSUE_NO = re.compile(r'排列五 第[\s\S]*>(\d+)</strong></font>[\s\S]*期', re.I)
    RE_LEVEL_1 = re.compile(r'排列五直选</td>[^0-9/]*(?P<count>\d+)</td>[^0-9/]*(?P<prize>[\d,]*)</td>', re.I)
    catchUrl = WURLFARMAT % (lotType, lot_no)
    print "catchUrl :" + catchUrl
    
    try:
        f = urllib.urlopen(catchUrl)
        html = f.read()
        print str([item for item in RE_RESULT_ORANGE.findall(html)])
        print str([item for item in RE_DRAW_DAY.findall(html)])
        print str([item for item in RE_SELL_AMOUNT.findall(html)])
        print str([item for item in RE_ISSUE_NO.findall(html)])
        print str([item for item in RE_LEVEL_1.findall(html)])
       
        orangeBalls = [item for item in RE_RESULT_ORANGE.findall(html)]
        
        _result = ','.join(orangeBalls)

        print "draw result: ", _result

        if len(orangeBalls) != 5:
            print "regular error!"
            return (-1)
            
        for orangeB in orangeBalls:
            if int(orangeB) < 0 or int(orangeB) > 10:
                print "error orange ball: " , orangeB
                return -1     

        if (resultOnly == True):
            ret = dict()
            ret['draw_result'] = _result
            print "Snatch for result only, succ!"
            return ret
        drawDays = [item for item in RE_DRAW_DAY.findall(html)]
        #print "drawDays : " + str(drawDays)
        sellAmount = [item for item in RE_SELL_AMOUNT.findall(html)]
        print "sellAmount : " + str(sellAmount)
        issueNo = [item for item in RE_ISSUE_NO.findall(html)]
        #print "issueNo : " + str(issueNo)
        level1 = [item for item in RE_LEVEL_1.findall(html)]
  

        try:
            _sellAmount = int(sellAmount[0].replace(",", "").replace("-","0")) * 100
            print "sellAmount : " + str(_sellAmount)
            _level1_count = int(level1[0][0].replace("-","0"))
            _level1_prize = int(level1[0][1].replace(",", "").replace("-","0")) * 100
            
        except Exception, e:
            _sellAmount = 0
            # _retainAmount = 0
            _level1_count = 0
            _level1_prize = 100000 * 100
           
        lot_json = dict()
        # lot_json['officialRetainAmount'] = _retainAmount
        lot_json['officialSellAmount'] = _sellAmount
        lot_json['officialPrizeList'] = [dict() for x in range(2)] 
        lot_json['officialPrizeList'][0]['level'] = 1
        lot_json['officialPrizeList'][0]['count'] = _level1_count
        lot_json['officialPrizeList'][0]['prize'] = _level1_prize
        
        
        print  json.dumps(lot_json)
        ret = dict()
        ret['ext_info'] = lot_json
        ret['lot_id'] = lotType
        ret['issue_no'] = lotNo
        ret['draw_result'] = _result

        return ret
    except Exception, e:
        printExe("plw some error occurred!")
        return(-1)            


# 返回数组：[抓取次数, sleep时间戳]        
def GetSnatchCnt(lotId):
    #普通彩30秒抓一次，一小时告警
    aNormalCntInfo = [120,30]    
    #快频彩10秒抓1次，5分钟告警
    aKPCCntInfo = [30,10]
    if(lotId == 'SSQ'):
        return aNormalCntInfo
    elif(lotId == 'QLC'):
        return aNormalCntInfo
    elif(lotId == 'DLT'):
        return aNormalCntInfo
    elif(lotId == 'QXC'):
        return aNormalCntInfo
    elif(lotId == 'PLS'):
        return aNormalCntInfo
    elif(lotId == 'PLW'):
        return aNormalCntInfo
    else:
        return [];    


def InsertDLTDrawResult(lotId, issueNo, drawRet,srcNo):   
    print "InsertDLTDrawResult begin!"
    dbInfo = dict()
    dbInfo = InitDB()    
    if(dbInfo.has_key("error")):
        return
    try:
        lot_conn=MySQLdb.connect(host=dbInfo["host"],user=dbInfo["user"],passwd=dbInfo["pwd"],db=dbInfo["db"],port=int(dbInfo["port"]),charset='gbk')
        lot_cur=lot_conn.cursor()
        
        draw_info = ""
        if(drawRet.has_key("ext_info")):
            draw_info = json.dumps(drawRet["ext_info"])
        
        sql = "INSERT INTO t_lottery_draw_result(lotteryId,issueNo,drawResult,createTime) "
        sql = sql + "VALUES('"+lotId+"','"+issueNo+"','"+drawRet['draw_result']+"',now());"
        print sql
        n = lot_cur.execute(sql)   
        lot_conn.commit()
        

        draw_info = json.loads(draw_info)
        # drawAmount = draw_info['officialRetainAmount']
        # print "drawAmount -->", drawAmount
        drawPrizeList = draw_info['officialPrizeList']
        for item in drawPrizeList:
            print "item --> %s" % item
            levelSql = "INSERT INTO t_lottery_draw_level(lotteryId,issueNo,level,levelName,money,totalCount,createTime) "
            levelSql = levelSql + "VALUES('"+lotId+"','"+issueNo+"',"+ str(item['level']) +",'"
            if item['level'] == 1: 
               levelSql = levelSql + "一等奖"
            elif item['level'] == 2:
               levelSql = levelSql + "一等奖追加"
            elif item['level'] == 3: 
               levelSql = levelSql + "二等奖"
            elif item['level'] == 4:
               levelSql = levelSql + "二等奖追加"
            elif item['level'] == 5:
               levelSql = levelSql + "三等奖"
            elif item['level'] == 6: 
               levelSql = levelSql + "三等奖追加"
            elif item['level'] == 7:
               levelSql = levelSql + "四等奖"
            elif item['level'] == 8:
               levelSql = levelSql + "四等奖追加"
            elif item['level'] == 9: 
               levelSql = levelSql + "五等奖"
            elif item['level'] == 10:
               levelSql = levelSql + "五等奖追加"
            else:
               levelSql = levelSql + "六等奖"
            levelSql = levelSql + "'," + str(item['prize']) + "," + str(item['count']) + ", now());"
            print "levelSql --> %s" % levelSql
            lot_cur.execute('SET NAMES gbk')
            lot_cur.execute(levelSql)   
            lot_conn.commit()
        
        lot_cur.close()
        lot_conn.close()
        print "InsertDLTDrawResult SUCC for [%s %s %s] at %s" % (lotId,issueNo,drawRet['draw_result'],strftime("%Y-%m-%d %H:%M:%S",localtime(int(time()))))
        return 0
    except Exception, e:
        printExe("InsertDLTDrawResult FAIL for [%s %s %s]" % (lotId,issueNo,drawRet['draw_result']))
        return(-1)

def InsertQXCDrawResult(lotId, issueNo, drawRet,srcNo):   
    print "InsertDLTDrawResult begin!"
    dbInfo = dict()
    dbInfo = InitDB()    
    if(dbInfo.has_key("error")):
        return
    try:
        lot_conn=MySQLdb.connect(host=dbInfo["host"],user=dbInfo["user"],passwd=dbInfo["pwd"],db=dbInfo["db"],port=int(dbInfo["port"]),charset='gbk')
        lot_cur=lot_conn.cursor()
        
        draw_info = ""
        if(drawRet.has_key("ext_info")):
            draw_info = json.dumps(drawRet["ext_info"])
        
        sql = "INSERT INTO t_lottery_draw_result(lotteryId,issueNo,drawResult,createTime) "
        sql = sql + "VALUES('"+lotId+"','"+issueNo+"','"+drawRet['draw_result']+"',now());"
        print sql
        n = lot_cur.execute(sql)   
        lot_conn.commit()
        

        draw_info = json.loads(draw_info)
        # drawAmount = draw_info['officialRetainAmount']
        # print "drawAmount -->", drawAmount
        drawPrizeList = draw_info['officialPrizeList']
        for item in drawPrizeList:
            print "item --> %s" % item
            levelSql = "INSERT INTO t_lottery_draw_level(lotteryId,issueNo,level,levelName,money,totalCount,createTime) "
            levelSql = levelSql + "VALUES('"+lotId+"','"+issueNo+"',"+ str(item['level']) +",'"
            if item['level'] == 1: 
               levelSql = levelSql + "一等奖"
            elif item['level'] == 2: 
               levelSql = levelSql + "二等奖"
            elif item['level'] == 3:
               levelSql = levelSql + "三等奖"
            elif item['level'] == 4:
               levelSql = levelSql + "四等奖"
            elif item['level'] == 5: 
               levelSql = levelSql + "五等奖"
            else:
               levelSql = levelSql + "六等奖"
            levelSql = levelSql + "'," + str(item['prize']) + "," + str(item['count']) + ", now());"
            print "levelSql --> %s" % levelSql
            lot_cur.execute('SET NAMES gbk')
            lot_cur.execute(levelSql)   
            lot_conn.commit()
        
        lot_cur.close()
        lot_conn.close()
        print "InsertDLTDrawResult SUCC for [%s %s %s] at %s" % (lotId,issueNo,drawRet['draw_result'],strftime("%Y-%m-%d %H:%M:%S",localtime(int(time()))))
        return 0
    except Exception, e:
        printExe("InsertDLTDrawResult FAIL for [%s %s %s]" % (lotId,issueNo,drawRet['draw_result']))
        return(-1)

def InsertPLSDrawResult(lotId, issueNo, drawRet,srcNo):   
    print "InsertPLSDrawResult begin!"
    dbInfo = dict()
    dbInfo = InitDB()    
    if(dbInfo.has_key("error")):
        return
    try:
        lot_conn=MySQLdb.connect(host=dbInfo["host"],user=dbInfo["user"],passwd=dbInfo["pwd"],db=dbInfo["db"],port=int(dbInfo["port"]),charset='gbk')
        lot_cur=lot_conn.cursor()
        
        draw_info = ""
        if(drawRet.has_key("ext_info")):
            draw_info = json.dumps(drawRet["ext_info"])
        
        sql = "INSERT INTO t_lottery_draw_result(lotteryId,issueNo,drawResult,createTime) "
        sql = sql + "VALUES('"+lotId+"','"+issueNo+"','"+drawRet['draw_result']+"',now());"
        print sql
        n = lot_cur.execute(sql)   
        lot_conn.commit()
        

        draw_info = json.loads(draw_info)
        # drawAmount = draw_info['officialRetainAmount']
        # print "drawAmount -->", drawAmount
        drawPrizeList = draw_info['officialPrizeList']
        for item in drawPrizeList:
            print "item --> %s" % item
            levelSql = "INSERT INTO t_lottery_draw_level(lotteryId,issueNo,level,levelName,money,totalCount,createTime) "
            levelSql = levelSql + "VALUES('"+lotId+"','"+issueNo+"',"+ str(item['level']) +",'"
            if item['level'] == 1: 
               levelSql = levelSql + "排列三直选"
            elif item['level'] == 2: 
               levelSql = levelSql + "排列三组六"
            elif item['level'] == 3: 
               levelSql = levelSql + "排列三组三"
            else:
               print "PLS prize level error"
               return(-1)
            levelSql = levelSql + "'," + str(item['prize']) + "," + str(item['count']) + ", now());"
            print "levelSql --> %s" % levelSql
            lot_cur.execute('SET NAMES gbk')
            lot_cur.execute(levelSql)   
            lot_conn.commit()
        
        lot_cur.close()
        lot_conn.close()
        print "InsertPLSDrawResult SUCC for [%s %s %s] at %s" % (lotId,issueNo,drawRet['draw_result'],strftime("%Y-%m-%d %H:%M:%S",localtime(int(time()))))
        return 0
    except Exception, e:
        printExe("InsertPLSDrawResult FAIL for [%s %s %s]" % (lotId,issueNo,drawRet['draw_result']))
        return(-1)

def InsertPLWDrawResult(lotId, issueNo, drawRet,srcNo):   
    print "InsertPLWDrawResult begin!"
    dbInfo = dict()
    dbInfo = InitDB()    
    if(dbInfo.has_key("error")):
        return
    try:
        lot_conn=MySQLdb.connect(host=dbInfo["host"],user=dbInfo["user"],passwd=dbInfo["pwd"],db=dbInfo["db"],port=int(dbInfo["port"]),charset='gbk')
        lot_cur=lot_conn.cursor()
        
        draw_info = ""
        if(drawRet.has_key("ext_info")):
            draw_info = json.dumps(drawRet["ext_info"])
        
        sql = "INSERT INTO t_lottery_draw_result(lotteryId,issueNo,drawResult,createTime) "
        sql = sql + "VALUES('"+lotId+"','"+issueNo+"','"+drawRet['draw_result']+"',now());"
        print sql
        n = lot_cur.execute(sql)   
        lot_conn.commit()
        

        draw_info = json.loads(draw_info)
        # drawAmount = draw_info['officialRetainAmount']
        # print "drawAmount -->", drawAmount
        drawPrizeList = draw_info['officialPrizeList']
        for item in drawPrizeList:
            print "item --> %s" % item
            levelSql = "INSERT INTO t_lottery_draw_level(lotteryId,issueNo,level,levelName,money,totalCount,createTime) "
            levelSql = levelSql + "VALUES('"+lotId+"','"+issueNo+"',"+ str(item['level']) +",'"
            if item['level'] == 1: 
               levelSql = levelSql + "排列五直选"
            else:
               print "PLW prize level error"
               return(-1)
            levelSql = levelSql + "'," + str(item['prize']) + "," + str(item['count']) + ", now());"
            print "levelSql --> %s" % levelSql
            lot_cur.execute('SET NAMES gbk')
            lot_cur.execute(levelSql)   
            lot_conn.commit()
        
        lot_cur.close()
        lot_conn.close()
        print "InsertPLWDrawResult SUCC for [%s %s %s] at %s" % (lotId,issueNo,drawRet['draw_result'],strftime("%Y-%m-%d %H:%M:%S",localtime(int(time()))))
        return 0
    except Exception, e:
        printExe("InsertPLWDrawResult FAIL for [%s %s %s]" % (lotId,issueNo,drawRet['draw_result']))
        return(-1)


def InsertDrawResult(lotId, issueNo, drawRet,srcNo):
    if lotId == 'DLT':
        InsertDLTDrawResult(lotId, issueNo, drawRet,srcNo)
    elif lotId == 'QXC':
        InsertQXCDrawResult(lotId, issueNo, drawRet,srcNo)
    elif lotId == 'PLS':
        InsertPLSDrawResult(lotId, issueNo, drawRet,srcNo)
    elif lotId == 'PLW':
        InsertPLWDrawResult(lotId, issueNo, drawRet,srcNo)

    return 0

#慢频彩抓奖：SSQ\DLT\SD\QXC\QLC\FC15X5    
def SnatchMpcData(lotId, issueNo, resultOnly):
    #抓去数据
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
        if(lotId == 'SSQ'):
            ret = SnatchSSQDataFrom500('ssq', issueNo, resultOnly)
        elif(lotId == 'QLC'):
            ret = SnatchQLCDataFrom500('qlc', issueNo, resultOnly)
        elif(lotId == 'DLT'):
            ret = SnatchDLTDataFrom500('dlt', issueNo, resultOnly)
        elif(lotId == 'QXC'):
            ret = SnatchQXCDataFrom500('qxc', issueNo, resultOnly)
        elif(lotId == 'PLS'):
            ret = SnatchPLSDataFrom500('pls', issueNo, resultOnly)
        elif(lotId == 'PLW'):
            ret = SnatchPLWDataFrom500('plw', issueNo, resultOnly)
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
    InsertDrawResult(lotId, issueNo, ret, '500')

    

#取当前待开奖期期号        
# def CountIssueNo(lotId):
#     '''将抓去结果写到DB, 没有考虑期号不存在的情况'''
#     dbInfo = dict()
#     dbInfo = InitDB()
#     issueNo = '';    
#     if(dbInfo.has_key("error")):
#         return(-1)
#     try:
#         print dbInfo["host"]
#         lot_conn=MySQLdb.connect(host=dbInfo["host"],user=dbInfo["user"],passwd=dbInfo["pwd"],db=dbInfo["db"],port=int(dbInfo["port"]))
#         lot_cur=lot_conn.cursor()
#         sql = 'select fissue_no from t_lottery_issue where flottery_id="%s" and fissue_state=7' % (lotId)
#         lot_cur.execute(sql)
#         rows = lot_cur.fetchall()
#         if len(rows) > 0:
#             issueNo = str(rows[0][0]).strip()
#             print "issue_no:%s" % (issueNo)
#         else:
#       #获取只抓取到固定奖的期号（0已抓取到固定奖，1固定奖已更新到期号表，2已抓取到浮动奖，3所有奖级都更新到期号表）
#       sql = 'select fissue_no from t_lottery_draw_result where flottery_id="%s" and Fstate=1 and Fstatus in (0,1) ' % (lotId)
#             lot_cur.execute(sql)
#             rows = lot_cur.fetchall()
#             if len(rows) > 0:
#           issueNo = str(rows[0][0]).strip()
#                 print "issue_no:%s" % (issueNo)
#       else:
#           issueNo = -1
#                 print "error in find next issue_no,sql:",sql
#         lot_conn.commit()
#         lot_cur.close()
#         lot_conn.close()
#         print "CountIssueNo SUCC for [%s %s] at %s" % (lotId,issueNo,strftime("%Y-%m-%d %H:%M:%S",localtime(int(time()))))
#   return issueNo
#     except Exception, e:
#         printExe("UpdateIssueTable FAIL for [%s %s]" % (lotId,issueNo))
#         return(-1) 

#供外部调用
def IssueDrawSnatch(lotId, issueNo, resultOnly):
    print '='*9, strftime("%Y-%m-%d %H:%M:%S",localtime(int(time()))), '='*9
    if lotId != "":
        SnatchMpcData(lotId, issueNo, resultOnly)
    else:
        print "lottery id is invalid, lotteryId[%s]." % (lotId)
        sys.exit(-1)
    #if issueNo == "":        
        # issueNo = CountIssueNo(lotId)
    # if issueNo == -1 or len(issueNo) == 0:
    #     print "issue no is null, no need to snatch lotteryId[%s] issue." % (lotId)
    #     sys.exit(-1)
        
    # if("SSQ" == lotId):
    #     if(len(issueNo) != 7):
    #         print "query issueNo Fail!"
    #         sys.exit(-1)
    #     print "Snatch [SSQ] for NO." + issueNo
    #     SnatchMpcData(lotId, issueNo, resultOnly)
    # elif("QLC" == lotId):
    #     if(len(issueNo) != 7):
    #         print "query issueNo Fail!"
    #         sys.exit(-1)
    #     print "Snatch [QLC] for NO." + issueNo
    #     SnatchMpcData(lotId, issueNo, resultOnly)
    # elif("DLT" == lotId):
    #     if(len(issueNo) != 7):
    #         print "query issueNo Fail!"
    #         sys.exit(-1)
    #     print "Snatch [DLT] for NO." + issueNo
    #     SnatchMpcData(lotId, issueNo, resultOnly)
    # elif("QXC" == lotId):
    #     if(len(issueNo) != 7):
    #         print "query issueNo Fail!"
    #         sys.exit(-1)
    #     print "Snatch [QXC] for NO." + issueNo
    #     SnatchMpcData(lotId, issueNo, resultOnly)
    # elif("PLS" == lotId):
    #     if(len(issueNo) != 7):
    #         print "query issueNo Fail!"
    #         sys.exit(-1)
    #     print "Snatch [PLS] for NO." + issueNo
    #     SnatchMpcData(lotId, issueNo, resultOnly)
    # elif("PLW" == lotId):
    #     if(len(issueNo) != 7):
    #         print "query issueNo Fail!"
    #         sys.exit(-1)
    #     print "Snatch [PLW] for NO." + issueNo
    #     SnatchMpcData(lotId, issueNo, resultOnly)
    # else:
    #     print "lottery id is invalid, lotteryId[%s]." % (lotId)
    #     sys.exit(-1)
        
    # sys.exit(0)    


if __name__ == "__main__":
    print '='*9, strftime("%Y-%m-%d %H:%M:%S",localtime(int(time()))), '='*9
    os.chdir(sys.path[0])

    # if(len(sys.argv) < 2):
    #     Help()
    
    
    resultOnly = False 
    issue_no = ""

    #IssueDrawSnatch("QXC", "2014153", False)
    
    # opts, args = getopt.getopt(sys.argv[2:], 'ri:', ['only_result', 'issue_no='])
    # for option, value in opts:
    #     if option in ['-r', '--only_result']:
    #         print "only result"
    #         resultOnly = True
    #     if option in ['-i', '--issue_no']:
    #         issue_no = value
    # print "resultOnly=" + str(resultOnly)
    #IssueDrawSnatch(sys.argv[1], issue_no, resultOnly)
    i = 1
    while i < 18: 
        tmp = str(i)
        if i < 10:
            tmp = "0" + tmp
        issue_no = "20150" + tmp
        IssueDrawSnatch("QXC", issue_no, False)
        sleep(1)
        i = i + 1


