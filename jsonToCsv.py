#!/usr/bin/python
# Convert github JSON files into CSV for import into STATA
# Not using csv.DictWriter since we're reading multilevel json
# February 2012
# Sheng Wu

import csv
import datetime
import json
import os
from feed.date.rfc3339 import tf_from_timestamp as tf_from_rfc3339

# Names of json files to convert
file_list = [
    'collaborators',
    'comments',
    'commits',
    'contributors',
    'forks',
    'issues',
    'issues_comments',
    'issues_events',
    'pulls',
    'pulls_comments',
    'stargazers',
    'subscribers'
]

# The fields we want from each file
# Some of them are nested
relevant_fields = {
'collaborators': [
    ['id'],
    ['login'],
    ['type'],
    ['gravatar_id']
    ],
'comments': [
    ['body'],
    ['commit_id'],
    ['created_at'],
    ['id'],
    ['line'],
    ['path'],
    ['position'],
    ['updated_at'],
    ['user', 'id'],
    ['user', 'login']
    ],
'commits': [
    ['author', 'id'],
    ['author', 'login'],
    ['commit', 'author', 'date'],
    ['commit', 'author', 'email'],
    ['commit', 'author', 'name'],
    ['commit', 'comment_count'],
    ['commit', 'committer', 'date'],
    ['commit', 'committer', 'email'],
    ['commit', 'committer', 'name'],
    ['commit', 'message'],
    ['commit', 'tree', 'sha'],
    ['committer', 'id'],
    ['committer', 'login'],
    ['parents', 'sha'],
    ['sha']
    ],
'contributors': [
    ['id'],
    ['login'],
    ['type'],
    ['gravatar_id']
    ],
'forks': [
    ['created_at'],
    ['description'],
    ['fork'], # Rename as is_fork
    ['forks'],
    ['full_name'],
    ['has_downloads'],
    ['has_issues'],
    ['has_wiki'],
    ['homepage'],
    ['id'],
    ['language'],
    ['name'],
    ['open_issues'],
    ['owner', 'id'],
    ['owner', 'login'],
    ['permissions', 'admin'],
    ['permissions', 'pull'],
    ['permissions', 'push'],
    ['private'],
    ['pushed_at'],
    ['size'],
    ['updated_at'],
    ['watchers']
    ],
'issues': [
    ['assignee'],
    ['body'],
    ['comments'],
    ['closed_at'],
    ['created_at'],
    ['id'],
    ['labels'],
    ['milestone'],
    ['number'],
    ['state'],
    ['title'],
    ['updated_at'],
    ['user', 'id'],
    ['user', 'login']
    ],
'issues_comments': [
    ['body'],
    ['created_at'],
    ['id'],
    ['issue_url'], # Get number after last slash, rename to issue_id
    ['updated_at'],
    ['user', 'id'],
    ['user', 'login']
    ],
'issues_events': [
    ['actor', 'id'],
    ['actor', 'login'],
    ['commit_id'],
    ['created_at'],
    ['event'],
    ['id'],
    ['issue', 'id']
    ],
'pulls': [
    ['assignee', 'id'], # assignee may be empty
    ['assignee', 'login'],
    ['base', 'ref'],
    ['base', 'repo', 'id'],
    ['base', 'repo', 'owner', 'id'],
    ['base', 'repo', 'owner', 'login'],
    ['base', 'user', 'id'], # base user may be null
    ['base', 'user', 'login'],
    ['base', 'sha'],
    ['body'],
    ['closed_at'],
    ['created_at'],
    ['head', 'ref'],
    ['head', 'repo', 'id'],
    ['head', 'repo', 'owner', 'id'],
    ['head', 'repo', 'owner', 'login'],
    ['head', 'user', 'id'], # head user may be null
    ['head', 'user', 'login'],
    ['head', 'sha'],
    ['id'],
    ['merge_commit_sha'],
    ['merged_at'],
    ['milestone', 'description'], # milestone may be null
    ['milestone', 'creator', 'id'],
    ['milestone', 'creator', 'login'],
    ['milestone', 'created_at'],
    ['milestone', 'title'],
    ['milestone', 'number'],
    ['milestone', 'due_on'],
    ['milestone', 'state'],
    ['milestone', 'closed_issues'],
    ['milestone', 'open_issues'],
    ['milestone', 'id'],
    ['number'],
    ['state'],
    ['title'],
    ['updated_at'],
    ['user', 'id'],
    ['user', 'login']
    ],
'pulls_comments': [
    ['body'],
    ['commit_id'],
    ['created_at'],
    ['id'],
    ['original_commit_id'],
    ['original_position'],
    ['path'],
    ['position'],
    ['updated_at'],
    ['user', 'id'],
    ['user', 'login']
    ],
'stargazers': [
    ['id'],
    ['login'],
    ['type'],
    ['gravatar_id']
    ],
'subscribers': [
    ['id'],
    ['login'],
    ['type'],
    ['gravatar_id']
    ]
}

# Grab list of folders containing json files
base_url = '/Github/data/crawl_topRepos/'
#base_url = '/Github/data/crawl_rnd10kRepos/'
files = [base_url + d for d in os.listdir(base_url)]
folders = sorted(filter(os.path.isdir, files))
print "Parsing JSON from %d folders found in %s" % (len(folders), base_url)

# Create tab-delimited files and store in dictionary
# Use .csv file extension for convenience in STATA import
csv_filenames = [x + '.csv' for x in relevant_fields.keys()]
opened_files = [open(x, 'w') for x in csv_filenames]
csv_writers = [csv.writer(x, delimiter='\t') for x in opened_files]
csv_files = dict(zip(relevant_fields.keys(), csv_writers))

# Write csv headers
for name in relevant_fields.keys():
    header = []
    for fields in relevant_fields[name]:
        head = '_'.join(fields).upper()

        # Rename certain fields
        if head == 'FORK':
            head = 'IS_FORK'
        elif name == 'ISSUE_URL':
            header = 'ISSUE_ID'

        # Add fields for times
        if head[-3:] == '_AT':
            header.append('TIME_' + head[:-3])
            head = 'DATE_' + head[:-3]

        header.append(head)

    csv_files[name].writerow(header)

for folder in folders:
    print "Reading json from " + folder
    skipped_files = 0
    skipped_values = 0

    for json_file in file_list:
        # Some files are missing
        try:
            f = open('%s/%s.json.txt' % (folder, json_file))
        except IOError as e:
            skipped_files += 1
            continue

        # Json can be malformed
        try:
            json_data = json.load(f)
        except:
            skipped_files += 1
            continue
            
        fields_to_read = relevant_fields[json_file]

        # Each item in the json list corresponds to a csv row
        for item in json_data:
            fields_read = []
            for fields in fields_to_read:
                # Some users don't have certain fields
                try:
                    val = item[fields[0]]
                except KeyError:
                    val = None

                # Only read first commit parent for now
                if fields[0] == 'parents' and len(val) > 0:
                    val = val[0]

                # Hit nested fields
                for f in fields[1:]:
                    if not val:
                        break
                    val = val[f]

                # Special cases
                # Only want id part of issue_url
                if fields[0] == 'issue_url':
                    val = val.split('/')[-1]

                # Separate dates and times for STATA
                if fields[-1][-3:] == '_at':
                    # Handle null values
                    if not val:
                        fields_read.append(val)
                        break

                    tf = tf_from_rfc3339(val)
                    dt = datetime.datetime.utcfromtimestamp(tf)

                    # Append the time to fields_read
                    fields_read.append(dt.strftime("%H:%M:%S"))

                    # Date is stored in val
                    val = dt.strftime("%d%b%Y")

                # Handle unicode values
                if type(val) == unicode:
                    val = val.encode('utf-8')

                fields_read.append(val)

            # Write fields from the current item to a csv row
            csv_files[json_file].writerow(fields_read)

    if skipped_files > 0:
        print "# Warning: skipped %d missing files" % skipped_files
    if skipped_values > 0:
        print "# Warning: skipped %d missing values" % skipped_values

for f in opened_files:
    f.close()

