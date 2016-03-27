# 
# FILE: convert.py
#
# AUTHOR: Mario Diana <software@mariodiana.com>
#
# DESCRIPTION: Convert an exported Delicious bookmarks.html file 
# into a JSON file conforming to the Pinboard API.
#
# RESTRICTION: The bookmarks.html file must be first processed using 
# the 'tidy' utility, converting the file with the -asxml option.
#
# DEPENDENCIES: BeautifulSoup v4. 
#
# SEE: https://pinboard.in/api, http://www.crummy.com/software/BeautifulSoup
#
# LICENSE: BSD v3.
#
# TOUCHED: 2016.03.27
#

import datetime
import json
import re

from bs4 import BeautifulSoup


def parseBookmarksHtml(bookmarks):
    """
    Return BeautifulSoup object, having wrapped each bookmark in a DIV tag.
    """
    # Some bookmarks have descriptions (dd) and some don't.
    pattern = r'(<dt>.+?<\/dt>(.?<dd>.+?<\/dd>)?)'
    bookmarks = re.findall(pattern, bookmarks, re.DOTALL)
    data = []
    wrapper = '<div class="bookmark">%s</div>'
    for aBookmark in bookmarks:
        # The regular expression we've relied on gives us a tuple.
        data.append(wrapper % (aBookmark[0].replace('\n', '')))
    return BeautifulSoup(''.join(data), 'html.parser')


def convertTimestamp(timestamp):
    """
    Return string representing 'timestamp' in ISO format ("Zulu").
    """
    timestamp = int(timestamp)
    return datetime.datetime.fromtimestamp(timestamp).isoformat() + 'Z'


def convertBookmarkDivsToJson(divs):
    """
    Return JSON string constructed from list of bookmark DIV tags: 'divs'.
    """
    bookmarks = []
    for aDiv in divs:
        d = dict()
        anchor = aDiv.find('a')
        d['url'] = anchor.attrs['href']
        d['description'] = anchor.text
        d['dt'] = convertTimestamp(anchor.attrs['add_date'])
        d['tags'] = anchor.attrs['tags'].split(',')
        extended = aDiv.find('dd')
        d['extended'] = extended.text if extended else ''
        bookmarks.append(d)
    return json.dumps(bookmarks)
