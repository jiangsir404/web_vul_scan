# web_vul_scan
web漏洞扫描器
基于爬虫的多线程web漏洞扫描器
    
    python run.py --help
    Usage: run.py [options]
    
    Options:
      -h, --help            show this help message and exit
      -d DOMAIN, --domain=DOMAIN
                            Start the domain name
      -t THREAD_NUM, --thread=THREAD_NUM
                            Numbers of threads
      --depth=DEPTH         Crawling dept
      --module=MODULE       vulnerability module(sql,xss,rfi)
      --policy=POLICY       Scan vulnerability when crawling: 0,Scan vulnerability
                            after crawling: 1
      --log=LOGFILE_NAME    save log file

## 功能
- [x] 优化输出，加入颜色
- [x] 优化基于广度优先的爬虫策略（处理相对路径，目标域，爬取规则)
- [x] SQL 注入检测（未变)
- [x] xss 检测(加入检测网页输出点的功能，优化 payload)
- [x] callback 和 redirect 等关键字搜索
- [x] 加入多个参数的xss检测
