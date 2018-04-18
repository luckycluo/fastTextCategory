# coding:utf-8
__author__ = 'cluo'
import jieba
import re
import argparse
import os
import pymysql
#获取公司关键词，加入分词字典里面
def add_company_name():
    conn = pymysql.connect(host='localhost', port=3306, user='geek', passwd='tomcat', db='infoadmin', charset='utf8')

    cursor = conn.cursor()

    sql = "select company_name,company_full_name from tcompany"

    cursor.execute(sql)
    fetchall = cursor.fetchall()
    for company in fetchall:
        jieba.add_word(company[0].encode('utf-8'),5,'nr')
        jieba.add_word(company[1].encode('utf-8'),5,'nr')
#解析传入参数
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default='./raw_data')#原始数据，一篇文章为一行
    parser.add_argument('--output', type=str, default='./parse_data')#解析后fastText的训练数据
    parser.add_argument('--stopwords', type=str, default='./stopwords')#过滤词文件
    parser.add_argument('--word2id', type=str, default='./word2id')#解析后的word2id字典
    parser.add_argument('--dict', type=str, default='')#结巴分词字典（可以自己爬取百度百科做成字典，提高分词的效果）
    return parser.parse_args()
#解析文章数据
def parse_data(input_path,output_path,stopwords,word2id):
    stop_words = []
    label_dict = {}
    label_prefix = '__label__'
    f1 = open(stopwords,'r')
    for stopword in f1.readlines():
        if stopword:
            stop_words.append(stopword.decode('utf-8').strip())
    f1.close()
    dr = re.compile(r'<[^>]+>',re.S)
    num = 0
    if os.path.exists(output_path):
        os.remove(output_path)
    if os.path.exists(word2id):
        os.remove(word2id)
    with open(input_path,'r') as f2:
        for i in f2.readlines():
            kv = i.split('\001')
            if(len(kv)==2):
                content = kv[0]
                labels = set(kv[1].split('\002'))
                content = dr.sub('',content)
                words = jieba.cut(content)
                result_words = [word for word in words if word not in stop_words]
                cut_words = " ".join(result_words)
    #             print labels
                if cut_words.strip():
                    for label in labels:
                        label = label.strip()
                        if label:
                            number_label = 0
                            if label in label_dict.keys():
                                number_label = label_dict[label]
                            else:
                                num += 1
                                number_label = num
                                label_dict[label] = num
                            with open(output_path,'a+') as f3:
                                write_line = (label_prefix + str(number_label) + ' , ' + cut_words).encode('utf-8')
                                f3.write(write_line+'\n')
    f4 = open(word2id,'a+')
    for key in label_dict.keys():
        if key.strip():
            line = (str(label_dict[key]) + ',' + key.decode('utf-8')).encode('utf-8')
            f4.write(line+'\n')
    f2.close()
    f3.close()
    f4.close()
if __name__ =='__main__':
    args = parse_args()
    dict_path = args.dict
    if dict_path:
        jieba.load_userdict(dict_path)
    add_company_name()
    parse_data(args.input,args.output,args.stopwords,args.word2id)

