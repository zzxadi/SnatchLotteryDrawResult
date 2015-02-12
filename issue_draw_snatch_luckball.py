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
    RE_RESULT_ORANGE = re.compile(r'<li class="ball_orange">(\d+)</li>', re.I)
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
    RE_LEVEL_7 = re.compile(r'幸运二等奖</td>[^0-9/]*(?P<count>\d+)</td>[^0-9/]*(?P<prize>[\d,]*)\(含派奖', re.I)
    catchUrl = WURLFARMAT % (lotType, lot_no)
    print "catchUrl :" + catchUrl
    
    try:
        f = urllib.urlopen(catchUrl)
        html = f.read()
        #print str([item for item in RE_RESULT_RED.findall(html)])
        #print str([item for item in RE_RESULT_BLUE.findall(html)])
        #print str([item for item in RE_RESULT_ORANGE.findall(html)])
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
	#幸运号码
        orangeBalls = [item for item in RE_RESULT_ORANGE.findall(html)]

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
        
	if(len(orangeBalls) == 1 and (int(orangeBalls[0]) < 1 or int(orangeBalls[0]) > 16)):
	    print "error orange ball:", orangeBalls[0]
	    return -1

        _result = ','.join(redBalls) + '|' + blueBalls[0]
        print "result : " + _result
	_luckyBall = ""
	if(len(orangeBalls) == 1):
	    pre_zero = "";
	    if(len(orangeBalls[0]) == 1):
                pre_zero = "0";
	    _luckyBall = pre_zero + orangeBalls[0]
	    print "luckball:" + _luckyBall


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
	level7 = [0, 0]
	if (len(orangeBalls) == 1):
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
	    _level7_count = 0
            _level7_prize = 0
	    if (len(orangeBalls) == 1):
                _level7_count = int(level7[0][0].replace("-","0"))
                _level7_prize = int(level7[0][1].replace(",", "").replace("-","0")) * 100
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
            _level7_count = 0
            _level7_prize = 0

        lot_json = dict()
        lot_json['officialRetainAmount'] = _retainAmount
        lot_json['officialSellAmount'] = _sellAmount
        lot_json['officialPrizeList'] = [dict() for x in range(6)] 
	if (len(orangeBalls) == 1):
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
	if (len(orangeBalls) == 1):
	    # 双色球幸运二等奖，对应的是第8奖级
            lot_json['officialPrizeList'][6]['level'] = 8
            lot_json['officialPrizeList'][6]['count'] = _level7_count
            lot_json['officialPrizeList'][6]['prize'] = _level7_prize
	    
        
        #print  json.dumps(lot_json)
        ret = dict()
        ret['ext_info'] = lot_json
        ret['lot_id'] = lotType
        ret['issue_no'] = lotNo
        ret['draw_result'] = _result
        ret['retain_amount'] = _retainAmount
	if(len(orangeBalls) == 1):
            ret['lucky_ball'] = _luckyBall
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
    else:
        return [];    

def InsertOrUpdateDrawResult(lotId, issueNo, drawRet,srcNo):
    flag = existsDrawResult(lotId, issueNo, srcNo)
    if flag == 1:
        UpdateDrawResult(lotId, issueNo, drawRet,srcNo)
    elif flag == 0:
        InsertDrawResult(lotId, issueNo, drawRet,srcNo)
    return 0


def existsDrawResult(lotId, issueNo, srcNo):
    dbInfo = dict()
    dbInfo = InitDB()    
    if(dbInfo.has_key("error")):
        return
    try:
        #print str(dbInfo)
        lot_conn=MySQLdb.connect(host=dbInfo["host"],user=dbInfo["user"],passwd=dbInfo["pwd"],db=dbInfo["db"],port=int(dbInfo["port"]))
	#lot_conn=MySQLdb.connect(host="203.195.182.110",user="mycqfc",passwd="mycqfc@db",db="cqfcdb",port=3306)
        lot_cur=lot_conn.cursor()
        
        #取得开奖源信息
        lot_json = dict()
        sql = "select Fdraw_info from t_lottery_draw_result where Flottery_id='"+ lotId +"' and Fissue_no='"+ issueNo +"' and Fsrc_no='" + srcNo + "'"
        #print sql
        if 0 < lot_cur.execute(sql):
	     lot_cur.close()
             lot_conn.close()
             return 1
	lot_cur.close()
        lot_conn.close()
        return 0
    except Exception, e:
        printExe("existsDrawResult FAIL for [%s %s %s]" % (lotId,issueNo,srcNo))
        return(-1)

def InsertDrawResult(lotId, issueNo, drawRet,srcNo):   
    print "InsertDrawResult begin!"
    dbInfo = dict()
    dbInfo = InitDB()    
    if(dbInfo.has_key("error")):
        return
    try:
        lot_conn=MySQLdb.connect(host=dbInfo["host"],user=dbInfo["user"],passwd=dbInfo["pwd"],db=dbInfo["db"],port=int(dbInfo["port"]))
        lot_cur=lot_conn.cursor()
        
        #取得开奖源信息
        sql = "SELECT Fsrc_no,Fstate,Fpriority from t_lottery_draw_src where Fsrc_no='"+ srcNo + "' and Flottery_id='" + lotId + "'"
        #print sql
        if(1 > lot_cur.execute(sql)):
            print "No draw src of src_no[%s] lotteryId[%s]" % (srcNo,lotId)
            lot_cur.close()
            lot_conn.close()
            return (-1)    
        srcs=lot_cur.fetchall()
        src_no = srcs[0][0]
        src_state = str(srcs[0][1])
        src_priority = str(srcs[0][2])
        
        #插入开奖结果表
        draw_info = ""
        if(drawRet.has_key("ext_info")):
            draw_info = json.dumps(drawRet["ext_info"])
        
        retain_amount = 0;
        if (drawRet.has_key('retain_amount')):
            retain_amount = drawRet['retain_amount']
	lucky_ball = ""
	if (drawRet.has_key('lucky_ball')):
	    lucky_ball = drawRet['lucky_ball']
        status = 0;#代表还未开出大奖，同时未更新到t_lottery_issue表
	if(drawRet.has_key('float_flag') and drawRet['float_flag'] == 1):
            status = 2;#代表开出大奖，同时未更新到t_lottery_issue表
        sql = "INSERT INTO t_lottery_draw_result(Flottery_id,Fissue_no,Fsrc_no,Fdraw_result,Fstate,Fpriority,Fcreate_time,Fint1,Fdraw_info,Flast_update_time,Fstatus, fchar1) "
	sql = sql +"VALUES('"+lotId+"','"+issueNo+"','"+src_no+"','"+drawRet['draw_result']+"',"+src_state+","+src_priority+",now(),"+str(retain_amount)+",'"+draw_info+"',now(),"+str(status)+",'"+str(lucky_ball)+"')"
        #print sql
        
        n = lot_cur.execute(sql)   
        lot_conn.commit()
        lot_cur.close()
        lot_conn.close()
        print "InsertDrawResult SUCC for [%s %s %s] at %s" % (lotId,issueNo,srcNo,strftime("%Y-%m-%d %H:%M:%S",localtime(int(time()))))
        return 0
    except Exception, e:
        printExe("InsertDrawResult FAIL for [%s %s %s]" % (lotId,issueNo,srcNo))
        return(-1)

    
def UpdateDrawResult(lotId, issueNo, drawRet,srcNo):
    print "UpdateDrawResult begin!"
    dbInfo = dict()
    dbInfo = InitDB()    
    if(dbInfo.has_key("error")):
        return
    try:
        lot_conn=MySQLdb.connect(host=dbInfo["host"],user=dbInfo["user"],passwd=dbInfo["pwd"],db=dbInfo["db"],port=int(dbInfo["port"]))
        lot_cur=lot_conn.cursor()
        
        #取得开奖源信息
        lot_json = dict()
        sql = "select Fdraw_info from t_lottery_draw_result where Flottery_id='"+ lotId +"' and Fissue_no='"+ issueNo +"' and Fsrc_no='" + srcNo + "'"
        #print sql
        if 0 < lot_cur.execute(sql):
            src_ext_info = lot_cur.fetchall()[0][0].strip()
            if len(src_ext_info) > 1:
                lot_json = json.loads(src_ext_info)        
        
        if(drawRet.has_key("ext_info")):
            if drawRet["ext_info"].has_key("officialRetainAmount"):
                lot_json["officialRetainAmount"] = drawRet["ext_info"]["officialRetainAmount"]    
            if drawRet["ext_info"].has_key("officialSellAmount"):
                lot_json["officialSellAmount"] = drawRet["ext_info"]["officialSellAmount"]
            if drawRet["ext_info"].has_key("officialPrizeList"):
                lot_json["officialPrizeList"] = drawRet["ext_info"]["officialPrizeList"]    
            if drawRet["ext_info"].has_key("official12SellAmount"):
                lot_json["official12SellAmount"] = drawRet["ext_info"]["official12SellAmount"] 
        
        sql = "UPDATE t_lottery_draw_result SET Fdraw_result='"+ drawRet['draw_result'] +"'"
        if (drawRet.has_key('retain_amount')):
            sql = sql + ", Fint1=" +  str(drawRet['retain_amount']) 
        if(drawRet.has_key('float_flag') and drawRet['float_flag'] == 1):
            sql = sql + ", Fstatus=2"
	if (drawRet.has_key('lucky_ball')):
	    sql = sql + ", Fchar1='" + str(drawRet['lucky_ball'])
        sql = sql + "', Fdraw_info='"+ json.dumps(lot_json) + "', Flast_update_time=now() where Flottery_id='"+ lotId +"' and Fissue_no='"+ issueNo +"' and Fsrc_no='" + srcNo + "'"
        #print sql
        
        n = lot_cur.execute(sql)    
        lot_conn.commit()
        lot_cur.close()
        lot_conn.close()
        print "UpdateDrawResult SUCC for [%s %s %s] at %s" % (lotId,issueNo,srcNo,strftime("%Y-%m-%d %H:%M:%S",localtime(int(time()))))
        return 0
    except Exception, e:
        printExe("UpdateDrawResult FAIL for [%s %s %s]" % (lotId,issueNo,srcNo))
        return(-1)   

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


def InsertDrawResult(lotId, issueNo, drawRet,srcNo):
    if lotId == 'DLT':
        InsertDLTDrawResult(lotId, issueNo, drawRet,srcNo)
    elif lotId == 'QXC':
        InsertQXCDrawResult(lotId, issueNo, drawRet,srcNo)
    elif lotId == 'PL3':
        InsertPL3DrawResult(lotId, issueNo, drawRet,srcNo)
    elif lotId == 'PL5':
        InsertPL5DrawResult(lotId, issueNo, drawRet,srcNo)

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
    InsertDrawResult(lotId, issueNo, ret, '500')


    

#取当前待开奖期期号        
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
        sql = 'select fissue_no from t_lottery_issue where flottery_id="%s" and fissue_state=7' % (lotId)
        lot_cur.execute(sql)
        rows = lot_cur.fetchall()
        if len(rows) > 0:
            issueNo = str(rows[0][0]).strip()
            print "issue_no:%s" % (issueNo)
        else:
	    #获取只抓取到固定奖的期号（0已抓取到固定奖，1固定奖已更新到期号表，2已抓取到浮动奖，3所有奖级都更新到期号表）
	    sql = 'select fissue_no from t_lottery_draw_result where flottery_id="%s" and Fstate=1 and Fstatus in (0,1) ' % (lotId)
            lot_cur.execute(sql)
            rows = lot_cur.fetchall()
            if len(rows) > 0:
	        issueNo = str(rows[0][0]).strip()
                print "issue_no:%s" % (issueNo)
	    else:
	        issueNo = -1
                print "error in find next issue_no,sql:",sql
        lot_conn.commit()
        lot_cur.close()
        lot_conn.close()
        print "CountIssueNo SUCC for [%s %s] at %s" % (lotId,issueNo,strftime("%Y-%m-%d %H:%M:%S",localtime(int(time()))))
	return issueNo
    except Exception, e:
        printExe("UpdateIssueTable FAIL for [%s %s]" % (lotId,issueNo))
        return(-1) 

#供外部调用
def IssueDrawSnatch(lotId, issueNo, resultOnly):
    print '='*9, strftime("%Y-%m-%d %H:%M:%S",localtime(int(time()))), '='*9

    if issueNo == "":        
        issueNo = CountIssueNo(lotId)
    if issueNo == -1 or len(issueNo) == 0:
        print "issue no is null, no need to snatch lotteryId[%s] issue." % (lotId)
        sys.exit(-1)
        
    if("SSQ" == lotId):
        if(len(issueNo) != 7):
            print "query issueNo Fail!"
            sys.exit(-1)
        print "Snatch [SSQ] for NO." + issueNo
        SnatchMpcData(lotId, issueNo, resultOnly)
    elif("QLC" == lotId):
        if(len(issueNo) != 7):
            print "query issueNo Fail!"
            sys.exit(-1)
        print "Snatch [QLC] for NO." + issueNo
        SnatchMpcData(lotId, issueNo, resultOnly)
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
    print "resultOnly=" + str(resultOnly)
    IssueDrawSnatch(sys.argv[1], issue_no, resultOnly)



