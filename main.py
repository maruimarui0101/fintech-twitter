from twitter_extract import TwitterClient, TweetAnalyzer,  collection
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd 

if __name__ == "__main__":
    
    twitter_account_list = ['Get_Chip', 'monzo']

    # starting date to filter out the tweets (1st Jan 2019)
    start_date = datetime(2019,1,1,0,0,0)

    fig, axes = plt.subplots(len(twitter_account_list), 1, figsize=(16,8))

    # iterating through each account name 

    for idx, account in enumerate(twitter_account_list):
        twitter_client = TwitterClient(account)
        tweet_analyzer = TweetAnalyzer()
        approved_tweets = []
        tweets = twitter_client.get_user_timeline_tweets()

        for tweet in tweets:
            if tweet.created_at >= start_date:
                approved_tweets.append(tweet)
        df = tweet_analyzer.tweets_to_data_frame(approved_tweets)
        df.to_csv('{}.csv'.format(account), index=None)

        time_likes = pd.Series(data=df['likes'].values, index=df['date'])
        time_retweets = pd.Series(data=df['retweets'].values, index=df['date'])
        axes[idx].set_title('@' + account)
        axes[idx].plot(df['date'], df['retweets'], label='retweets')
        axes[idx].plot(df['date'], df['likes'], label='likes')
        axes[idx].legend(loc="upper right")

        store = df.head().T.to_dict().values()
        collection.insert_many(store)

    plt.tight_layout()
    plt.savefig('chip_twitter_extract.png')