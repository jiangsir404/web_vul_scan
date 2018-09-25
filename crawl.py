#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = w8ay
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import requests
import re
import threading
import lxml.html
import urlparse
import time
from Queue import Queue
import vul_module
import urllib2
import chardet
from selenium import webdriver 
from bs4 import BeautifulSoup as bs


from config import *


_cookie = "PHPSESSID:a7va6lvk2u60js78f1hq90mefp"

def netlocdeal(url):
	if len(url.split('.')) == 2:
		return url
	return url.partition('.')[-1]

class SpiderThread(threading.Thread):
	def __init__(self,target,url,logfile,module):
		threading.Thread.__init__(self)
		self.target = target
		self.deep_url = url
		self.logfile = logfile
		self.module = module
		

	def GetLinks(self,host,html):
		soup = bs(html,"html.parser")
		results = soup.find_all(name='a')
		link_list = []
		if not results:
			return []
		# print results
		for item in results:
			if item.has_attr('href'): #判断是否有href标签
				if not re.compile("logout").search(item['href']): # 不爬取注销连接
					link_list.append(item['href'])

		# 去除不需要的后缀连接，如jpg,pdf,png之类的
		link_tmp1 = []
		for i in link_list:
			ext = urlparse.urlparse(i)[2].split('.')[-1]
			if ext not in IGNORE_EXT:
				link_tmp1.append(i)

		# 判断link是否是在目标域下
		link_tmp2 = []
		for i in link_tmp1:
			if netlocdeal(urlparse.urlparse(self.target).netloc) == netlocdeal(urlparse.urlparse(i).netloc):
				link_tmp2.append(i)

		return link_tmp2


	def SpiderPage(self):
		
		try:
			html = self.get_by_request()
			# if chardet.detect(html)['encoding'] == 'GB2312':
			# 	html = html.decode('gb2312').encode('utf8')
			# if chardet.detect(html)['encoding'] == 'UNICODE':
			# 	html = html.encode('utf8')
			html = html.encode('UTF-8')
			#print type(html)
			link_list = self.GetLinks(self.target,html)
			return link_list

		except Exception,e:
			print get_ctime() + '\tHttp error:',str(e)
			self.logfile.write(get_ctime() + '\tHttp error:' + str(e) + '\turl:' + self.deep_url[1] +'\n')
			self.logfile.flush()
		# print link_list
		

	def get_by_request(self):
		html = requests.get(url=self.deep_url[1],timeout=10,headers=HEADER).text
		return html

	def get_by_selenium(self):
		driver = webdriver.Chrome()
		cookie = {'name':_cookie.split(':')[0],'value':_cookie.split(':')[1]}
		driver.get(self.deep_url[1])
		driver.delete_all_cookies()
		driver.add_cookie(cookie)
		driver.refresh()
		html = driver.page_source
		driver.quit()
		return html

	def url_similar_check(self,url):
		'''
		URL相似度分析
		当url路径和参数键值类似时，则判为重复
		'''
		global SIMILAR_SET
		url_struct = urlparse.urlparse(url)
		query_key = '|'.join(sorted([ i.split('=')[0] for i in url_struct.query.split('&') ]))
		#print 'query_key:',query_key
		url_hash = hash(url_struct.path + query_key)
		if url_hash not in SIMILAR_SET:
			SIMILAR_SET.add(url_hash)
			return True
		return False



	def run(self):
		global QUEUE
		global TOTAL_URL
		link_list = self.SpiderPage()
		pre_url_list = TOTAL_URL

		TOTAL_URL = TOTAL_URL | set(link_list)
		new_url_list = list(TOTAL_URL - pre_url_list)

		#添加deep信息,并进行url相似度分析
		depth = self.deep_url[0] + 1
		for i in range(len(new_url_list)):
			if self.url_similar_check(new_url_list[i]):
				print(get_ctime() + '\tCrawl url:' + new_url_list[i] + ',depth:' + str(depth))
				vul_module.vul_module(new_url_list[i],self.logfile).check(self.module)
				self.logfile.write(get_ctime() + '\tCrawl url:' + new_url_list[i] + ' depth:' + str(depth) + '\n')
				self.logfile.flush()
				QUEUE.append([depth,new_url_list[i]])


if __name__ == '__main__':
	target = sys.argv[-1]
	#target = "https://user.0831home.com/user-index.html"
	SpiderThread(target, [0,target],open('log.txt',"a"),'xss').start()