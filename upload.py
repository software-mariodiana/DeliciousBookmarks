# 
# FILE: upload.py
#
# AUTHOR: Mario Diana <software@mariodiana.com>
#
# DESCRIPTION: Upload merged bookmarks to Pinboard.
#
# SEE: https://pinboard.in/api
#
# LICENSE: BSD v3.
#
# TOUCHED: 2016.03.26
#

import json
import sys
import urllib.parse
import urllib.request


def upload(token, bookmark):
    """
    Upload bookmark to Pinboard.
    """
    uri = 'https://api.pinboard.in/v1/posts/add'
    bookmark['auth_token'] = token
    bookmark['tags'] = ','.join(bookmark['tags'])
    query = urllib.parse.urlencode(bookmark)
    uri = '%s?%s' % (uri, query)
    with urllib.request.urlopen(uri) as f:
        response = f.read().decode('utf-8')
        if response.find('result code="done"') == -1:
            print("Error uploading: %s" % (bookmarks['url']))



def main(token, bookmarksFilePath):
    data = None
    with open(bookmarksFilePath, 'r') as f:
        data = f.read()
    bookmarks = json.loads(data)
    for aBookmark in bookmarks:
        upload(token, aBookmark)



if __name__ == '__main__':
    # Pinboard API token for account.
    token = ''
    try:
        token = sys.argv[1]
    except:
        print("Usage: python3 upload.py <token>")
        sys.exit(1)
    main(token, 'bookmarks.json')

