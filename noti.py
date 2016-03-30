#!/usr/bin/python
# coding=utf-8
import sys
import time, datetime
import sqlite3
import telepot
from pprint import pprint
from datetime import date
from urllib2 import Request, urlopen
from urllib import urlencode, quote_plus
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

key = 'mcGA6xDEsvdIH3sbow%2B7gIBwxcGJC4dTkHt%2Bd7DXJ2pg2Gqq3g6IvU%2BLwFKCiqOQncYX2uI2Kav1yzRw7WO1RA%3D%3D'
url = 'http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTrade?ServiceKey='+key
ROOT = '/root/git/realestate-bot/'

def howmuch(loc_param, date_param, filter_param):
    res_list = []
    request = Request(url+'&LAWD_CD='+loc_param+'&DEAL_YMD='+date_param)
    request.get_method = lambda: 'GET'
    try:
        res_body = urlopen(request).read()
    except UnicodeEncodeError:
        return []
    soup = BeautifulSoup(res_body, 'html.parser')
    items = soup.findAll('item')
    for item in items:
        item = item.text.encode('utf-8')
        item = re.sub('<.*?>', '|', item)
        parsed = item.split('|')
        try:
            row = parsed[2]+'/'+parsed[5]+'/'+parsed[6]+', '+parsed[3]+' '+parsed[4]+', '+parsed[7]+'m², '+parsed[9]+'F, '+parsed[1].strip()+'만원\n'
        except IndexError:
            row = item.replace('|', ',')
        if filter_param and row.find(filter_param)<0:
            row = ''
        if row:
            res_list.append(row.strip())
    return res_list

def runNoti(date_param):
    conn2 = sqlite3.connect(ROOT+'logs.db')
    c2 = conn2.cursor()
    c2.execute('CREATE TABLE IF NOT EXISTS logs( user TEXT, log TEXT, PRIMARY KEY(user, log) )')
    conn2.commit()

    conn = sqlite3.connect(ROOT+'user.db')
    c = conn.cursor()
    c.execute('SELECT user,command from user') # get all comamnds
    for data in c.fetchall():
        filter_param=None
        user = data[0].encode('utf-8')
        command = data[1].encode('utf-8')
        params = command.split(' ')
        print user, date_param, params
        if len(params)>1:
            filter_param = params[1]
        res_list = howmuch( params[0], date_param, filter_param )
        msg = ''
        for r in res_list:
            try:
                c2.execute('INSERT INTO logs (user,log) VALUES ("%s", "%s")'%(user,r))
            except sqlite3.IntegrityError:
                # means already sent
                pass
            else:
                print str(datetime.now()).split('.')[0], r
                if len(r+msg+1)>400:
                    bot.sendMessage( user, msg )
                    msg = r+'\n'
                else:
                    msg += r+'\n'
        if msg:
            bot.sendMessage( user, msg )

    conn2.commit()

TOKEN = sys.argv[1]
print 'received token :', TOKEN

bot = telepot.Bot(TOKEN)
pprint( bot.getMe() )

today = date.today()
current_month = today.strftime('%Y%m')
now=datetime.now()
past=datetime(now.year, now.month, 1) - timedelta(days=1)
prev_month="%d%02d"%(past.year,past.month)

runNoti(prev_month)
runNoti(current_month)