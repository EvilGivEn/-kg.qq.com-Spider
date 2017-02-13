#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests
import re
import os.path
import sys
import time
import json
import threading
import hashlib
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf-8')

class KGSpider:

	def __init__(self, uid):

		self.uid    = uid
		self.Songs  = []
		self.Failed = []
		self.Record = []
		self.PreUrl = 'http://kg.qq.com/cgi/kg_ugc_get_homepage?from=1&g_tk=5381&g_tk_openkey=5381&format=json&type=get_ugc'


	def DownloadMusic(self, Url, Name, ID, Path = './'):
		Times = 1
		while True:
			try:
				html = requests.get(url = Url, timeout = 60)
				temp = re.findall(r'"playurl":"http://.*\.m4a[\w=&?]*"', html.content)
				Type = '.m4a'
				if len(temp) == 0:
					temp = re.findall(r'"playurl_video":"http://.*\.mp4[\w=&?]*"', html.content)
					Type = '.mp4'
					if len(temp) == 0:
						break
					else:
						FileUrl = temp[0][17:-1]
				else:
					FileUrl = temp[0][11:-1]
				FileName = Name + ' [' + ID + ']' + Type
				print u'开始下载 ' + Name
				download = requests.get(url = FileUrl, timeout = 60).content
				md5 = hashlib.md5(download).hexdigest()
				if not md5 in self.Record:
					with open(Path + FileName.decode('utf-8').encode('gbk'), 'wb') as fp:
						fp.write(download)
					self.Record += [md5]
					print Name + u' 下载完毕 '
				else:
					print Name + u' 已存在'

			except:
				if Times <= 3:
					print Name + u' 下载失败 正在进行第 ' + str(Times) + u' 次重试(共 3 次)'
					Times += 1
					time.sleep(3)
					continue
				else:
					print Name + u' 下载失败 重试次数用尽'
					self.Failed += [{'name':Name, 'id':ID}]
					break

			break


	def Run(self):

		html = requests.get('http://kg.qq.com/node/personal?uid=' + self.uid)
		UserName = re.findall(r'<span class="my_show__name">.*?</span>', html.content)
		if len(UserName) == 0:
			UserName = ''
		else:
			UserName = UserName[0][28:-7]
		print u'用户名: ' + UserName
	
		html  = requests.get(url = self.PreUrl + '&start=' + str(1) + '&num=8&touin=&share_uid=' + self.uid)

		Total = int(json.loads(html.content.decode('gbk').encode('utf-8'))['data']['ugc_total_count'])
		PageN = Total / 8
		if Total % 8 != 0:
			PageN += 1

		print u'共 ' + str(Total) + u' 个歌曲或视频文件'

		for i in range(PageN):

			html = requests.get(url = self.PreUrl + '&start=' + str(i + 1) + '&num=8&touin=&share_uid=' + self.uid).content
			temp = json.loads(html.decode('gbk').encode('utf-8'))['data']['ugclist']

			for it in temp:
				self.Songs += [{'url':'http://kg.qq.com/node/play?s=' + it['shareid'], 'name':it['title'], 'id':it['shareid']}]

		Path = './' + re.sub(r'[\/:*?"<>|]', '_', UserName.decode('utf-8').encode('gbk')) + ' [' + self.uid + ']' + '/'

		if not os.path.exists(Path):
			os.makedirs(Path)

		if os.path.isfile(Path + 'Record.json'):
			with open(Path + 'Record.json', 'r') as fp:
				self.Record = json.load(fp)

		Threads = []
		for Song in self.Songs:
			ThisThread = threading.Thread(target = self.DownloadMusic, args = (Song['url'], Song['name'], Song['id'], Path, ))
			Threads += [ThisThread]
			ThisThread.start()

		for ThisThread in Threads:
			ThisThread.join()

		if len(self.Failed) == 0:
			print u'\n全部下载完成'
		else:
			print u'部分内容下载失败'
			for it in self.Failed:
				print it['name'] + ' [' + it['id'] + ']'

		with open(Path + 'Record.json', 'w') as fp:
			json.dump(self.Record, fp)
