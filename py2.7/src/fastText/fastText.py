# coding:utf-8
__author__ = 'cluo'
import fasttext
import jieba
import argparse
import pymysql
import os
def add_company_name():
    conn = pymysql.connect(host='localhost', port=3306, user='geek', passwd='tomcat', db='infoadmin', charset='utf8')

    cursor = conn.cursor()

    sql = "select company_name,company_full_name from tcompany"

    cursor.execute(sql)
    fetchall = cursor.fetchall()
    for company in fetchall:
        jieba.add_word(company[0].encode('utf-8'),5,'nr')
        jieba.add_word(company[1].encode('utf-8'),5,'nr')
def train_model(train_data_path,model_output_path):
    #if os.path.exists(train_data_path+'.bin'):
    #    os.remove(train_data_path+'.bin')
    model = fasttext.supervised(train_data_path,model_output_path)
    return model
def parse_args():
    parse = argparse.ArgumentParser()
    parse.add_argument('--pattern', type=str, default="train")
    parse.add_argument('--context', type=str, default="")
    parse.add_argument('--train_data_path', type=str, default="")
    parse.add_argument('--data_path', type=str, default='./test.data')
    parse.add_argument('--model_path', type=str, default='./model.bin')
    parse.add_argument('--dict_path', type=str, default='./dict.data')
    parse.add_argument('--result_path', type=str, default='./result_path')
    parse.add_argument('--num', type=int, default=1)
    return parse.parse_args()
def predict(content,data_path,model_path,dict_path,result_path,k):
    add_company_name()
    texts = []
    if content.strip():
        texts = [" ".join(jieba.cut(content))]
    else:
        texts = [" ".join(jieba.cut(line)) for line in open(data_path)]
    model = fasttext.load_model(model_path)
    id2word = {}
    f = open(dict_path)
    for i in f.readlines():
        kv = i.split(",")
        id2word[kv[0]] = kv[1]
    result_list = model.predict_proba(texts,k)
    if os.path.exists(result_path):
        os.remove(result_path)
    result_file = open(result_path, 'a+')
    for line in result_list:
        for label in line:
            result_file.write(id2word[label[0].replace("__label__","")]+str(label[1])+'\n')
    result_file.close()
def main():
    args = parse_args()
    pattern = args.pattern
    if pattern.strip() == 'train':
        fasttext.supervised(args.train_data_path,args.model_path)
    if pattern.strip() == 'predict':
        predict(args.context,args.data_path,args.model_path,args.dict_path,args.result_path,args.num)
if __name__ == '__main__':
    main()
