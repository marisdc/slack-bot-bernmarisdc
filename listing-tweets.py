from tweepy import API
from tweepy import OAuthHandler

consumer_key = 'vy88mDepUBvRc5u5iNITUixie'
consumer_secret = 'W5qR6wtKqQHIjflzCn1RKEk62k3CVcjyGe7YbvQTexEYGeLuGF'
access_token = '1022094482282491904-Zf0hXNyUK5AYOgOpnNmfwiL8R2QZqa'
access_token_secret = 'MHpuz0wGWuxCzTnbBvKLbQFB1j4L2gfAqnvGBAjDLtpX1'

auth = OAuthHandler(consumer_key,consumer_secret)
auth.set_access_token(access_token,access_token_secret)
api = API(auth)

top_tweets = api.trends_place(1)

import json
new_tweets = json.dumps(top_tweets, indent=4, sort_keys=True)
new_tweets = json.loads(new_tweets)
tweet_dict = new_tweets[0]

top = tweet_dict['trends']
container = []
response = ''
instr = []
top10 = 10

for x in top:
        if x['tweet_volume'] >= 0:
            container.append([x['tweet_volume'], x['name']])
        container.sort(reverse=True)
        ctr = 1

        for y in container:
            if ctr <= top10:
                instr += str(ctr)+'. ' + y[1] + "\n"
                ctr += 1
            else:
                break


