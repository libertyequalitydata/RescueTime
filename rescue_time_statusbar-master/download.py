# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.6.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import requests
import os
from datetime import date, datetime, timedelta as td
import pandas as pd
from dateutil import relativedelta
import json

# %%
# define the name of the directory to be created
current_directory = os.getcwd()
final_directory = os.path.join(current_directory, r'data')
if not os.path.exists(final_directory):
    os.makedirs(final_directory)

# %%
with open("credentials.json", "r") as file:
    credentials = json.load(file)
    rescuetime_cr = credentials['rescuetime']
    KEY = rescuetime_cr['Key']

# %%
baseurl = 'https://www.rescuetime.com/anapi/data?key='
url =  baseurl + KEY


# %%
# Adjustable by Time Period
def get_payload(start_date, end_date,
                resolution='day', device='computers'):
    return {
        'perspective':'interval',
        'resolution_time': resolution, #1 of "month", "week", "day", "hour", "minute"
        'restrict_kind': 'document',
        'restrict_begin': start_date,
        'restrict_end': end_date,
        'restrict_source_type': device,
        'format':'json' #csv
    }

def rescuetime_get_activities(start_date, end_date,
                              resolution='day', device='computers'):
    return _rescuetime_get_activities(
        get_payload(start_date, end_date,
                resolution='day', device=device))

def _rescuetime_get_activities(payload):
    # Configuration for Query
    # SEE: https://www.rescuetime.com/apidoc
    
    # restrict_source_type
    

    # Setup Iteration - by Day
    d1 = datetime.strptime(payload['restrict_begin'], "%Y-%m-%d").date()
    d2 = datetime.strptime(payload['restrict_end'], "%Y-%m-%d").date()
    delta = d2 - d1

    activities_list = []

    # Iterate through the days, making a request per day
    for i in range(delta.days + 1):
        # Find iter date and set begin and end values to this to extract at once.
        d3 = d1 + td(days=i) # Add a day

        # Update the Payload
        payload['restrict_begin'] = str(d3) # Set payload days to current
        payload['restrict_end'] = str(d3)   # Set payload days to current

        # Request
        try:
            r = requests.get(url, payload) # Make Request
            iter_result = r.json() # Parse result
            # print("Collecting Activities for " + str(d3))
        except:
            print("Error collecting data for " + str(d3))

        for i in iter_result['rows']:
            activities_list.append(i)

    return activities_list

# %%
def get_data(cdate):
    all_activities = []
    start_date = str(cdate - relativedelta.relativedelta(days=0))
    end_date = str(cdate)
    print('Pulling daily data for ', start_date)

    for device in ['computers', 'mobile']:
        activities_minute_log = rescuetime_get_activities(
            start_date, end_date, 'minute', device=device)
        activities_per_minute = pd.DataFrame.from_dict(activities_minute_log)
        activities_per_minute.columns = [
            'Date', 'Seconds', 'NumberPeople', 'Actitivity',
            'Document', 'Category', 'Productivity']
        all_activities.append(activities_per_minute)

    return pd.concat(all_activities)


# %%
def fname(cdate):
    return 'data/' + str(cdate) + '.csv'


# %%
def save_data(cdate):
    df = get_data(cdate)
    df.to_csv(fname(cdate), sep='\t')


# %%
def update_history(days=14, start=1):
    for i in range(start, days):
        try:
            save_data(date.today()-relativedelta.relativedelta(days=i))
        except:
            continue

# %%
