"""
download top 5 daily news articles through searching
the stock ticker in Google news 
"""

import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import time
from datetime import timedelta,date, datetime
from newspaper import Article
from newspaper import Config
import csv
from csv import DictWriter
import Gen_header
from Gen_header import random_header
import requests
from random import randrange
from collections import OrderedDict
from bs4 import BeautifulSoup
import os.path

def generate_date_range(start, end):     
    """Generate dates in a range"""
    return [start + timedelta(n) for n in range(int((end - start).days))]

def collect_news(keyword, search_date):
    """collect news through webpage scraping"""
    config = Config()
    user_agent= random_header()['User-Agent']
    config.browser_user_agent = user_agent
    config.request_timeout = 10
    
    # save the ticker name/ search keyword in a variable
    search_keyword = keyword.replace(' ','+')
    search_date = search_date.strftime('%m-%d-%Y')
    # set query for google
    query = '{}'.format(search_keyword)
    baseurl = f"https://www.google.com/search?q={query}&tbm=nws&lr=lang_en&hl=en&num=5"
    url = baseurl + '&source=lnt&tbs=lr%3Alang_1en%2Ccdr%3A1%2' + \
         'Ccd_min%3A' + search_date[:2]+ '%2F' + search_date[3:5] + '%2F' + search_date[6:] + '%2Ccd_max%3A' +\
         search_date[:2]+ '%2F' + search_date[3:5] + '%2F' + search_date[6:]
    #print(url)
    
    i = 0
    loop_flag = True
    news_link = []
    # when the server is unresponsive, try the server ten times
    while loop_flag and i <= 10:
        r = requests.Session()
        headers = random_header()
        r.headers = headers
        res = r.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        cd_min = search_date[:2] + '/' + search_date[3:5] + '/' + search_date[6:]
        for links in soup.find_all('a', href=True):
            raw_link = links['href']
            #TODO, hard-coded for now
            if 'https://' in raw_link  and 'google' not in raw_link:
                if '/url?esrc' not in raw_link:
                    news_link.append(raw_link)
                    loop_flag = False
                    #print(raw_link)
                else:
                    i += 1
                    time.sleep(randrange(10,28,1))
                    print('fail to get the data for ', search_date)
        

    try:
        list =[] #creating an empty list 
        for i in range(len(news_link)):
            dict = {} #creating an empty dictionary to append an article in every single iteration
            article = Article(news_link[i],config=config) #providing the link
            try:
                article.download() #downloading the article 
                article.parse() #parsing the article
                article.nlp() #performing nlp to get summary
            except:
                pass 
            #storin results in the dictionary
            dict['Date']=search_date
            dict['Title']=article.title
            dict['Article']=article.text
            dict['Summary']=article.summary
            dict['Key_words']=article.keywords
            dict['Datetime'] = article.publish_date
            dict['Link'] = news_link[i]
            list.append(dict)
        #check_empty = not any(list)
        news_df=pd.DataFrame(list) #creating dataframe
        print(news_df['Date'][0])

    except Exception as e:
        #exception handling
        print("exception occurred:" + str(e))
        print('there is probably some error in retrieving the data, Please try again or try with a different keyword.' )
        pass
    return news_df

with open("newsarticle_amazon_2018.csv", "w") as my_empty_csv:
    # create an empty file 
    pass 
article_list =[] #creating an empty list 
search_keyword = 'AMZN'  # can use ticker name for individual stocks
for date in generate_date_range(date(2019, 1, 1), date(2021, 1, 1)):
    df_news = collect_news(search_keyword, date)
    for i in df_news.index:
        dict = {} #creating an empty dictionary to append an article in every single iteration
        dict['Date']=df_news['Date'][i] 
        dict['Summary']=df_news['Summary'][i]
        dict['Title'] = df_news['Title'][i]
        dict['Article'] = df_news['Article'][i]
        dict['Link'] = df_news['Link'][i]
        article_list.append(dict)
        #appending more data for other years
        with open('newsarticle_amazon_2018.csv', 'a') as f_object:  
            header = ['Date','Summary','Title','Article','Link']
            writer = csv.DictWriter(f_object, delimiter = ',', fieldnames=header)
            writer.writerow(dict)
    time.sleep(randrange(8))



