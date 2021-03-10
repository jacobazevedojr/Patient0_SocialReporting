import tweepy
import simplejson as json
import csv


class TwitterParse:

    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        self.api = self.loadAuth(consumer_key, consumer_secret, access_token, access_token_secret)

    # This function uploads credentials for authorization to use the API
    def loadAuth(self, consumer_key, consumer_secret, access_token, access_token_secret):

        # Upload credentials into authorization for Twitter
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        tempAPI = tweepy.API(auth)

        try:
            tempAPI.verify_credentials()
            print("Verified")
            return tempAPI
        except:
            print("Error during authentication")

        return None

    # This function will gather the relevant tweets and store the information for later processing
    def gatherData(self, searchStrings, storageFile):
        # Request all tweets matching every string in the searchString list
        # (should be more sophisticated later to search for more telling information)
        # e.g. Searching for the word "sick" and "sneeze" separately may return tweets
        # that aren't as telling as tweets containing "feeling snick and sneezing"

        # Aggregate of individual word searches
        try:
            csvFile = open(storageFile, "a", encoding="utf-8")
            dictList = []
            totalTweets = 0
            colSet = set()
            for search in searchStrings:
                moreTweetsExist = True
                while(moreTweetsExist):
                    currentID = 0
                    # Receive matching tweets from Twitter
                    # search(queryString, [geocode], [lang], [locale], [result_type] ("mixed", "recent", "popular"), [count],
                    # [until] ("YYYY-MM-DD" 7-day limit), [since_id], [max_id], [include_entities]
                    #, since_id=currentID
                    tweets = self.api.search(search, lang="en", count=1000)
                    totalTweets += len(tweets)
                    if len(tweets) == 0:
                        moreTweetsExist = False
                    for i, tweet in enumerate(tweets):
                        # Format tweet for better reading
                        formattedTweet = json.dumps(tweet._json, indent=4, sort_keys=True)
                        # Convert to Python dict
                        dictTweet = json.loads(formattedTweet)
                        dictList.append(dictTweet)
                        if dictTweet["geo"] is not None:
                            if dictTweet["geo"]["coordinates"] is not None:
                                print(search)
                                print(dictTweet["geo"]["coordinates"])
                        if dictTweet["place"] is not None:
                            print(search)
                            print(dictTweet["place"])
                        # Store dict in csv
                        for key in dictTweet:
                            if key not in colSet:
                                colSet.add(key)
                        if i == len(tweets):
                            currentID = dictTweet['id']

                        moreTweetsExist = False

            csv_columns = []
            for item in colSet:
                csv_columns.append(item)
            writer = csv.DictWriter(csvFile, fieldnames=csv_columns)
            writer.writeheader()
            for data in dictList:
                writer.writerow(data)
            csvFile.close()
        except IOError:
            print("I/O error")

    # Read txt file (passed as file path string) with each line corresponding to a search query keyword
    def getSearchString(self, relevantWordsFile):
        read = open(relevantWordsFile, 'r')
        searchStrings = read.readlines()
        read.close()

        return searchStrings

    def drive(self, searchDoc, archive):
        searchStrings = self.getSearchString(searchDoc)
        self.gatherData(searchStrings, archive)
