__author__ = 'qiyuan zheng'
import json
import matplotlib.pyplot as plt
import dateutil.parser
import time
import re
import numpy as np
from twython import Twython
from collections import Counter

class RumorDetector:
    ####################################################################################################################
    #constructor
    #initialize and build up a twitter authentication
    ####################################################################################################################
    def __init__(self):
        CONSUMER_KEY = 'LpQbqdoMkDkSPDuXuiAic0vLn'
        CONSUMER_SECRET = 'knBDwraPNVL6KJOgKjtbAmCaSGexRtGM8qV9UkpuJEknX8z7Yf'
        ACCESS_KEY = '2316055658-oa6LuglzJiSY2ks5cov4DTxfk87WGb5thb8lPZ5'
        ACCESS_SECRET = 'OJvEfXDZpLEAtdVVIXIll8o6RzckBRo2Mo5vVTYZgyO7z'
        self.twitter = Twython(CONSUMER_KEY,CONSUMER_SECRET,ACCESS_KEY,ACCESS_SECRET)
        #a map between time to the tweets released
        self.time2tweet={}


    ####################################################################################################################
    #collectTweets
    #Now, we collect the historical tweets by fetching max 3200 tweets of a user
    #It's not a best solution
    ##TO DO: collect data within a long period
    ####################################################################################################################
    def collectTweets(self, user, file2BeWritten):
        #step1: get the first tweet
        user_timeline = self.twitter.get_user_timeline(screen_name=user,count=1)

        #step2: record the current latest id
        latest_id = user_timeline[0]['id']
        lis = [latest_id]

        #write the result into a file
        with open(file2BeWritten,'w+') as f:
            #since we can only get max 200 tweets once a time, we need iterate 16 times
            for i in range(0, 16):
                #iterate through all tweets
                #tweet extract method with the last list item as the max_id
                user_timeline = self.twitter.get_user_timeline(screen_name=user, count=200, max_id=lis[-1])
                for tweet in user_timeline:
                    #print the tweet
                    print tweet['text']

                    #append latest tweet id
                    lis.append(tweet['id'])

                    #convert the string of tweet into an object(json)
                    f.write(json.dumps(tweet))
                    f.write('\n')

                #5 minute rest between api calls
                time.sleep(300)


    ####################################################################################################################
    #findTweetsByKeyWords
    #find tweets that include specified keywords
    ####################################################################################################################
    def findTweetsByKeyWords(self, files, key_words):
        for file in files:
            tweet_objs = []

            #open a file and read tweet line by line
            with open(file, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    tweet_objs.append(json.loads(line))

            for tweet in tweet_objs:
                time = dateutil.parser.parse(tweet['created_at']).strftime("%Y-%m-%d")
                #only consider the November and October
                if not '2014-11' in time and not '2014-10' in time:
                    continue

                #lowerize
                lower_str = tweet['text'].lower()

                findit = True
                for k_word in key_words:
                    if not k_word in lower_str:
                        findit = False
                        break

                #if no key in the map, create a new one
                if not time in self.time2tweet:
                    self.time2tweet[time]= []

                #if ALL key words are in the tweet, collect the tweet
                if findit:
                    self.time2tweet[time].append(tweet)

        return sorted(self.time2tweet.items())


    ####################################################################################################################
    #getBurst
    #get the frequency distribution
    #seg: the segment of moving average
    ####################################################################################################################
    def getBurst(self, tweets, seg=10):
        counter = [len(tweet[1]) for tweet in tweets]
        return np.array(counter)


    ####################################################################################################################
    #getBurst
    #get the retweet count distribution
    #seg: the segment of moving average
    ####################################################################################################################
    def getRetweet(self, tweets,seg=10):
        counter = []
        for tweet in tweets:
            count = 0
            for tweet_obj in tweet[1]:
                count += tweet_obj['retweet_count']

            counter.append(count)

        return np.array(counter)


    ####################################################################################################################
    #plot_trend
    #plot a single trend
    ####################################################################################################################
    def plot_trend(self, x, y, title):
        plt.figure()
        plt.plot(y)
        plt.xticks(range(len(x))[::10], x[::10], rotation='90')
        plt.title(title)
        plt.show()


    ####################################################################################################################
    #plot_trends
    #plot multiple trends
    ####################################################################################################################
    def plot_trends(self,x, y1, y2, color1, color2, label1, label2):
        # Plot two trends with different y-scales
        fig, ax1 = plt.subplots()
        ax1.plot(y1, color1+'.-', label=label1)
        ax1.set_ylabel(label1, color=color1)
        plt.xticks(range(len(x))[::1], x[::1], rotation='90')
        ax2 = ax1.twinx()
        ax2.plot(y2, color2+'.-', label=label2)
        ax2.set_ylabel(label2, color=color2)
        plt.show()

    ####################################################################################################################
    #tokenize
    #tokenize a file
    #1. lowerize
    #2. remove 'http'
    #3. remove punctuation
    ####################################################################################################################
    def tokenize(self, file):
        wordCol = []
        with open(file, 'r') as f:
            for line in f.readlines():
                #filter http:
                if 'http' in line:
                   continue

                #lowerize
                lower_line = line.lower()

                #filter punctuation
                tokens = re.sub('\W+', ' ', lower_line).split()
                wordCol.extend(tokens)


        counter_sorted = sorted(Counter(wordCol).items(), key=lambda x: -x[1])

        with open('words.txt', 'w+') as f:
            for item in counter_sorted:
                f.write(item[0]+':'+str(item[1]))
                f.write('\n')

        print counter_sorted
        return counter_sorted


    ####################################################################################################################
    #export
    #save the tweets with key word into a file
    ####################################################################################################################
    def exportTweets(self):
        with open('result/result.txt', 'w+') as f:
            for time in self.time2tweet:
                for tweet in self.time2tweet[time]:
                    #convert an object into a string(json)
                    f.write(json.dumps(tweet))
                    f.write('\n')


    ####################################################################################################################
    #analyzeCorrection
    #distingguish correction from 'rumor'
    ####################################################################################################################
    def analyzeCorrection(self):
        #read rumor words
        print 'rumor words:'
        rumor_list = []
        with open('rumor_dic.txt', 'r') as f:
            for line in f.readlines():
                print line
                rumor_list.append(line)
        print '============================================'


        #read correction words
        print 'correction words:'
        correction_list = []
        with open('correction_dic.txt', 'r') as f:
            for line in f.readlines():
                print line
                correction_list.append(line)
        print '============================================'

        for time in self.time2tweet:
            for tweet in self.time2tweet[time]:
                #calculate the rumor score
                tweet['rumor_score'] = 0
                for rumor_word in rumor_list:
                    if rumor_word in tweet['text']:
                        tweet['rumor_score'] += 1
                for correction_word in correction_list:
                    if 'denies' in correction_word:
                        print 'haha'+ correction_word
                    if correction_word in tweet['text']:
                        tweet['rumor_score'] -= 1

        #record rumor result
        with open('result/rumors.txt', 'w+') as f:
            for time in self.time2tweet:
                for tweet in self.time2tweet[time]:
                    if tweet['rumor_score'] > 0:
                        print 'USER:%s' % tweet['user']['screen_name']
                        print 'CREATED AT:%s' % tweet['created_at']
                        print 'TWEET:%s' % tweet['text']

                        f.write('USER:' + tweet['user']['screen_name']+'\n')
                        f.write('CREATE AT:'+tweet['created_at']+'\n')
                        f.write('TWEET:'+tweet['text'])
                        f.write('\n==========================\n')

        #record correction result
        with open('result/correction.txt', 'w+') as f:
            for time in self.time2tweet:
                for tweet in self.time2tweet[time]:
                    if tweet['rumor_score'] < 0:
                        count = 1
                        print 'USER:%s' % tweet['user']['screen_name']
                        print 'CREATED AT:%s' % tweet['created_at']
                        print 'TWEET:%s' % tweet['text']

                        f.write('USER:' + tweet['user']['screen_name']+'\n')
                        f.write('CREATE AT:'+tweet['created_at']+'\n')
                        f.write('TWEET:'+tweet['text'])
                        f.write('\n==========================\n')

        correction = sorted(self.time2tweet.items())

        return correction

if __name__ == '__main__':
    rumor_detector = RumorDetector()
    #rumor_detector.collectTweets('alexweprin', 'tweet_alexweprin.txt')
    #Step1: find tweets by key words
    #keywords: laker, trade
    tweets = rumor_detector.findTweetsByKeyWords(['data/tweet_BryantJordan.txt', 'data/tweet_NBALivenews.txt', 'data/tweet_NBAFantacy.txt', 'data/tweet_InsideHoops.txt', 'data/tweet_NBARUMORS.txt', 'data/tweet_BestBballSwag.txt', 'data/tweet_LakerRumors.txt'], ['laker', 'trade'])

    ##keywords: laker, sign
    tweets = rumor_detector.findTweetsByKeyWords(['data/tweet_BryantJordan.txt', 'data/tweet_NBALivenews.txt', 'data/tweet_NBAFantacy.txt', 'data/tweet_InsideHoops.txt', 'data/tweet_NBARUMORS.txt', 'data/tweet_BestBballSwag.txt', 'data/tweet_LakerRumors.txt'], ['laker', 'sign'])

    ##keywords: laker, join
    tweets = rumor_detector.findTweetsByKeyWords(['data/tweet_BryantJordan.txt', 'data/tweet_NBALivenews.txt', 'data/tweet_NBAFantacy.txt', 'data/tweet_InsideHoops.txt', 'data/tweet_NBARUMORS.txt', 'data/tweet_BestBballSwag.txt', 'data/tweet_LakerRumors.txt'], ['laker', 'join'])
    #Step2: burst and retweet
    ##burst
    rumor__burst = rumor_detector.getBurst(tweets)

    ##retweet
    rumor_retweet = rumor_detector.getRetweet(tweets)

    #3export
    rumor_detector.exportTweets()

    #Step3: filter correction
    correction = rumor_detector.analyzeCorrection()

    #plot burst retweet

    rumor_detector.plot_trends([tweet[0] for tweet in tweets], rumor__burst, rumor_retweet, 'b', 'r', 'burst', 'retweet')

    #plot retweet correction
    x = []
    for cor in correction:
        if len(cor[1]) == 0:
            x.append(0)
        else:
            count = 0
            for tweet in cor[1]:
                if tweet['rumor_score'] < 0:
                    count = 1
            x.append(count)

    rumor_detector.plot_trends([tweet[0] for tweet in tweets], rumor_retweet, x, 'r', 'g', 'retweet', 'correction')
