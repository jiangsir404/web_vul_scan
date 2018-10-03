#coding:utf8
from config import *
from crawl import *
from vul_module import vul_module


def vulscan(target,thread_num,depth,module,policy,logfile):
	global QUEUE
	global TOTAL_URL

	print "[+] start scan target " + target
	logfile.write("[+] start scan target " + target + '...' + '\n') 

	QUEUE.append([0,target])
	# TOTAL_URL.add(target) #如果加上这行，那么第一个链接就无法检测了。
	SpiderThread(target, [0,target],logfile,module).start()
	print 'test crawl'
	quit_flag = 0
	while(quit_flag == 0):
		while True: # 从Queue中获取一条新链接，执行下一个while
			try:
				deep_url = QUEUE.pop(0)
				break
			except Exception,e:
				if threading.activeCount() == 1:
					print "[-] All crawl finish..."
					logfile.write("[-] All crawl finish..." + '\n') 
					quit_flag = 1
					break
				else:
					time.sleep(1)
					continue
		while True: 
			if deep_url[0] == depth + 1: # 如果该链接的depth等于设置的depth,就退出，不爬取该链接
				break
			try:
				if threading.activeCount() < thread_num:
					SpiderThread(target, deep_url,logfile,module).start() # target是不变的，deep_url才是变化的链接
					break
			except Exception,e:
				self.logfile.write(get_time() + '\tError:' + str(e) + '\n')
				self.logfile.flush()
				time.sleep(1)
				pass
	'''
	quit_flag = 0
	total_url_list = list(TOTAL_URL)
	while(quit_flag == 0):
		while True:
			try:
				url = total_url_list.pop(0)
				break
			except Exception,e:
				print e
				if threading.activeCount() == 1:
					print "All Scan Finish..."
					quit_flag = 1
					break
					#exit(0)
				time.sleep(1)
		
		while True:
			try:
				if threading.activeCount() < thread_num:
					vul_module(url,logfile).start()
					break
			except Exception,e:
				print e
				time.sleep(1)
				pass
	'''


	

