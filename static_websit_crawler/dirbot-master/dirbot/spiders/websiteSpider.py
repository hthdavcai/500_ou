# -*- coding: utf-8 -*-
from dirbot.jsonDataDemo import jsonDataDemo
from dirbot.DataDemoUtil import DataDemoUtil
from scrapy.selector import Selector
from scrapy.contrib.spiders import CrawlSpider
import ConfigParser
import json
import logging
import urlparse
import copy
import scrapy
import os
import datetime

cf = ConfigParser.ConfigParser()
cf.read("platinfo.cfg")


class websiteSpider(CrawlSpider):
    def __init__(self, category=None, filePath=None):
        f = file(category)
        jsonstr = f.read()
        f.close()
        if os.path.isfile(filePath):
            os.remove(filePath)

        self.jsonstr = '%s' % jsonstr
        self.DataDemoUtil = DataDemoUtil()
        self.dataDemo = DataDemoUtil.__getDataDemoFromString__(self.DataDemoUtil, jsonstr)
        self.start_urls = [
            self.dataDemo.__getURL__('URL')
        ]
        self.crawlerTime = datetime.datetime.now()
        print 'init'

    jsonstr = ''
    name = cf.get("spider", "spider_name")

    # is woring  really * is delete this
    # allowed_domains = ["*"]

    def parse(self, response):
        if response.meta.has_key('config'):
            configStr = response.meta['config']
            currentDataDemo = DataDemoUtil.__getDataDemoFromString__(self.DataDemoUtil, configStr)
        else:
            currentDataDemo = self.dataDemo

        try:
            sel = Selector(response)
            variables = currentDataDemo.__getVariables__('variables')
            actualVars = copy.deepcopy(variables)
            while 1 == 1:
                item = {}
                itemCount = 0
                items = currentDataDemo.__getItems__('items')
                for jsonitem in items:
                    try:
                        xpath = str(jsonitem.get('xpath'))
                        for var in variables:
                            xpath = xpath.replace(var.get('flag'), str(var.get('min')))
                        valuexpath = sel.xpath(xpath).extract()
                        valuexpathone = valuexpath[0].strip('\r\n').strip('\r\n').strip(' ')
                        item[str(jsonitem.get('name'))] = str(valuexpathone).strip()
                        # print jsonitem.get('name')
                        # print item[str(jsonitem.get('name'))],
                        itemCount = itemCount + 1
                        # print "itemCount" ,
                        # print itemCount,
                    except Exception, e:
                        item[str(jsonitem.get('name'))] = ""
                chirdrenJsonObjects = currentDataDemo.__getChirdren__(currentDataDemo)
                for chirdrenjsonDataDemo in chirdrenJsonObjects:
                    jsonDataDemo().encode(chirdrenjsonDataDemo)
                    jsonConfigString = json.dumps(chirdrenjsonDataDemo, cls=jsonDataDemo)

                    for itemkey in item.keys():
                        jsonConfigString = jsonConfigString.replace(str("#" + itemkey + "#"), str(item[itemkey]))

                    jsonConfigObject = json.loads(jsonConfigString)
                    chirdrenKey = jsonConfigObject['URL'].replace(str('#super.'), str(''))
                    chirdrenLink = item[chirdrenKey]
                    if chirdrenLink != '':
                        chirdrenURL = urlparse.urljoin(response.url, chirdrenLink)
                        chirdrenURL = chirdrenURL.replace("##year", str(self.crawlerTime.year))
                        chirdrenURL = chirdrenURL.replace("##month", str(self.crawlerTime.month))
                        chirdrenURL = chirdrenURL.replace("##day", str(self.crawlerTime.day))
                        chirdrenURL = chirdrenURL.replace("##hour", str(self.crawlerTime.hour))
                        chirdrenURL = chirdrenURL.replace("##minute", str(self.crawlerTime.minute))
                        chirdrenURL = chirdrenURL.replace("##second", str(self.crawlerTime.second))
                        jsonConfigObject['URL'] = chirdrenURL
                        jsonConfigString = json.dumps(jsonConfigObject)
                        yield scrapy.Request(chirdrenURL, meta={'config': jsonConfigString},
                                             callback=self.parse_chirdren)
                yield item
                finish = 0;
                for c in range(0, len(variables)):
                    if variables[c]['min'] == actualVars[c]['max']:
                        finish = finish + 1
                if finish == len(variables):
                    break;
                variables = self.addVars(variables, actualVars);
            print 'Spider While Crawler OK'

            date_now = self.crawlerTime.date()
            if response.url != "http://live.500.com/?e={}".format(date_now - datetime.timedelta(days=1)):
                next_request = "http://live.500.com/?e={}".format(date_now - datetime.timedelta(days=1))
                yield scrapy.Request(next_request, meta={'config': self.jsonstr}, callback=self.parse)

        except Exception, e:
            print e
            logging.error(e)

    def parse_chirdren(self, response):
        configStr = response.meta['config']
        print "parse_chirdren"
        currentDataDemo = DataDemoUtil.__getDataDemoFromString__(self.DataDemoUtil, configStr)
        try:
            sel = Selector(response)
            variables = currentDataDemo.__getVariables__('variables');
            actualVars = copy.deepcopy(variables)
            while 1 == 1:
                item = {}
                item['###spiderConfigString###'] = configStr
                itemCount = 0
                items = currentDataDemo.__getItems__('items')
                for jsonitem in items:
                    try:
                        xpath = str(jsonitem.get('xpath'))
                        for var in variables:
                            xpath = xpath.replace(var.get('flag'), str(var.get('min')))
                        valuexpath = sel.xpath(xpath).extract()
                        valuexpathone = valuexpath[0].strip('\r\n').strip('\r\n').strip(' ')
                        # print valuexpathone,
                        item[str(jsonitem.get('name'))] = valuexpathone
                        # print jsonitem.get('name')
                        # print item[str(jsonitem.get('name'))],
                        itemCount = itemCount + 1
                        # print "itemCount" ,
                        # print itemCount,
                    except Exception, e:
                        item[str(jsonitem.get('name'))] = ""
                        # print ''
                chirdrenJsonObjects = currentDataDemo.__getChirdren__(currentDataDemo)
                for chirdrenjsonDataDemo in chirdrenJsonObjects:
                    jsonDataDemo().encode(chirdrenjsonDataDemo)
                    jsonConfigString = json.dumps(chirdrenjsonDataDemo, cls=jsonDataDemo)

                    for itemkey in item.keys():
                        jsonConfigString = jsonConfigString.replace(str("#" + itemkey + "#"), str(item[itemkey]))

                    jsonConfigObject = json.loads(jsonConfigString)
                    chirdrenKey = jsonConfigObject['URL'].replace(str('#super.'), str(''))
                    chirdrenLink = item[chirdrenKey]
                    if chirdrenLink != '':
                        chirdrenURL = urlparse.urljoin(response.url, chirdrenLink)
                        chirdrenURL = chirdrenURL.replace("##year", str(self.crawlerTime.year))
                        chirdrenURL = chirdrenURL.replace("##month", str(self.crawlerTime.month))
                        chirdrenURL = chirdrenURL.replace("##day", str(self.crawlerTime.day))
                        chirdrenURL = chirdrenURL.replace("##hour", str(self.crawlerTime.hour))
                        chirdrenURL = chirdrenURL.replace("##minute", str(self.crawlerTime.minute))
                        chirdrenURL = chirdrenURL.replace("##second", str(self.crawlerTime.second))
                        jsonConfigObject['URL'] = chirdrenURL
                        jsonConfigString = json.dumps(jsonConfigObject)
                        yield scrapy.Request(chirdrenURL, meta={'config': jsonConfigString},
                                             callback=self.parse_chirdren)
                yield item
                # count
                finish = 0;
                for c in range(0, len(variables)):
                    if variables[c]['min'] == actualVars[c]['max']:
                        finish = finish + 1
                if finish == len(variables):
                    break;
                variables = self.addVars(variables, actualVars);
            print 'Spider While Crawler OK'
        except Exception, e:
            print e
            logging.error(e)

    # return to pipelines For First Crawler
    def getDataDemo(self):
        return self.dataDemo

    #  vars ++ 
    def addVars(self, vars, acutalVars):
        vc = len(acutalVars) - 1;
        if vc == 0:
            val = vars[vc]['min'] + 1;
            if val <= acutalVars[vc]['max']:
                vars[vc]['min'] = val
                return vars;
        for vc in range(vc, 0, -1):
            val = vars[vc]['min'] + 1;
            if val <= acutalVars[vc]['max']:
                vars[vc]['min'] = val
                return vars;
            else:
                vars[vc]['min'] = acutalVars[vc]['min']
                if vc - 1 >= 0:
                    vars[vc - 1]['min'] = vars[vc - 1]['min'] + 1
                return vars;
        return vars;
