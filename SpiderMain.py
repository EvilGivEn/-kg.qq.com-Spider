#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests
import re
import sys
from SpiderClass import KGSpider

reload(sys)
sys.setdefaultencoding('utf-8')

PreUrl = 'http://kg.qq.com/node/personal?uid='

while True:

	temp = raw_input(u'请输入要抓取的全民K歌个人主页链接: '.decode('utf-8').encode('gbk'))
	temp = re.findall(r'\w{10,}', temp)

	if len(temp) == 0:
		print u'错误的个人主页.'
		continue

	uid = temp[0]

	html  = requests.get(url = PreUrl + uid)

	if html.status_code == 404 or html.content.find(r'invalid shareuid') != -1:

		print u'错误的个人主页.'
		continue

	else:

		Spider = KGSpider(uid = uid)
		Spider.Run()
		sys.exit(0)