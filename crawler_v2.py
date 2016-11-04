#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Created on 2016年10月26日

@author: luhaiya
@id: 2016110274
@description:
    1、没有将各个模块进行拆分文件，都合并在一个文件中，用定义类的方式封装各个模块（只是简单实现功能，没有过分抽象）
    1、requests不添加header以及必要的cookies可能会403 forbidden
    2、简单requests的get只能获取静态页面，注意网站是否是使用ajax加载，是的话有些内容获取不到
    3、关于爬取动态页面，接下来要深入研究一下，可能可以使用Selenium（自动化web测试解决方案）以及PhantomJS（一个没有图形界面的浏览器），也可以找到网站提供的接口
    4、xpath获取之后可能需要encode，关注一下编码问题
    5、字符串的拼接，更加喜欢用%的方式
    6、没有将各个模块进行拆分文件，都合并在一个文件中，用定义类的方式封装各个模块（只是简单实现功能，没有过分抽象）

'''
from lxml import html
import requests
import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

class Crawler:
    baseUrl = ''
    htmlData = ''
    newurl = set()
    oldurl = set()
    headers = {}
    cookies = {}
    def __init__(self,baseurl,headers,cookies):
        self.baseUrl = baseurl
        self.headers = headers
        self.cookies = cookies
    def crawAllHtml(self,url):
        htmlData = requests.get(url,headers=self.headers,cookies=self.cookies).content
        self.htmlData = htmlData
    def crawJsonData(self,url):
        htmlData = requests.get(url).json()
        return htmlData
    def crawByXpath(self,xpath):
        domTree = html.fromstring(self.htmlData)
        data = domTree.xpath(xpath)
        return data
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
    #https://item.jd.com/10372809652.html------商品具体信息页面
    #https://list.jd.com/list.html?cat=1318,12115,12117&page=1&trans=1&JL=6_0_0&ms=6#J_main---------商品列表页面，获取各个商品的地址
    #https://p.3.cn/prices/mgets?type=1&area=1_72_4137_0&skuIds=J_10622607725&pdbp=0&pdtk=&pdpin=&pduid=1507505966&_=1477488482582--------价格获取接口
    cookies = {
        'ipLoc-djd': '1-72-4137-0',
        'unpl': 'V2_ZzNtbUsDFxR8DEZXchgOAWIEFlkRAkVCfV9PAX5MCVBkUUIJclRCFXIURlVnGlsUZwIZXUVcQBVFCHZXchBYAWcCGllyBBNNIEwHDCRSBUE3XHxcFVUWF3RaTwEoSVoAYwtBDkZUFBYhW0IAKElVVTUFR21yVEMldQl2VH8YWgFmBxpaRWdzEkU4dlJ7G18GZDMTbUNnAUEpC0dUcxFUSGcHE1tGVkcdcg92VUsa',
        '__jdv': '122270672|baidu-pinzhuan|t_288551095_baidupinzhuan|cpc|0f3d30c8dba7459bb52f2eb5eba8ac7d_0_8ee0851280c54655bd7f9f8d4ddd2cae|1477448181306',
        'ipLocation': '%u5317%u4EAC',
        'areaId': '1',
        '__jda': '122270672.1507505966.1476891958.1477448181.1477486886.5',
        '__jdb': '122270672.24.1507505966|5.1477486886',
        '__jdc': '122270672',
        '__jdu': '1507505966',
    }
        
    headers = {
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
    }
    baseUrl = 'https://list.jd.com/list.html?cat=1318,12115,12117'
    crawler = Crawler(baseUrl,headers,cookies)
    maxPage = 1;
    crawData = ''
    for page in range(1, maxPage+1):
        baseUrl = 'https://list.jd.com/list.html?cat=1318,12115,12117&page=%d&trans=1&JL=6_0_0&ms=6#J_main'%page
        crawler.crawAllHtml(baseUrl)
        xpath = '//*[@id="plist"]/ul/li'
        listgroup = crawler.crawByXpath(xpath)
        for list in listgroup:
            htmlpath = './div/div[1]/a/@href'
            href = len(list.xpath(htmlpath)) and list.xpath(htmlpath)[0] or ''
            crawler.getNewUrl('https:'+href)
    for url in crawler.newurl:
        crawData += '<----------------------------------------------------------->\n'
        crawler.crawAllHtml(url)
        xpath = '//*[@id="detail"]/div[2]/div[1]/div[1]/ul[2]/li'
        itemIdPath = '//*[@id="detail"]/div[2]/div[1]/div[1]/ul[2]/li[2]/text()'
        infogroup = crawler.crawByXpath(xpath)
        for info in infogroup:
            infopath = './text()'
            data = info.xpath(infopath)[0]+'\n'
            crawData += data
        itemId = len(crawler.crawByXpath(itemIdPath)) and crawler.crawByXpath(itemIdPath)[0] or ''
        if itemId!='':
            itemId = itemId[5:]
            priceAPI = 'https://p.3.cn/prices/mgets?type=1&area=1_72_4137_0&skuIds=J_%s&pdbp=0&pdtk=&pdpin=&pduid=1507505966&_=1477488482582'%itemId
            priceJsonData = crawler.crawJsonData(priceAPI)
            crawData += '售价：￥%s\n最高价：￥%s\n'%(priceJsonData[0]['p'],priceJsonData[0]['m'])
    file = File('result_v2','txt','./')
    file.inputData(crawData)
    file.closeFile()
            
if __name__ == "__main__":
    main()