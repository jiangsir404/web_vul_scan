#coding:utf8
import time

IGNORE_EXT = ['css','js','jpg','png','gif','rar','pdf','doc']
#不期待的文件后缀
EXPECT_EXT = ['php','jsp','asp','aspx']


HEADER = {
	#'Cookie':"PHPSESSID=a7va6lvk2u60js78f1hq90mefp; Hm_lvt_2440c7a168754e8b63657a6c1fff1d91=1536996611; Hm_lpvt_2440c7a168754e8b63657a6c1fff1d91=1536996611; UM_distinctid=165dc23164e10d-06d20f21c4de03-24414032-102111-165dc23165096; PHPSESSID=he3og58eeph68vj156vhsmi3on"
	'Cookie':'_trs_uv=jjjjbinw_397_kvot; Hm_lvt_2001062cf1eba9e5e337e8464dd128dc=1537492975; __utmc=53807035; __utmz=53807035.1537492975.3.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utma=53807035.321804146.1532359458.1537492975.1537846212.4; __utmt=1; Hm_lpvt_2001062cf1eba9e5e337e8464dd128dc=1537846222; __utmb=53807035.3.10.1537846212; JSESSIONID=4D5D5CF5E0B62D542597B99DDC2DCC47'
}


QUEUE = []
TOTAL_URL = set()
SIMILAR_SET = set()

def get_ctime():
	return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())