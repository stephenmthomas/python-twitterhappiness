from __future__ import division
import json
import operator


#NOTE: some of these variables are tracked, but not reported or used
#and while this slows the code down just a LITTLE, efficiency isn't
#the priority here.  I've mostly used them for debugging.as

twit = [] #lines with valid tweets
twit_en = [] #Only tweets in English will be analyzed; a more refined approach would be to detect the
             #contents of the tweet to determine if it is actually in English, but using the "lang" tag
             #works for this method
twit_en_val = [] #corresponding list for twit_en sentiment values (one-for-one)
dat_count = 0 #lines analyzed
no_text = 0 #lines with no text; these are not tweets
no_eng = 0 #valid tweets that are NOT marked as English
no_loc = 0 #tweets with no location; should not be analyzed
in_us = 0 #tweets marked with the country_code 'US'
garb_loc = 0 #counts locations that do not fit the model paradigm

senti = {} #dictionary for sentiment values

states = {'AK': 'Alaska','AL': 'Alabama','AR': 'Arkansas','AZ': 'Arizona',
		'CA': 'California','CO': 'Colorado','CT': 'Connecticut',
		'DC': 'District of Columbia','DE': 'Delaware','FL': 'Florida','GA': 'Georgia',
		'GU': 'Guam','HI': 'Hawaii','IA': 'Iowa','ID': 'Idaho','IL': 'Illinois',
        'IN': 'Indiana','KS': 'Kansas','KY': 'Kentucky','LA': 'Louisiana',
        'MA': 'Massachusetts','MD': 'Maryland','ME': 'Maine','MI': 'Michigan',
        'MN': 'Minnesota','MO': 'Missouri','MS': 'Mississippi','MT': 'Montana',
		'NC': 'North Carolina','ND': 'North Dakota','NE': 'Nebraska',
        'NH': 'New Hampshire','NJ': 'New Jersey','NM': 'New Mexico','NV': 'Nevada',
        'NY': 'New York','OH': 'Ohio','OK': 'Oklahoma','OR': 'Oregon','PA': 'Pennsylvania',
		'RI': 'Rhode Island','SC': 'South Carolina','SD': 'South Dakota','TN': 'Tennessee',
        'TX': 'Texas','UT': 'Utah','VA': 'Virginia','VT': 'Vermont','WA': 'Washington',
        'WI': 'Wisconsin','WV': 'West Virginia','WY': 'Wyoming'}

scores = {'AK': 0,'AL': 0,'AR': 0,'AZ': 0,
		'CA': 0,'CO': 0,'CT': 0,'DC': 0,'DE': 0,
		'FL': 0,'GA': 0,'HI': 0,'IA': 0,'ID': 0,
		'IL': 0,'IN': 0,'KS': 0,'KY': 0,'LA': 0,
        'MA': 0,'MD': 0,'ME': 0,'MI': 0,'MN': 0,
		'MO': 0,'MS': 0,'MT': 0,'NC': 0,'ND': 0,
		'NE': 0,'NH': 0,'NJ': 0,'NM': 0,'NV': 0,
        'NY': 0,'OH': 0,'OK': 0,'OR': 0,'PA': 0,
		'RI': 0,'SC': 0,'SD': 0,'TN': 0,'TX': 0,
		'UT': 0,'VA': 0,'VT': 0,'WA': 0,'WI': 0,
		'WV': 0,'WY': 0}

def check_tweet(which):
    global no_text
    if 'text' not in which:
        no_text += 1
        return 0 #data is other than a tweet
    else:
        return 1 #data is a tweet

def check_lang(which):
    global no_eng
    tweet = json.loads(which)
    if 'lang' in tweet:
        if tweet['lang'] == "en":
            return 1 #tweet is in english
        else:
            no_eng += 1
            return 0

def build_dict():
    global senti
    sentdat = open("AFINN-111.txt")
    for lines in sentdat.read().split('\n'):
        line = lines.split('\t')
        senti[line[0]] = line[1]

def value_tweets():
    global senti, twit_en, twit_en_val
    for tweet in twit_en:
        cur_val = 0
        json_dat = json.loads(tweet, "utf-8")
        for word in json_dat['text'].split(' '):
            if word in senti:
                cur_val += int(senti[word])
        twit_en_val.append(cur_val)


print "Twitter Analysis Script using JSON\n"
print "Building Dictionary..."
build_dict()
print "Analyzing Twitter Data...\n"
twitdat = open("twitterData.txt")
tweets = twitdat.read().split('\n')

for twits in tweets:
    dat_count += 1
    if check_tweet(twits) == 1:
        twit.append(twits)

for twits in twit:
    if check_lang(twits) == 1:
        twit_en.append(twits)

print "Lines Analyzed: ", dat_count
print "Valid Tweets: ", (dat_count - no_text)
print "English Tweets: ", len(twit_en), "\n"

value_tweets()

print "Sentiment Values by Tweet Index:"
print twit_en_val
print "Average Sentiment Value: ", sum(twit_en_val) / len(twit_en_val)

print "\nAnalyzing State Happiness...\n"
for x in range(len(twit_en_val)):
    data = json.loads(twit[x], "utf-8")
    if 'place' in data:
        if data['place'] <> None:
            if data['place']['country_code'] == 'US':
                in_us += 1
                if 'full_name' in data['place']:
                    state = data['place']['full_name'].split(', ')
                    if state[1] in scores.keys():
                        scores[state[1]] += twit_en_val[x]
                    else:
                        garb_loc += 1

print "US Based Tweets with Garbage Location Data: ", garb_loc
happy_state = max(scores.iteritems(),key=operator.itemgetter(1))[0]
print "Happiest State:", states[happy_state]