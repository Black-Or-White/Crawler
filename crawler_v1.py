#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Created on 2016年10月19日

@author: luhaiya
@id: 2016110274
@description: 为了上传方便，这个简单的爬虫就没有将各个模块进行拆分文件，都合并在一个文件中，用定义类的方式封装各个模块（只是简单实现功能，没有过分抽象，以后的爬虫作业在此之上进行完善抽象）.同时把一些收获也写在这里

心得：
    1、requests不添加header以及必要的cookies可能会403 forbidden
    2、简单requests的get只能获取静态页面，注意网站是否是使用ajax加载，是的话有些内容获取不到
    3、关于爬取动态页面，接下来要深入研究一下，可能可以使用Selenium（自动化web测试解决方案）以及PhantomJS（一个没有图形界面的浏览器），也可以找到网站提供的接口
    4、xpath获取之后可能需要encode，关注一下编码问题
    5、字符串的拼接，更加喜欢用%的方式
    6、还需要改进url的管理部分

'''
from lxml import html
import requests
import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

class Crawler:
    newurl = set()
    cookies = ''
    headers = {}
    def __init__(self,baseurl,headers):
        self.newurl.add(baseurl)
        self.headers = headers
    def crawler(self,url,xpath):
        htmlData = requests.get(url,headers=self.headers,cookies=self.cookies).content
        domTree = html.fromstring(htmlData)
        data = domTree.xpath(xpath)
        return data
    def getCookies(self,url):
        htmlData = requests.get(url,headers=self.headers,cookies=self.cookies)
        self.cookies = htmlData.cookies
    def getNewUrl(self,url):
        self.newurl.add(url)

class File:
    name = ''
    type = ''
    src = ''
    file = ''
    def __init__(self,name, type, src):
        self.name = name
        self.type = type
        self.src = src  
        filename = self.src+self.name+'.'+self.type
        self.file = open(filename,'w+')
    def inputData(self,data):
        self.file.write(data)
    def closeFile(self):
        self.file.close()
        
def main():
    baseUrl = 'http://www.mtime.com/top/movie/top100/'
    xpath = '//*[@id="asyncRatingRegion"]/li'
    pagepath = '//*[@id="PageNavigator"]/a'
    headers = {
        'Host': 'www.mtime.com',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36 LBBROWSER',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'http://www.mtime.com/',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
    }
    crawler = Crawler(baseUrl,headers)
    file = File('result','txt','./')
    crawler.getCookies(baseUrl)
    urlgroup = crawler.crawler(baseUrl, pagepath)
    for url in urlgroup:
        href = url.xpath('./@href')
        if len(href)!=0:
            crawler.getNewUrl(href[0]) 
    for url in crawler.newurl:
        datagroup=crawler.crawler(url, xpath)
        for li in datagroup:
            rank = len(li.xpath('./div[1]/em/text()')) and li.xpath('./div[1]/em/text()')[0] or 0
            movName = len(li.xpath('./div[3]/h2/a/text()')) and li.xpath('./div[3]/h2/a/text()')[0] or ''
            leader = len(li.xpath('./div[3]/p[1]/a/text()')) and li.xpath('./div[3]/p[1]/a/text()')[0] or ''
            actors = len(li.xpath('./div[3]/p[2]/a/text()')) and li.xpath('./div[3]/p[2]/a/text()')[0] or ''
            type = len(li.xpath('./div[3]/p[3]/span/a/text()')) and li.xpath('./div[3]/p[3]/span/a/text()')[0] or ''
            desc = len(li.xpath('./div[3]/p[4]/text()')) and li.xpath('./div[3]/p[4]/text()')[0] or ''
            point1 = len(li.xpath('./div[4]/b/span[1]/text()')) and li.xpath('./div[4]/b/span[1]/text()')[0] or 0
            point2 = len(li.xpath('./div[4]/b/span[2]/text()')) and li.xpath('./div[4]/b/span[2]/text()')[0] or '.0'
            point = len(li.xpath('./div[4]/p/text()')) and li.xpath('./div[4]/p/text()')[0] or ''
            str = '排名:%s     电影名称:%s     导演:%s     主演:%s     类型:%s     简介:%s     评分:%s%s分      %s  \n'%(rank,movName,leader,actors,type,desc,point1,point2,point)
            print str
            file.inputData(str)
            str = ''
    file.closeFile()
            
if __name__ == "__main__":
    main()