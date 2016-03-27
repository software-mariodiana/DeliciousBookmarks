# 
# FILE: merge.py
#
# AUTHOR: Mario Diana <software@mariodiana.com>
#
# DESCRIPTION: Merge separate Delicious tag JSON files into 
# one JSON file, converted into Pinboard format.
#
# SEE: https://pinboard.in/api
#
# LICENSE: BSD v3.
#
# TOUCHED: 2016.03.26
#

import glob
import json
import os.path


def convertBookmarks(deliciousBookmarks):
    bookmarks = []
    for bm in deliciousBookmarks:
        # Some of my bookmarks have a malformed tag.
        tags = list(map(lambda x: x if x != "UI/UX" else "UI-UX", bm['t']))
        bookmark = dict()
        bookmark['tags'] = tags
        bookmark['url'] = bm['u']
        # 'description' is actually what we would think of as the URL's title.
        bookmark['description'] = bm['d']
        # Datetime of when URL was added.
        bookmark['dt'] = bm['dt']
        # 'extended' is actually what we would think of as the URL's description.
        bookmark['extended'] = bm['n']
        bookmarks.append(bookmark)
    return bookmarks


def mergeBookmark(dictionary, bookmarks):
    for bm in bookmarks:
        url = bm['url']
        if url in dictionary:
            a = set(dictionary[url]['tags'])
            b = set(bm['tags'])
            a.update(b)
            dictionary[url]['tags'] = list(a)
        else:
            dictionary[url] = bm
    return dictionary


def main(files):
    bookmarks = {}
    for aFile in files:
        print(aFile)
        data = None
        with open(aFile, 'r') as f:
            data = f.read()
        bookmarksForTag = json.loads(data)
        convertedBookmarks = convertBookmarks(bookmarksForTag)
        bookmarks = mergeBookmark(bookmarks, convertedBookmarks)
    allBookmarks = []
    for aKey in bookmarks.keys():
        allBookmarks.append(bookmarks[aKey])
    data = json.dumps(allBookmarks)
    with open('bookmarks.json', 'w') as f:
        f.write(data)


if __name__ == '__main__':
    files = glob.glob(os.path.join('data', '*.json'))
    main(files)
