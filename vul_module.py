#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = w8ay
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import requests
import urlparse
from urllib import quote as urlencode
from urllib import unquote as urldecode
from bs4 import BeautifulSoup as bs
import md5
import json
import sys
import re
import urlparse
import copy
import threading
import dbms as dbms
from config import *
from colorprinter import *

reload(sys)
sys.setdefaultencoding( "utf-8" )

PROXY = {
  "http": "http://127.0.0.1:1080"
}


COOKIE = {}

vul_file = open('vulfile.txt','w')

def md5_encrypt(str):  
	m = md5.new()   
	m.update(str)   
	return m.hexdigest()  

class vul_module(threading.Thread):

	def __init__(self,url,logfile):
		threading.Thread.__init__(self)
		self.url = url
		self.testurl = ''
		self.sql_errors = []
		self.logfile = logfile
		self.output = ColorPrinter()
		up = lambda x:urlparse.urlparse(x)
		self.url_struct = up(self.url)
		self.TEST_PAYLOAD = [
			'rivirtest'
			]
		self.XSS_PAYLOAD	= [
			'<script>confirm(1)</script>',
			'<img onerror=alert`1` src=0>',
			'x"><img>',
			'" onfocus=alert(1) autofocus x="'
		]

	def Integer_sqlinj_scan(self):
		try:
			res_md5_1 = md5_encrypt(requests.get(url=self.url,headers=HEADER).text)
			res_md5_2 = md5_encrypt(requests.get(url=self.url+urlencode('+1'),headers=HEADER).text)
			res_md5_3 = md5_encrypt(requests.get(url=self.url+urlencode('+1-1'),headers=HEADER).text)
		except Exception,e:
			traceback.print_exc()
			res_md5_1 = res_md5_2 = res_md5_3 = 0
			pass

		if ( res_md5_1 == res_md5_3 ) and res_md5_1 != res_md5_2:
			return 1
		return 0

								
	def Str_sqlinj_scan(self):
		quotes = ['\'' , '"','']
		payload_0 = [" and 0;-- ","/**/and/**/0;#","\tand\t0;#","\nand/**/0;#"]
		payload_1 = [" and 1;-- ","/**/and/**/1;#","\tand\t1;#","\nand/**/1;#"]

		for i in quotes:
			for j in range(len(payload_0)):
				p0 = i + payload_0[j]
				p1 = i + payload_1[j]
				try:
					res_md5_1 = md5_encrypt(requests.get(url=self.url,headers=HEADER).text)
					res_md5_2 = md5_encrypt(requests.get(url=self.url+urlencode(p0),headers=HEADER).text)
					res_md5_3 = md5_encrypt(requests.get(url=self.url+urlencode(p1),headers=HEADER).text)
				except Exception,e:
					traceback.print_exc()
					res_md5_1 = res_md5_2 = res_md5_3 = 0
					pass
				if ( res_md5_1 == res_md5_3 ) and res_md5_1 != res_md5_2:
					return 1
		return 0

	def Sql_error_scan(self):
		'''
		This method searches for SQL errors in html's.
		
		@parameter response: The HTTP response object
		@return: A list of errors found on the page
		'''
		r1 = requests.get(url=self.url,headers=HEADER)
		r2 = requests.get(url=self.url+urlencode('\''),headers=HEADER)

		res = []
		for sql_regex, dbms_type in self.Get_sql_errors():
			match1 = sql_regex.search(r1.text)
			match2 = sql_regex.search(r2.text)
			if  match2 and not match1 :
				msg = 'A SQL error was found in the response supplied by the web application,'
				msg += match2.group(0)  + '". The error was found '
				#res.append( (sql_regex, match.group(0), dbms_type) )
				return 1
		return 0

	def param_get_xss(self):
		params = self.url_struct.query.split('&')
		for i in range(len(params)): # 对每个参数都加上payload 检测xss
			for test in self.XSS_PAYLOAD:
				querys = copy.deepcopy(params) # list 深拷贝
				querys[i] = params[i] + test
				url_preix = self.url.partition('?')[0]
				self.testurl = url_preix+'?'+('&'.join(querys))
				if debug:
					output.print_blue_text('xss payload: '+self.testurl)
				try:
					r = requests.get(url=self.testurl,headers=HEADER)
					if test in r.text:
						return 1
				except Exception,e:
					output.print_red_text(e)

			for test in self.TEST_PAYLOAD:
				querys = copy.deepcopy(params)
				querys[i] = params[i] + test
				url_preix = self.url.partition('?')[0]
				self.testurl = url_preix+'?'+('&'.join(querys))
				if debug:
					output.print_blue_text('test payload: '+self.testurl)
				try:
					r = requests.get(url=self.testurl,headers=HEADER)
					if test in r.text:
						self.output.print_yellow_text(get_ctime() + '\t' + self.testurl + " => OUTPUT Point(maybe xss)")
				except Exception,e:
					traceback.print_exc()

		return 0

	def param_post_xss(self):
		#print 'param_post_xss'
		#  不判断有验证码的情况
		# 不判断 form 表单没有submit 按钮的情况
		# 如果有hidden的默认表单，如果有value，则用默认的value,不修改
		# post 参数不需要像get一样一个个去检测参数，post直接将所有的input都写上payload即可。

		url_preix = self.url.rpartition('/')[0] #如果是相对路径，则url_preix + actionUrl
		url_root =  self.url_struct[0]+'://'+self.url_struct[1] #如果指定了根路径，则url_root+actionUrl
		html = requests.get(url=self.url,headers=HEADER).text
		soup = bs(html,"html.parser")
		forms = soup.find_all(name="form")
		#print forms
		if not forms:
			return false
		for form in forms:
			if form.has_attr('action'):
				actionUrl = form['action'] 
			else:
				actionUrl = ''
			if actionUrl == '#' or actionUrl == '': #默认处理
				self.testurl = self.url
			elif actionUrl.startswith('/'): #绝对路径处理
				self.testurl = url_root + actionUrl
			elif actionUrl.startwith('./') or actionUrl.startswith('../'): #相对路径处理
				self.testurl = url_preix + actionUrl

			method = form['method']
			if method == '':
				method = 'get'
			sendData = {}
			for child in form.descendants: #
				if child.name == 'input' and child['type'] == 'hidden' and child.has_attr('value'):
					sendData[child['name']] = child['value']
				elif child.name == 'input' and child.has_attr('name') and not child['type'] == 'hidden':	
					sendData[child['name']] = ''

			#print '[INFO]:',self.testurl,method,sendData

			for test in self.XSS_PAYLOAD:

				for i in sendData.keys():
					if sendData[i] == '':
						sendData[i] = test
					

				if method.lower() == "post":
					if debug:
						output.print_blue_text('post payload: '+str(sendData))
					r = requests.post(url=self.testurl,data=sendData,headers=HEADER)
					#print r.text
					if test in r.text:
						self.output.print_green_text(get_ctime() + '\t' + self.testurl + " POST XSS: "+ str(sendData))
						break

				if method.lower() == 'get':
					query = ''
					for i in sendData.keys():
						query += (i + '=' + sendData[i]+'&')

					if debug:
						output.print_blue_text('get payload: '+str(self.testurl+'?'+query))
					r = requests.get(url=self.testurl+'?'+query,headers=HEADER)
					if test in r.text:
						self.output.print_green_text(get_ctime() + '\t' + self.testurl + " GET XSS: "+ str(self.testurl+'?'+query))
						break 




	def Xss_scan(self):
		if self.param_get_xss():
			return 1
		elif self.param_post_xss():
			return 1
		else:
			return 0
		
	# def FileInclude_scan(self):
	# 	#http://192.168.87.143/fileincl/example1.php?page=intro.php
	# 	#如上，要把参数替换成我们想要的,?page=intro.php替换为page=http://www.baidu.com
	# 	#把全部参数都替换成了payload
	# 	RFI_PAYLOAD = [
	# 		"http://www.baidu.com"
	# 	]
	# 	url = urlparse.urlparse(self.url)
	# 	url_query = url.query
	# 	url_query_tmp = []
	# 	if not url_query:
	# 		return 0
	# 	for i in url_query.split('&'):
	# 		i_tmp = i.replace(i.split('=')[1],RFI_PAYLOAD[0])
	# 		url_query_tmp = url_query
	# 		url_query_tmp = url_query_tmp.replace(i,i_tmp)
	# 		url_tmp = urlparse.urlunparse( urlparse.ParseResult(url.scheme,url.netloc,url.path,url.params,url_query_tmp,url.fragment) )
	# 		r = requests.get(url=url_tmp,headers=HEADER)
	# 		if  "tieba.baidu.com" in r.text:
	# 			return 1
	# 	return 0

	def Api_scan(self):
		url = urlparse.urlparse(self.url)
		url_query = url.query 
		url_query_tmp = []
		for i in url_query.split('&'):
			if i.split('=')[0] == 'callback':
				self.output.print_yellow_text(get_ctime() + '\t' + self.testurl + " => jsonp callback!")
			if i.split('=')[0] == 'redirect' or i.split('=')[0] == 'resurl':
				self.output.print_yellow_text(get_ctime() + '\t' + self.testurl + " => redirect!")

		
	def Get_sql_errors(self):
		
		if len(self.sql_errors) != 0:
			return self.sql_errors
			
		else:
			errors = []
			
			# ASP / MSSQL
			errors.append( ('System\.Data\.OleDb\.OleDbException', dbms.MSSQL ) )
			errors.append( ('\\[SQL Server\\]', dbms.MSSQL ) )
			errors.append( ('\\[Microsoft\\]\\[ODBC SQL Server Driver\\]', dbms.MSSQL ) )
			errors.append( ('\\[SQLServer JDBC Driver\\]', dbms.MSSQL ) )
			errors.append( ('\\[SqlException', dbms.MSSQL ) )
			errors.append( ('System.Data.SqlClient.SqlException', dbms.MSSQL ) )
			errors.append( ('Unclosed quotation mark after the character string', dbms.MSSQL ) )
			errors.append( ("'80040e14'", dbms.MSSQL ) )
			errors.append( ('mssql_query\\(\\)', dbms.MSSQL ) )
			errors.append( ('odbc_exec\\(\\)', dbms.MSSQL ) )
			errors.append( ('Microsoft OLE DB Provider for ODBC Drivers', dbms.MSSQL ))
			errors.append( ('Microsoft OLE DB Provider for SQL Server', dbms.MSSQL ))
			errors.append( ('Incorrect syntax near', dbms.MSSQL ) )
			errors.append( ('Sintaxis incorrecta cerca de', dbms.MSSQL ) )
			errors.append( ('Syntax error in string in query expression', dbms.MSSQL ) )
			errors.append( ('ADODB\\.Field \\(0x800A0BCD\\)<br>', dbms.MSSQL ) )
			errors.append( ("Procedure '[^']+' requires parameter '[^']+'", dbms.MSSQL ))
			errors.append( ("ADODB\\.Recordset'", dbms.MSSQL ))
			errors.append( ("Unclosed quotation mark before the character string", dbms.MSSQL ))
			
			# DB2
			errors.append( ('SQLCODE', dbms.DB2 ) )
			errors.append( ('DB2 SQL error:', dbms.DB2 ) )
			errors.append( ('SQLSTATE', dbms.DB2 ) )
			errors.append( ('\\[IBM\\]\\[CLI Driver\\]\\[DB2/6000\\]', dbms.DB2 ) )
			errors.append( ('\\[CLI Driver\\]', dbms.DB2 ) )
			errors.append( ('\\[DB2/6000\\]', dbms.DB2 ) )
			
			# Sybase
			errors.append( ("Sybase message:", dbms.SYBASE ) )
			
			# Access
			errors.append( ('Syntax error in query expression', dbms.ACCESS ))
			errors.append( ('Data type mismatch in criteria expression.', dbms.ACCESS ))
			errors.append( ('Microsoft JET Database Engine', dbms.ACCESS ))
			errors.append( ('\\[Microsoft\\]\\[ODBC Microsoft Access Driver\\]', dbms.ACCESS ) )
			
			# ORACLE
			errors.append( ('(PLS|ORA)-[0-9][0-9][0-9][0-9]', dbms.ORACLE ) )
			
			# POSTGRE
			errors.append( ('PostgreSQL query failed:', dbms.POSTGRE ) )
			errors.append( ('supplied argument is not a valid PostgreSQL result', dbms.POSTGRE ) )
			errors.append( ('pg_query\\(\\) \\[:', dbms.POSTGRE ) )
			errors.append( ('pg_exec\\(\\) \\[:', dbms.POSTGRE ) )
			
			# MYSQL
			errors.append( ('supplied argument is not a valid MySQL', dbms.MYSQL ) )
			errors.append( ('Column count doesn\'t match value count at row', dbms.MYSQL ) )
			errors.append( ('mysql_fetch_array\\(\\)', dbms.MYSQL ) )
			errors.append( ('mysql_', dbms.MYSQL ) )
			errors.append( ('on MySQL result index', dbms.MYSQL ) )
			errors.append( ('You have an error in your SQL syntax;', dbms.MYSQL ) )
			errors.append( ('You have an error in your SQL syntax near', dbms.MYSQL ) )
			errors.append( ('MySQL server version for the right syntax to use', dbms.MYSQL ) )
			errors.append( ('\\[MySQL\\]\\[ODBC', dbms.MYSQL ))
			errors.append( ("Column count doesn't match", dbms.MYSQL ))
			errors.append( ("the used select statements have different number of columns", dbms.MYSQL ))
			errors.append( ("Table '[^']+' doesn't exist", dbms.MYSQL ))

			
			# Informix
			errors.append( ('com\\.informix\\.jdbc', dbms.INFORMIX ))
			errors.append( ('Dynamic Page Generation Error:', dbms.INFORMIX ))
			errors.append( ('An illegal character has been found in the statement', dbms.INFORMIX ))
			
			errors.append( ('<b>Warning</b>:  ibase_', dbms.INTERBASE ))
			errors.append( ('Dynamic SQL Error', dbms.INTERBASE ))
			
			# DML
			errors.append( ('\\[DM_QUERY_E_SYNTAX\\]', dbms.DMLDATABASE ))
			errors.append( ('has occurred in the vicinity of:', dbms.DMLDATABASE ))
			errors.append( ('A Parser Error \\(syntax error\\)', dbms.DMLDATABASE ))
			
			# Java
			errors.append( ('java\\.sql\\.SQLException', dbms.JAVA ))
			errors.append( ('Unexpected end of command in statement', dbms.JAVA ))

			# Coldfusion
			errors.append( ('\\[Macromedia\\]\\[SQLServer JDBC Driver\\]', dbms.MSSQL ))
			
			# Generic errors..
			errors.append( ('SELECT .*? FROM .*?', dbms.UNKNOWN ))
			errors.append( ('UPDATE .*? SET .*?', dbms.UNKNOWN ))
			errors.append( ('INSERT INTO .*?', dbms.UNKNOWN ))
			errors.append( ('Unknown column', dbms.UNKNOWN ))
			errors.append( ('where clause', dbms.UNKNOWN ))
			errors.append( ('SqlServer', dbms.UNKNOWN ))
			
			#  compile them and save that into self.sql_errors. 
			for re_string, dbms_type in errors:
				self.sql_errors.append( (re.compile(re_string, re.IGNORECASE ), dbms_type) )
		
		return self.sql_errors

	def check(self,module):
		global vul_file
		if self.url_struct.query != '': # 没有参数的链接可以爬取，但是不需要检测，过滤没有参数的链接的检测。
			if module == 'all':
				self.run()
			if module == 'sql':
				if self.Integer_sqlinj_scan() or self.Str_sqlinj_scan() or self.Sql_error_scan():
					self.output.print_green_text(get_ctime() + '\t' + self.url + "=> SQL injection!")
					self.logfile.write(get_ctime() + '\t' + self.url + "=> SQL injection!" + '\n')
					self.logfile.flush()

					vul_file.write(self.url + '\t' + "SQL injection!" + '\n')
					vul_file.flush()
			if module == 'xss':
				if self.Xss_scan():
					self.output.print_green_text(get_ctime() + '\t' + self.testurl + " => XSS!")
					self.logfile.write(get_ctime() + '\t' + self.testurl + " => XSS!" + '\n')
					self.logfile.flush()

					vul_file.write(self.url + '\t' + "XSS!" + '\n')
					vul_file.flush()
			if module == 'api':
				self.Api_scan()
				# if self.Api_scan():
				# 	self.output.print_green_text(get_ctime() + '\t' + self.url + " => api !")
				# 	self.logfile.write(get_ctime() + '\t' + self.url + " => api !" + '\n')
				# 	self.logfile.flush()

				vul_file.write(self.url + '\t' + "api bug!" + '\n')
				vul_file.flush()
		else: #对没有参数的链接进行form 表单检测
			self.param_post_xss()




	def run(self):
		#待添加具体url匹配哪个漏洞
		print "[+] %s\t%s" % (get_ctime(),self.url)
		if self.Integer_sqlinj_scan():
			self.output.print_green_text(get_ctime() + '\t' + self.url + " => Integer SQL injection!" + '\n')
			self.logfile.write(get_ctime() + '\t' + self.url + " => Integer SQL injection!" + '\n')
			self.logfile.flush()
			vul_file.write(self.url + '\t' + "Integer SQL injection!" + '\n')
			vul_file.flush()
		elif self.Str_sqlinj_scan():
			self.output.print_green_text(get_ctime() + '\t' + self.url + " => String SQL injection!" + '\n')
			self.logfile.write(get_ctime() + '\t' + self.url + " => String SQL injection!" + '\n')
			self.logfile.flush()
			vul_file.write(self.url + '\t' + "String SQL injection!" + '\n')
			vul_file.flush()
		elif self.Sql_error_scan():
			self.output.print_green_text(get_ctime() + '\t' + self.url + "=> SQL error injection!" + '\n')
			self.logfile.write(get_ctime() + '\t' + self.url + "=> SQL error injection!" + '\n')
			self.logfile.flush()
			vul_file.write(self.url + '\t' + "SQL error injection!" + '\n')
			vul_file.flush()
		elif self.Xss_scan():
			self.output.print_green_text(get_ctime() + '\t' + self.testurl + " => XSS vulnerabe!" + '\n')
			self.logfile.write(get_ctime() + '\t' + self.testurl + " => XSS vulnerabe!" + '\n')
			self.logfile.flush()
			vul_file.write(self.url + '\t' + "XSS vulnerabe!" + '\n')
			vul_file.flush()

			self.Api_scan()
		else:
			self.output.print_blue_text(" /** above links is no vulnerabe **/")
			self.logfile.write(get_ctime() + '\t' + self.url + " => safe" + '\n')
			self.logfile.flush()

if __name__ == '__main__':
	
	logfile = open('logfile.txt','a')
	

	url = "http://121.41.128.239:8098/stkj/index.php/product/safety_wire?t=7"
	self = vul_module(url,logfile)
	self.start()

	'''
	url = "http://192.168.8.131/sqli/example1.php?name=root"
	self = vul_module(url,logfile)
	self.start()

	url = "http://192.168.8.131/sqli/example2.php?name=root"
	self = vul_module(url,logfile)
	self.start()

	url = "http://192.168.8.131/sqli/example3.php?name=root"
	self = vul_module(url,logfile)
	self.start()

	
	url = "http://192.168.8.131/sqli/example4.php?id=2"
	self = vul_module(url,logfile)
	self.start()

	

	url = "http://192.168.8.131/sqli/example5.php?id=2"
	self = vul_module(url,logfile)
	self.start()

	url = "http://192.168.8.131/sqli/example6.php?id=2"
	self = vul_module(url,logfile)
	self.start()

	

	url = "http://192.168.8.131/sqli/example7.php?id=2"
	self = vul_module(url,logfile)
	self.start()

	url = "http://192.168.8.131/sqli/example8.php?order=name"
	self = vul_module(url,logfile)
	self.start()

	url = "http://192.168.8.131/sqli/example9.php?order=name"
	self = vul_module(url,logfile)
	self.start()
	'''
