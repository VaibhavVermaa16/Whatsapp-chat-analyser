from collections import Counter
import emoji
import emoji.unicode_codes
from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
import string
import re


def fetch_stats(selected_user, df):
    if selected_user=="Overall":
        return df.shape[0]
    else:
        return df[df['Sender']==selected_user].shape[0]

def fetch_words(selected_user, df):
    if selected_user=="Overall":
        words=[]
        for msg in df['Message']:
            words.extend(msg.split())
        return len(words)
    else:
        return df[df['Sender']==selected_user]['Message'].apply(lambda x: len(x.split())).sum()
    

def fetch_emojis(selected_user, df):
    emojis = []
    if(selected_user != "Overall"):
        df = df[df['Sender'] == selected_user]
    for msg in df['Message']:
        emojis.extend([c for c in msg if c in emoji.EMOJI_DATA])
    
    emoji_df = Counter(emojis)
    top_5_emojis = emoji_df.most_common(5)
    arr=[]
    for i in top_5_emojis:
        arr.extend(i[0])
    
    return len(emojis), arr

def media_shared(selected_user, df):
    if(selected_user != "Overall"):
        df = df[df['Sender'] == selected_user]
    return df[df['Message']=='<Media omitted>'].shape[0]

def links_shared(selected_user, df):
    if(selected_user != "Overall"):
        df = df[df['Sender'] == selected_user]
    
    extractor = URLExtract()
    urls=[]
    for msg in df['Message']:
        urls.extend(extractor.find_urls(msg))
    
    return len(urls)
    

def most_busy_user(df):
    x = df['Sender'].value_counts().head()
    sender_percentage = (df['Sender'].value_counts()/(df.shape[0]) * 100).round(2)
    sender_percentage=sender_percentage.reset_index()
    sender_percentage.rename(columns={'count':'Percent'}, inplace=True)
    return x, sender_percentage


def create_wordcloud(selected_user, df):
    if(selected_user != 'Overall'):
        df = df[df['Sender'] == selected_user]
        
    f=open('stop_hinglish.txt','r')
    stopWords=f.read()
    temp= df[df['Sender'] != 'group notification']
    temp = temp[temp['Message'] != '<Media omitted>']
    temp=temp[temp['Message'] != 'This message was deleted']
    temp=temp[temp['Sender']!='group_notification']
    
    def rem_stop_word(message):
        y=[]
        for word in message.lower().split():
            if word not in stopWords:
                y.append(word)
        return ' '.join(y)
    
    msg = temp['Message'].apply(rem_stop_word)
    
    wc= WordCloud(width=800, height=400, max_words=200, background_color='white', min_font_size=10)
    df_wc=wc.generate(msg.str.cat(sep=' '))
    return df_wc
    
    
def most_freq_words(selected_user, df):
    
    # Removing code in the messages
    
    if(selected_user != 'Overall'):
        df = df[df['Sender'] == selected_user]
     
    f=open('stop_hinglish.txt','r')
    stopWords=f.read()
    temp= df[df['Sender'] != 'group notification']
    temp = temp[temp['Message'] != '<Media omitted>']
    temp=temp[temp['Message'] != 'This message was deleted']
    temp=temp[temp['Sender']!='group_notification']
    
    translator = str.maketrans('', '', string.punctuation)
    
    words=[]
    translator = str.maketrans('', '', string.punctuation)
    for msg in temp['Message']:
            # Remove code in the messages
        msg = re.sub(r'```.*?```', '', msg, flags=re.DOTALL)
        for word in msg.lower().split():
            cleaned_word = word.translate(translator)
            if cleaned_word and cleaned_word not in stopWords:
                words.append(cleaned_word)
    data=Counter(words).most_common(20)
    data=pd.DataFrame(data, columns=['Word', 'count'])
    
    return data
    
def monthly_timeline(selected_user, df):
    if(selected_user != 'Overall'):
        df = df[df['Sender'] == selected_user]
        
    timeline = df[['year','month','date','Message']]    
    timeline['monthNum']=df['Date'].dt.month
    timeline=timeline.groupby(['month', 'year', 'monthNum']).count()['Message'].reset_index()
    time=[]
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i]+'-'+str(timeline['year'][i]))
    timeline['time']=time
    return timeline

def daily_timeline(selected_user, df):
    if(selected_user != 'Overall'):
        df = df[df['Sender'] == selected_user]
        
    data=df[['Date', 'Message']]
    data['Date']=data['Date'].dt.date
    data=data.groupby(['Date']).count()['Message'].reset_index()
    return data

def week_activity_map(selected_user, df):
    if(selected_user != 'Overall'):
        df = df[df['Sender'] == selected_user]
        
    return df['Day_name'].value_counts()

def month_activity_map(selected_user, df):
    if(selected_user != 'Overall'):
        df = df[df['Sender'] == selected_user]
        
    return df['month'].value_counts()

def activity_heatmap(selected_user, df):
    if(selected_user != 'Overall'):
        df = df[df['Sender'] == selected_user]
        
    # Combine 'Time' and 'AM/PM' into a single datetime column
    data1=df
    data1['Datetime'] = pd.to_datetime(df['Time'] + ' ' + df['Period'], format='%I:%M %p')

    # Create a column for 2-hour intervals
    data1['Interval_Start'] = data1['Datetime'].dt.floor('2H')
    data1['Interval_End'] = data1['Interval_Start'] + pd.Timedelta(hours=2)

    # Format the intervals as "HH:MM - HH:MM"
    data1['Interval'] = data1['Interval_Start'].dt.strftime('%H:%M') + ' - ' + df['Interval_End'].dt.strftime('%H:%M')

    # Group by the interval and count the messages
    data = data1[['Day_name','Interval','Message']]
    
    return data

        