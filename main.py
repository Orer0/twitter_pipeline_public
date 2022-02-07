import requests
import pandas as pd
import pygsheets

BEARER_TOKEN = YOUR_BEARER_TOKEN

target_people = ['elonmusk',
                  'JeffBezos',
                  'ylecun',
                  'BarackObama',
                  'KimKardashian',
                  'Cristiano',
                  'rihanna',
                  'PlayStation',
                  '42born2code',
                  'justinbieber'
                ]

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {BEARER_TOKEN}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def write_in_sheet(sheet_name, data):
    #authorization
    gc = pygsheets.authorize(service_file='drive_creds.json')

    # Create empty dataframe
    df = pd.DataFrame.from_dict(data)

    #open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
    sh = gc.open(sheet_name)

    #select the first sheet 
    wks = sh[0]
    cells = wks.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')
    last_row = len(cells)

    #For hanlde sheet size problem
    wks.rows = last_row + 1000

    if last_row <= 1: 
        wks.set_dataframe(df,(1,1))
    else:
        wks.set_dataframe(df,(last_row + 1,1), copy_head=False)

def run_query(user_lookup, query_params_user):
    return requests.get(user_lookup, auth=bearer_oauth, params=query_params_user).json()['data']

def get_user_data():
    #Build User table
    final_dict = {
        'created_at' : [],
        'name' : [],
        'username' : [],
        'id': [],
        'description' : [],
        'followers_count' : [],
        'following_count' : [],
        'listed_count' : [],
        'tweet_count' : []
    }

    for username in target_people:
        user_lookup = 'https://api.twitter.com/2/users/by/username/%s' %username
        query_params_user = {'user.fields':'id,created_at,description,location,public_metrics,username'}
        user_response = run_query(user_lookup, query_params_user)

        final_dict['created_at'].append(user_response['created_at'])
        final_dict['name'].append(user_response['name'])
        final_dict['username'].append(user_response['username'])
        final_dict['id'].append(user_response['id'])
        final_dict['description'].append(user_response['description'])
        final_dict['followers_count'].append(user_response['public_metrics']['followers_count'])
        final_dict['following_count'].append(user_response['public_metrics']['following_count'])
        final_dict['listed_count'].append(user_response['public_metrics']['listed_count'])
        final_dict['tweet_count'].append(user_response['public_metrics']['tweet_count'])
    return final_dict


def get_tweets_user(user_data):
    final_dict_tweet = {
        'user_id' : [],
        'created_at' : [],
        'tweet_id' : [],
        'lang' : [],
        'text' : [],
        'like_count' : [],
        'quote_count' : [],
        'reply_count' : [],
        'retweet_count' : [],
        'source' : []
    }

    for id in user_data['id']:
        tweets_user = 'https://api.twitter.com/2/users/%s/tweets'%id
        query_params_tweet = {'max_results':100,
                            'tweet.fields':'author_id,created_at,id,lang,public_metrics,source,text',
                            'exclude':'retweets,replies'}
        tweets_response = run_query(tweets_user, query_params_tweet)

        for tweet in tweets_response:
            final_dict_tweet['user_id'].append(tweet['author_id'])
            final_dict_tweet['created_at'].append(tweet['created_at'])
            final_dict_tweet['tweet_id'].append(tweet['id'])
            final_dict_tweet['lang'].append(tweet['lang'])
            final_dict_tweet['text'].append(tweet['text'])
            final_dict_tweet['like_count'].append(tweet['public_metrics']['like_count'])
            final_dict_tweet['quote_count'].append(tweet['public_metrics']['quote_count'])
            final_dict_tweet['reply_count'].append(tweet['public_metrics']['reply_count'])
            final_dict_tweet['retweet_count'].append(tweet['public_metrics']['retweet_count'])
            final_dict_tweet['source'].append(tweet['source'])
    return final_dict_tweet

def get_twitter_data_source(event, context):
  user_data = get_user_data()
  tweets_data = get_tweets_user(user_data)

  write_in_sheet('twitter_users', user_data)
  write_in_sheet('twitter_tweets', tweets_data)