# 
# FILE: download.py
#
# AUTHOR: Mario Diana <software@mariodiana.com>
#
# DESCRIPTION: Retrieve bookmarks from Delicious.
#
# SEE: http://delicious.com/rss
#
# LICENSE: BSD v3.
#
# TOUCHED: 2016.03.26
#

import glob
import json
import os
import os.path
import sys
import urllib.error
import urllib.request


# urllib.error.HTTPError


def fetchDataAtUri(uri):
    """
    Return data in JSON format as bytes for 'uri'.
    """
    data = None
    try:
        # The Delicious server seems spotty lately, so we set a longer timeout.
        with urllib.request.urlopen(uri, timeout=90) as f:
            data = f.read()
    except urllib.error.HTTPError as err:
        print(uri)
        raise
    return data


def fetchTags(username):
    """
    Return tags for 'username'.
    """
    uri = 'http://feeds.delicious.com/v2/json/tags/%s' % (username)
    return fetchDataAtUri(uri).decode('utf-8')


def fetchBookmarksForTag(tag, username):
    """
    Return bookmarks for 'tag' for 'username'.
    """
    uri = 'http://feeds.delicious.com/v2/json/%s/%s' % (username, tag)
    return fetchDataAtUri(uri).decode('utf-8')


def loadTagsFromFile(path):
    """
    Return tags loaded from file at 'path'.
    """
    # This can be used if you've already retrieved the tags.
    tags = None
    with open(path, 'r') as f:
        tags = json.loads(f.read())
    return tags


def loadTags(username, path):
    """
    Load tags from either file at 'path' or network using 'username'.
    """
    tags = None
    if path:
        tags = loadTagsFromFile(path)
    else:
        tags = json.loads(fetchTags(username))
    return tags


def loadListOfPreviouslyDownloadedTags(directory):
    """
    Return list of tags previously downloaded to 'directory'.
    """
    files = glob.glob(os.path.join(directory, '*.json'))
    return [os.path.splitext(os.path.basename(f))[0] for f in files]


def filterPreviouslyDownloadedTags(tags, dataDirectory):
    """
    Return list of tags not downloaded by filtering previously downloaded tags.
    """
    downloadedTags = loadListOfPreviouslyDownloadedTags(dataDirectory)
    for tag in downloadedTags:
        tags.pop(tag, None)
    return tags


def main(username, tagFilePath=None):
    """
    Retrieve bookmarks for 'username': max 100 per tag, per Delicious restrictions.
    """
    directory = 'data'
    maxErrors = 3
    errorCount = 0
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(os.path.join(directory, 'bookmarks.log'), 'a') as log:
        tags = loadTags(username, tagFilePath)
        tags = filterPreviouslyDownloadedTags(tags, directory)
        print('Tags remaining: %d' % (len(tags)))
        # Doing everything in 1 thread reduces load on the Delicious server.
        for aKey in tags.keys():
            if errorCount >= maxErrors:
                print("Maximum errors reached: exiting.")
                break
            try:
                bookmarks = fetchBookmarksForTag(aKey, username)
                file = os.path.join(directory, '%s.json' % (aKey))
                with open(file, 'w') as f:
                    f.write(bookmarks)
                print(aKey)
                if tags[aKey] > 100:
                    # We want to know if we're missing bookmarks for a tag.
                    log.write('%s: %d\n' % (aKey, tags[aKey]))
            except urllib.error.HTTPError as err:
                print('%s - HTTPError: %s' % (aKey, err.strerror))
                errorCount += 1



if __name__ == '__main__':
    # Set username for account.
    username = ''
    try:
        username = sys.argv[1]
    except:
        print("Usage: python3 download.py <username>")
        sys.exit(1)
    # If we've had trouble with getting the tags, we can load them manually.
    path = os.path.join(os.path.dirname(os.getcwd()), 'tags.json')
    if os.path.exists(path):
        main(username, path)
    else:
        main(username)
