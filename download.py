# 
# FILE: download.py
#
# AUTHOR: Mario Diana <software@mariodiana.com>
#
# DESCRIPTION: Retrieve bookmarks from Delicious.
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
import urllib.request


# urllib.error.HTTPError


def fetchDataAtUri(uri):
    """
    Return data in JSON format as bytes for 'uri'.
    """
    data = None
    # The Delicious server seems spotty lately, so we set a longer timeout.
    with urllib.request.urlopen(uri, timeout=90) as f:
        data = f.read()
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


def loadSetOfPreviouslyDownloadedTags(directory):
    """
    Return set of tags previously downloaded to 'directory'.
    """
    files = glob.glob(os.path.join(directory, '*.json'))
    tags = [os.path.splitext(os.path.basename(f))[0] for f in files]
    return set(tags)


def main(username, tagFilePath=None):
    """
    Retrieve bookmarks for 'username': max 100 per tag, per Delicious restrictions.
    """
    directory = 'data'
    if not os.path.exists(directory):
        os.makedirs(directory)
    downloadedTags = loadSetOfPreviouslyDownloadedTags(directory)
    with open(os.path.join(directory, 'bookmarks.log'), 'w') as log:
        tags = loadTags(username, tagFilePath)
        # Doing everything in 1 thread reduces load on the Delicious server.
        for aKey in tags.keys():
            bookmarks = fetchBookmarksForTag(aKey, username)
            file = os.path.join(directory, '%s.json' % (aKey))
            if aKey in downloadedTags:
                continue
            with open(file, 'w') as f:
                f.write(bookmarks)
            downloadedTags.add(aKey)
            print(aKey)
            if tags[aKey] > 100:
                # We want to know if we're missing bookmarks for a tag.
                log.write('%s: %d\n' % (aKey, tags[aKey]))


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
