import re
import pandas as pd

def preprocess(data):
    # Regular expression pattern to match the date, time, and am/pm
    pattern = r'(\d{1,2}/\d{1,2}/\d{2}), (\d{1,2}:\d{2})\s?[^\S\r\n]*([ap]m) - (.*?): '

    # Lists to hold the extracted data
    dates = []
    times = []
    periods = []
    senders = []
    messages = []

    # Temporary variables to handle multiline messages
    current_message = ""
    current_date = ""
    current_time = ""
    current_period = ""
    current_sender = ""

    # Process the dataset
    for line in data.split('\n'):
        match = re.match(pattern, line)
        if match:
            if current_message:  # Save the previous message if there is one
                messages.append(current_message.strip())
            
            # Extract new date, time, period, and sender
            current_date = match.group(1)
            current_time = match.group(2)
            current_period = match.group(3)
            current_sender = match.group(4)
            
            # Append the date, time, and sender to their respective lists
            dates.append(current_date)
            times.append(current_time)
            periods.append(current_period)
            senders.append(current_sender)
            
            # Start a new message
            current_message = line[match.end():].strip()
        else:
            # Continuation of the previous message
            current_message += "\n" + line.strip()

    # Append the last message
    if current_message:
        messages.append(current_message.strip())

    # Debugging: print lengths of all lists
    messages.pop()
    print(f"Lengths -> Dates: {len(dates)}, Times: {len(times)}, Periods: {len(periods)}, Senders: {len(senders)}, Messages: {len(messages)}")
    # Create the DataFrame
    df = pd.DataFrame({
        'Date': dates,
        'Time': times,
        'Period': periods,
        'Sender': senders,
        'Message': messages
    })

    df=df[1:]
    df['Date']=pd.to_datetime(df['Date'], format='%d/%m/%y')
    df['year']=df['Date'].dt.year
    df['month']=df['Date'].dt.month_name()
    df['date'] = df['Date'].dt.day
    df['time']=pd.to_datetime(df['Time'], format='%H:%M')
    df['hour']=df['time'].dt.hour
    df['min']=df['time'].dt.minute
    df['time']=df['time'].dt.time
    df['Day_name']=df['Date'].dt.day_name()
    return df
