# -*- coding: utf-8 -*-
"""
Created on Thu May  7 00:04:37 2020

@author: xzl
"""

from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from datetime import datetime
import re


def tfidf(doc):
  tfidf_model = TfidfVectorizer(max_features=30, ngram_range=(1, 2),
                                stop_words=['具备','熟悉','熟练','出差','接受','善于','较强','精神','每周','实习','连续',
                                            '行业','五险','一金','地点','员工','优秀','优先','能力','快速','工作','项目',
                                            '业务','文档','客户','毕业生']).fit(doc)
  # ngram_range=(1,2)，max_df=0.5, token_pattern=r"(?u)\b\w+\b",
  size = tfidf_model.transform(doc)[0].data

  word_list=[]
  for k in tfidf_model.vocabulary_:
    word_list.append({'name': k, 'value': size[29 - tfidf_model.vocabulary_[k]]*1000})
    #print("{name: '", k, "',value:", size[29 - tfidf_model.vocabulary_[k]] * 1000, '},')
  return word_list


def result(name, region, time1, time2):
  jobs = {'产品经理': [re.compile(u'产品经理'), re.compile(u'产品助理'), re.compile(u'需求分析师')],
          '数据产品经理': [re.compile(u'数据产品')],
          '高级产品经理': [re.compile(u'高级产品经理')],
          '产品经理助理': [re.compile(u'产品经理助理'), re.compile(u'助理产品经理'), re.compile(u'产品助理')],
          '金融产品经理': [re.compile(u'金融产品经理'), re.compile(u'金融产品经理助理')],
          '电商产品经理': [re.compile(u'电商产品经理')],
          '售前产品经理': [re.compile(u'售前产品经理')],
          '策略产品经理': [re.compile(u'策略产品')],
          '软件产品经理': [re.compile(u'软件产品经理')],
          '法律产品经理': [re.compile(u'法律产品经理')],
          '需求分析师': [re.compile(u'需求分析师')]}
  connect = MongoClient(host='localhost', port=27017)
  db = connect['recruit']
  collection = db['info']

  doc = ['']
  count = 0
  if region == '全国':
    for record in collection.find({'name': {'$in': jobs[name]},
                                   'date': {'$lte': datetime.strptime(time2, '%Y/%m/%d'),
                                            '$gte': datetime.strptime(time1, '%Y/%m/%d')}}):
      doc[0] += record.get('tokens')
      count+=1
  else:
    for record in collection.find({'name': {'$in': jobs[name]}, 'place': re.compile(region), 'date': {'$lte': datetime.strptime(time2, '%Y/%m/%d'),
                                                                         '$gte': datetime.strptime(time1, '%Y/%m/%d')}}):
      # for record in collection.find({'name':{'$in':[re.compile(u'产品经理')]}}):
      doc[0] += record.get('tokens')
      count += 1
  word_cloud = tfidf(doc)
  return {'word_cloud': word_cloud, 'count': count}


