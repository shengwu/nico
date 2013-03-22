#!/usr/bin/python
# Scrape Google Trends for a list of keywords
# March 2012
# Sheng Wu

import csv
import os
from pyGTrends import pyGTrends

# Set Google username and password
google_username = '' # Insert username
google_password = '' # Insert password

# Create folders in which to save files
daily_dir = 'daily'
weekly_dir = 'weekly'
if not os.path.exists(daily_dir):
    os.makedirs(daily_dir)
if not os.path.exists(weekly_dir):
    os.makedirs(weekly_dir)

# Import list of words
f = open('words_list.txt', 'r')
keywords = [line.strip() for line in f.readlines()]
f.close()

# Start pyGTrends
c = pyGTrends(google_username, google_password)
for keyword in keywords:
    print 'Writing files for keyword: %s' % keyword
    daily_filename = keyword + '.csv'
    weekly_filename = keyword + '.csv'
    daily_file = open(daily_dir + '/' + daily_filename, 'w')
    weekly_file = open(weekly_dir + '/' + weekly_filename, 'w')
    daily_writer = csv.writer(daily_file, delimiter='\t')
    weekly_writer = csv.writer(weekly_file, delimiter='\t')

    # Retrieve and write daily_data
    daily_data = c.get_daily(keyword)
    for row in daily_data:
        daily_writer.writerow(row)

    # Retrieve and write weekly data
    weekly_data = c.get_all(keyword)
    for row in weekly_data:
        weekly_writer.writerow(row)

    daily_file.close()
    weekly_file.close()

