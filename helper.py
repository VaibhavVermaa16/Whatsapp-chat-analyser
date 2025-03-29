from collections import Counter
import emoji
from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
import string
import re

def fetch_stats(selected_user, df):
    """Count total messages for selected user or overall"""
    if selected_user == "Overall":
        return df.shape[0]
    else:
        return df[df['Sender'] == selected_user].shape[0]

def fetch_words(selected_user, df):
    """Count total words for selected user or overall"""
    if selected_user == "Overall":
        words = []
        for msg in df['Message']:
            words.extend(str(msg).split())
        return len(words)
    else:
        return df[df['Sender'] == selected_user]['Message'].apply(
            lambda x: len(str(x).split())).sum()

def fetch_emojis(selected_user, df):
    """Count emojis and return top 5 for selected user"""
    emojis = []
    if selected_user != "Overall":
        df = df[df['Sender'] == selected_user]
    
    for msg in df['Message']:
        emojis.extend([c for c in str(msg) if c in emoji.EMOJI_DATA])
    
    emoji_counter = Counter(emojis)
    top_5_emojis = emoji_counter.most_common(5)
    top_emoji_list = [emoji[0] for emoji in top_5_emojis]
    
    return len(emojis), top_emoji_list

def media_shared(selected_user, df):
    """Count media files shared"""
    if selected_user != "Overall":
        df = df[df['Sender'] == selected_user]
    return df[df['Message'] == '<Media omitted>'].shape[0]

def links_shared(selected_user, df):
    """Count URLs shared in messages"""
    if selected_user != "Overall":
        df = df[df['Sender'] == selected_user]
    
    extractor = URLExtract()
    urls = []
    for msg in df['Message']:
        urls.extend(extractor.find_urls(str(msg)))
    
    return len(urls)

def most_busy_user(df):
    """Return top 5 active users and their percentage contribution"""
    top_users = df['Sender'].value_counts().head()
    user_percentage = round(df['Sender'].value_counts() / df.shape[0] * 100, 2)
    user_percentage = user_percentage.reset_index().rename(
        columns={'index': 'User', 'Sender': 'Percent'})
    return top_users, user_percentage

def create_wordcloud(selected_user, df):
    """Generate word cloud from messages"""
    if selected_user != 'Overall':
        df = df[df['Sender'] == selected_user]
    
    # Load stop words
    with open('stop_hinglish.txt', 'r') as f:
        stop_words = f.read().split('\n')
    
    # Filter data
    temp = df[(df['Sender'] != 'group notification') & 
              (df['Message'] != '<Media omitted>') &
              (df['Message'] != 'This message was deleted')]
    
    def clean_message(message):
        words = [word for word in str(message).lower().split() 
                if word not in stop_words and word.strip()]
        return ' '.join(words)
    
    cleaned_messages = temp['Message'].apply(clean_message)
    
    wc = WordCloud(width=800, height=400, max_words=200, 
                  background_color='white', min_font_size=10)
    wordcloud = wc.generate(' '.join(cleaned_messages))
    return wordcloud

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
    """Generate monthly message count timeline"""
    if selected_user != 'Overall':
        df = df[df['Sender'] == selected_user]
    
    timeline = df[['year', 'month', 'Message']].copy()
    timeline['month_num'] = df['DateTime'].dt.month
    
    timeline = timeline.groupby(['year', 'month', 'month_num']).count().reset_index()
    timeline['time'] = timeline['month'] + '-' + timeline['year'].astype(str)
    
    return timeline.sort_values(['year', 'month_num'])

def daily_timeline(selected_user, df):
    """Generate daily message count timeline"""
    if selected_user != 'Overall':
        df = df[df['Sender'] == selected_user]
    
    daily_data = df.groupby('date').count()['Message'].reset_index()
    daily_data.rename(columns={'date': 'Date', 'Message': 'Count'})
    return daily_data

def week_activity_map(selected_user, df):
    """Count messages by day of week"""
    if selected_user != 'Overall':
        df = df[df['Sender'] == selected_user]
    return df['day_name'].value_counts()

def month_activity_map(selected_user, df):
    """Count messages by month"""
    if selected_user != 'Overall':
        df = df[df['Sender'] == selected_user]
    return df['month'].value_counts()

# def activity_heatmap(selected_user, df):
#     if selected_user != 'Overall':
#         df = df[df['Sender'] == selected_user]
    
#     # Clean 'Time' and 'Period' columns
#     df['Time'] = df['Time'].str.strip()  # Remove leading/trailing spaces
#     df['Period'] = df['Period'].str.strip().str.upper()  # Ensure AM/PM is uppercase and clean

#     # Combine 'Time' and 'Period' into a single datetime column
#     try:
#         df['Datetime'] = pd.to_datetime(df['Time'] + ' ' + df['Period'], format='%I:%M %p', errors='coerce')
#     except Exception as e:
#         raise ValueError(f"Error parsing datetime: {e}")

#     # Drop rows with invalid datetime values
#     df = df.dropna(subset=['Datetime'])

#     # Create a column for 2-hour intervals
#     df['Interval_Start'] = df['Datetime'].dt.floor('2H')
#     df['Interval_End'] = df['Interval_Start'] + pd.Timedelta(hours=2)

#     # Format the intervals as "HH:MM - HH:MM"
#     df['Interval'] = df['Interval_Start'].dt.strftime('%H:%M') + ' - ' + df['Interval_End'].dt.strftime('%H:%M')

#     # Group by the interval and count the messages
#     data = df[['day_name', 'Interval', 'Message']]

#     return data
