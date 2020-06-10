# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 15:45:25 2020

@author: xzl
"""
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from datetime import datetime
import re


def tfidf(doc):
  tfidf_model = TfidfVectorizer(max_features=25, ngram_range=(1, 2),
                                stop_words=['具备', '熟悉', '熟练', '出差', '接受', '善于', '较强', '精神', '每周', '实习', '连续', '行业',
                                            '五险', '一金', '地点', '员工', '优秀', '优先', '能力', '快速', '工作', '项目', '业务', '文档',
                                            '客户', '毕业生', '应届', '工具']).fit(
    doc)  # ngram_range=(1,2)，max_df=0.5, token_pattern=r"(?u)\b\w+\b",
  #print(tfidf_model.vocabulary_)
  # print(tfidf_model.transform(doc)[0].data)
  # print(tfidf_model.transform(doc)[0].indices)
  word_dict = []
  for k in sorted(tfidf_model.vocabulary_):
    word_dict.append(k)
  #print(word_dict)
  job_dict = [[], [], [], [], [], [], [], [], [], []]
  for i in range(10):
    for it in tfidf_model.transform(doc)[i].indices:
      job_dict[i].append(word_dict[it])
  #print(job_dict)

  fliterNode = []
  jobs = ['数据产品经理', '高级产品经理', '产品经理助理', '金融产品经理', '电商产品经理', '售前产品经理', '策略产品经理', '软件产品经理', '法律产品经理', '需求分析师']
  n = 0
  for job in jobs:
    fliterNode.append({'id': str(n), 'name': job, 'itemStyle': None, 'symbolSize': len(job_dict[n])+20,
                       'attributes': {'modularity_class': 0}, 'value': len(job_dict[n]), 'label': {'normal': {'show': False}},
                       'category': 0})
    n += 1
  for k in word_dict:
    num = 0
    for it in job_dict:
      if k in it:
        num += 1
    fliterNode.append({'id': str(n), 'name': k, 'itemStyle': None, 'symbolSize': num+20,
                       'attributes': {'modularity_class': 0}, 'value': num, 'label': {'normal': {'show': False}}, 'category': 1})
    n += 1

  link = []
  n = 0
  for job in jobs:
    for it in job_dict[n]:
      link.append({'source': str(n), 'target': str(tfidf_model.vocabulary_[it]+10)})
    n += 1

  return {'fliterNode': fliterNode, 'link': link}


def result(region, time1, time2):
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

  doc = ['', '', '', '', '', '', '', '', '', '']
  count_all = 0
  it = 0
  for job in jobs:
    if job == '产品经理':
      continue
    if region == '全国':
      for record in collection.find({'name': {'$in': jobs[job]}, 'date': {'$lte': datetime.strptime(time2, '%Y/%m/%d'),
                                                                          '$gte': datetime.strptime(time1,
                                                                                                    '%Y/%m/%d')}}):
        doc[it] += record.get('tokens')
        count_all += 1
    else:
      for record in collection.find({'name': {'$in': jobs[job]}, 'place': re.compile(region),
                                     'date': {'$lte': datetime.strptime(time2, '%Y/%m/%d'),
                                              '$gte': datetime.strptime(time1, '%Y/%m/%d')}}):
        doc[it] += record.get('tokens')
        count_all += 1
    it += 1
  res = tfidf(doc)
  return {'fliterNode': res['fliterNode'], 'count_all': count_all, 'link': res['link']}

