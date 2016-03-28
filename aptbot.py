#!/usr/bin/python
# coding=utf-8
import sys
import time
import sqlite3
import telepot
from pprint import pprint
from datetime import date
from urllib2 import Request, urlopen
from urllib import urlencode, quote_plus
from bs4 import BeautifulSoup
import re

key = 'mcGA6xDEsvdIH3sbow%2B7gIBwxcGJC4dTkHt%2Bd7DXJ2pg2Gqq3g6IvU%2BLwFKCiqOQncYX2uI2Kav1yzRw7WO1RA%3D%3D'
url = 'http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTrade?ServiceKey='+key

def help(id):
    bot.sendMessage(id, '''명령어 사용법:
/howmuch 지역코드 년월 필터 : 해당 지역의 월 거래를 확인하며, 필터를 포함하는 정보를 조회합니다.
 (년월이 생략되면 현재 월로 설정되며, 필터가 생략되면 전체 구/군의 정보가 나옵니다.)
 ex. /howmuch 11710 201603
 ex. /howmuch 11710
 ex. /howmuch 11710 201603 잠실
/loc 지역명 : 지역코드 검색.
 ex. /loc 송파
/noti add : 구현 중...
/noti list
/noti remove
''')

def handle(msg):
    conn = sqlite3.connect('loc.db')
    c = conn.cursor()

    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type != 'text':
        bot.sendMessage(chat_id, '난 텍스트 이외의 메시지는 처리하지 못해요.')
        return
    #pprint(msg)

    text = msg['text']
    args = text.split(' ')
    res = ''
    if text.startswith('/'):
        if text.startswith('/loc'):
            if len(args)>1:
                param = args[1]
                c.execute('SELECT * FROM location WHERE loc LIKE "%%%s%%"'%param)
                for data in c.fetchall():
                    res += data[0] + ' : ' + data[1] + '\n'
                if not res:
                    res = '조회 결과가 없습니다. 구/군 이름으로 검색해 보세요.'
                bot.sendMessage(chat_id, res)
                return

        if text.startswith('/howmuch'):
            if len(args)>1:
                loc_param = args[1]
                if len(args)>2:
                    date_param = args[2]
                else:
                    today = date.today()
                    date_param = today.strftime('%Y%m')
                filter=''
                if len(args)>3:
                    filter = args[3].encode('utf-8')
                res=''
                printed = False
                request = Request(url+'&LAWD_CD='+loc_param+'&DEAL_YMD='+date_param)
                request.get_method = lambda: 'GET'
                res_body = urlopen(request).read()
                soup = BeautifulSoup(res_body, 'html.parser')
                items = soup.findAll('item')
                for item in items:
                    item = item.text.encode('utf-8')
                    item = re.sub('<.*?>', '|', item)
                    parsed = item.split('|')
                    row = parsed[2]+'/'+parsed[5]+'/'+parsed[6]+', '+parsed[3]+' '+parsed[4]+', '+parsed[7]+'m², '+parsed[9]+'F, '+parsed[1].strip()+'만원\n'
                    if filter and row.find(filter)<0:
                        row = ''
                    #print row
                    if len(res+row)>400: # becuz of telegram 400 char restrict
                        bot.sendMessage(chat_id, res)
                        res=row
                        printed = True
                    else:
                        res+=row
                if res:
                    bot.sendMessage(chat_id, res)
                elif not printed:
                    bot.sendMessage(chat_id, '조회 결과가 없습니다.')
                return

        if text.startswith('/noti'):
            pass

    help(chat_id)

TOKEN = sys.argv[1]
print 'received token :', TOKEN

bot = telepot.Bot(TOKEN)
pprint( bot.getMe() )

bot.notifyOnMessage(handle)

print 'Listening...'

while 1:
  time.sleep(10)