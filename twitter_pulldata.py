import tweepy
#import csv
#import pandas as pd
import time
import datetime
import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import requests
import json

####input your credentials here
access_token = 'your-token'
access_token_secret= 'your-token-secret'
consumer_key = 'your-key'
consumer_secret = 'your-secret'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth,wait_on_rate_limit=True)
#####United Airlines
# Open/Create a file to append data
#csvFile = open('ipl.csv', 'a')
#Use csv Writer
#csvWriter = csv.writer(csvFile)
url = "http://localhost:12201/gelf"

headers = {
    'content-type': "application/json"
    }

sid = SentimentIntensityAnalyzer()
lang=["java", "c#", "javascript", "php", "python", "ruby", "swift", "c++", "angular js", "react js", "node js", "golang", "matlab","html","css",".net"]
max_id=-1L
tweetCount=0
sinceId=None
tweetsPerQry = 100
maxTweets =30000000
searchQuery='#blockchain'

while tweetCount < maxTweets:
    try:
        if(max_id<=0):
            if (not sinceId):
                new_tweets=api.search(q=searchQuery, count=tweetsPerQry)
            else:
                new_tweets= api.search(q=searchQuery, count=tweetsPerQry,since_id=sinceId)
        else:
            if (not sinceId):
                new_tweets = api.search(q=searchQuery, count=tweetsPerQry,max_id=str(max_id - 1))
            else:
                new_tweets = api.search(q=searchQuery, count=tweetsPerQry,max_id=str(max_id - 1),since_id=sinceId)
        if not new_tweets:
            print "No more tweets found"
            break
        for tweet in new_tweets:
            res_json= {"message":"bigdata","type":searchQuery[1:]}
            tweet_text=tweet.text.encode('utf-8')
            res_json["tweet"]= tweet_text
            tweet_time= str(tweet.created_at)
            unix_timestamp= time.mktime(datetime.datetime.strptime(tweet_time, "%Y-%m-%d %H:%M:%S").timetuple())
            res_json["timestamp"]= unix_timestamp
            tweet_user=re.findall(r'[@]\w+',tweet_text)
            tweet_topic= re.findall(r'[#]\w+',tweet_text)
            if len(tweet_user)>0:
                res_json["user"]=tweet_user 
            if len(tweet_topic)>0:
                res_json["topics"]=tweet_topic[0] 
            lang_found=[]
            for l in lang:
                if l in tweet_text.lower():
                    lang_found.append(l)
            if len(lang_found)>0:
                res_json["language"]= lang_found[0]
            ss = sid.polarity_scores(tweet_text)
            res_json["positive"]=ss['pos']
            res_json["negative"]=ss['neg']
            res_json["neutral"]= ss['neu']
            lst=[res_json["positive"],res_json["negative"],res_json["neutral"]]
            max_s=max(lst)
            if max_s==res_json["positive"]:
                res_json["sentiment"]="positive"
            elif max_s==res_json["negative"]:
                res_json["sentiment"]="negative"
            elif max_s==res_json["neutral"] and max_s>0.9:
                res_json["sentiment"]="neutral"
            else:
                if res_json["positive"]>res_json['negative']:
                    res_json["sentiment"]="positive"
                else:
                    res_json["sentiment"]="negative"

            res_json["isretweeted"]= tweet_text.startswith('RT')
            res_json["retweet_count"]= tweet.retweet_count
            res_json["favourite_count"]= tweet.favorite_count
            #csvWriter.writerow([tweet.created_at, tweet.text.encode('utf-8')])
            response = requests.request("POST", url, data=json.dumps(res_json), headers=headers)

        tweetCount += len(new_tweets)
        max_id = new_tweets[-1].id
    except tweepy.TweepError as e:
        print str(e)
        break


