import requests
import os
from datetime import date, datetime, timedelta as td
import pandas as pd
from dateutil import relativedelta

# define the name of the directory to be created
current_directory = os.getcwd()
final_directory = os.path.join(current_directory, r'data')
if not os.path.exists(final_directory):
   os.makedirs(final_directory)

import json

with open("credentials.json", "r") as file:
    credentials = json.load(file)
    rescuetime_cr = credentials['rescuetime']
    KEY = rescuetime_cr['KEY']

baseurl = 'https://www.rescuetime.com/anapi/data?key='
url =  baseurl + KEY

# Configure These to Your Preferred Dates - default is the last week
start_date = str(date.today()-relativedelta.relativedelta(weeks=1))  # Start date for data
end_date   = str(date.today())  # End date for data

# Adjustable by Time Period
def rescuetime_get_activities(start_date, end_date, resolution='hour'):
    # Configuration for Query
    # SEE: https://www.rescuetime.com/apidoc
    payload = {
        'perspective':'interval',
        'resolution_time': resolution, #1 of "month", "week", "day", "hour", "minute"
        'restrict_kind':'document',
        'restrict_begin': start_date,
        'restrict_end': end_date,
        'format':'json' #csv
    }

    # Setup Iteration - by Day
    d1 = datetime.strptime(payload['restrict_begin'], "%Y-%m-%d").date()
    d2 = datetime.strptime(payload['restrict_end'], "%Y-%m-%d").date()
    delta = d2 - d1

    activities_list = []

    # Iterate through the days, making a request per day
    for i in range(delta.days + 1):
        # Find iter date and set begin and end values to this to extract at once.
        d3 = d1 + td(days=i) # Add a day
        if d3.day == 1: print('Pulling Monthly Data for ', d3)

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

activities_day_log = rescuetime_get_activities(start_date, end_date, 'day')
activities_daily = pd.DataFrame.from_dict(activities_day_log)
activities_hour_log = rescuetime_get_activities(start_date, end_date, 'hour')
activities_hourly = pd.DataFrame.from_dict(activities_hour_log)
activities_hourly.columns = ['Date', 'Seconds', 'NumberPeople', 'Actitivity', 'Document', 'Category', 'Productivity']
activities_hourly.to_csv('data/rescuetime-hourly-' + start_date + '-to-' + end_date + '.csv')

activities_minute_log = rescuetime_get_activities(start_date, end_date, 'minute')
activities_per_minute = pd.DataFrame.from_dict(activities_minute_log)
activities_per_minute.columns = ['Date', 'Seconds', 'NumberPeople', 'Actitivity', 'Document', 'Category', 'Productivity']
activities_per_minute.to_csv('data/rescuetime-by-minute' + start_date + '-to-' + end_date + '.csv')

import glob
import os

# import hourly data exports and create a single data frame
path = 'data/'
allFiles = glob.glob(path + "/rescuetime-hourly*.csv")
timelogs = pd.DataFrame()
list_ = []
for file_ in allFiles:
    df = pd.read_csv(file_,index_col=None, header=0)
    list_.append(df)
activities = pd.concat(list_)

activities.to_csv('data/rescuetime-full-data-export.csv',index=False)
