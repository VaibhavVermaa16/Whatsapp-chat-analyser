import re
import pandas as pd
from datetime import datetime

def clean_time_string(time_str):
    """Clean and standardize time strings before parsing."""
    # Replace special whitespace characters with regular space
    time_str = re.sub(r'[\xa0\u202f]', ' ', time_str)
    # Remove leading/trailing spaces
    time_str = time_str.strip()
    # Ensure AM/PM is uppercase with no space before it
    time_str = re.sub(r'(\d)\s*([APap][mM])', r'\1 \2', time_str)
    return time_str

def convert_to_datetime(date_str):
    """Converts a date string to datetime, handling WhatsApp date formats."""
    if pd.isna(date_str):
        return pd.NaT
    
    date_str = str(date_str).strip()
    date_str = re.sub(r'[\xa0\u202f]', ' ', date_str)  # Replace special whitespace
    
    try:
        # Try parsing with dayfirst=True (for dd/mm/yyyy)
        return pd.to_datetime(date_str, dayfirst=True, errors='raise')
    except ValueError:
        try:
            # Try parsing with monthfirst=True (for mm/dd/yyyy)
            return pd.to_datetime(date_str, monthfirst=True, errors='raise')
        except ValueError:
            return pd.NaT

def preprocess(data):
    # Regular expression pattern to match the date, time, and am/pm
    pattern = r'^(\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}\s?[APap][mM]\b)\s*-\s*(.+?):\s*(.*)$'
    
    # Lists to hold extracted data
    datetimes = []
    times = []
    periods = []
    senders = []
    messages = []
    current_message = ""

    for line in data.split('\n'):
        match = re.match(pattern, line)
        if match:
            if current_message:
                messages.append(current_message.strip())
            
            # Extract date-time and clean it
            datetime_str = match.group(1)
            datetime_str = clean_time_string(datetime_str)
            
            datetimes.append(datetime_str)
            
            # Extract time components
            time_part = datetime_str.split(', ')[1]
            time_part = clean_time_string(time_part)
            times.append(time_part)
            
            # Extract period (AM/PM)
            period = re.search(r'([APap][mM])', time_part)
            periods.append(period.group(0).upper() if period else '')
            
            senders.append(match.group(2))
            current_message = match.group(3)
        elif line.strip():
            # Handle multiline messages
            current_message += ' ' + line.strip()

    # Append the last message
    if current_message:
        messages.append(current_message.strip())

    # Create DataFrame
    df = pd.DataFrame({
        'DateTime': datetimes,
        'Time': times,
        'Period': periods,
        'Sender': senders,
        'Message': messages[:len(datetimes)]
    })
    
    # Convert to datetime with error handling
    df['DateTime'] = df['DateTime'].apply(convert_to_datetime)
    
    # Extract datetime components - NOTE THE COLUMN NAMES HERE
    df['year'] = df['DateTime'].dt.year
    df['month'] = df['DateTime'].dt.month_name()
    df['date'] = df['DateTime'].dt.day  # Changed from 'day' to 'date' to match your expectation
    df['hour'] = df['DateTime'].dt.hour
    df['minute'] = df['DateTime'].dt.minute
    df['day_name'] = df['DateTime'].dt.day_name()
    
    # Clean up the Time column
    df['Time'] = df['Time'].apply(clean_time_string)
    
    return df.dropna(subset=['DateTime'])