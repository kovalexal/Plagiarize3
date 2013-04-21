"""
Modificated for my purposes
"""

#!/usr/bin/env python

# Python bindings to the Google search engine
# Copyright (c) 2009-2013, Mario Vilas
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice,this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the copyright holder nor the names of its
#       contributors may be used to endorse or promote products derived from
#       this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

__all__ = ['search']

import http.cookiejar
import os
import time
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import urllib.parse

try:
    import bs4 as BeautifulSoup
except ImportError:
    import BeautifulSoup

# URL templates to make Google searches.
url_home          = "http://www.google.%(tld)s/"
url_search        = "http://www.google.%(tld)s/search?hl=%(lang)s&q=%(query)s&btnG=Google+Search"
url_next_page     = "http://www.google.%(tld)s/search?hl=%(lang)s&q=%(query)s&start=%(start)d"
url_search_num    = "http://www.google.%(tld)s/search?hl=%(lang)s&q=%(query)s&num=%(num)d&btnG=Google+Search"
url_next_page_num = "http://www.google.%(tld)s/search?hl=%(lang)s&q=%(query)s&start=%(start)d"

#Sites to block
blocked = [
    "http://www.youtube.com",
    "http://www.blogger.com"
]

# Cookie jar. Stored at the user's home folder.
home_folder = os.getenv('HOME')
if not home_folder:
    home_folder = os.getenv('USERHOME')
    if not home_folder:
        home_folder = '.'   # Use the current folder on error.
cookie_jar = http.cookiejar.LWPCookieJar(
                            os.path.join(home_folder, '.google-cookie'))
try:
    cookie_jar.load()
except Exception:
    pass

#Parse resultStats
def parse_result_stats(stats):
    """
    Parse result stats and get a string of results quantity
    """
    stat = stats.get_text()
    result_list = stat.split()
    if (len(result_list) == 2):
        return result_list[0]
    elif (len(result_list) == 3):
        return result_list[1]
    else:
        return ""

#Convert str to int
def convert_int(str_in):
    '''
    Convert str to int
    '''
    if (str_in == ""):
        return 0
    res = 0
    tmp_str = str_in
    for i in range(len(str_in)):
        if (str_in[i : i + 1] >= '0' and str_in[i : i + 1] <= "9"):
            res *= 10
            res += int(str_in[i : i + 1])
    return res


# Request the given URL and return the response page, using the cookie jar.
def get_page(url):
    """
    Request the given URL and return the response page, using the cookie jar.

    @type  url: str
    @param url: URL to retrieve.

    @rtype:  str
    @return: Web page retrieved for the given URL.

    @raise IOError: An exception is raised on error.
    @raise urllib2.URLError: An exception is raised on error.
    @raise urllib2.HTTPError: An exception is raised on error.
    """
    request = urllib.request.Request(url)
    request.add_header('User-Agent',
                       'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0)')
    cookie_jar.add_cookie_header(request)

    '''
    Asking to wait for an internet connection to be established or exiting if needed
    '''
    got_result = 0
    while not got_result:
        try:
            response = urllib.request.urlopen(request)
            got_result = 1
        except:
            print("No internet connection found!\n")
            ans = input("Do you want to try again? (\"y\" or \"n\"): ")
            if (ans != "y"):
                exit(0)

    cookie_jar.extract_cookies(response, request)
    html = response.read()
    response.close()
    cookie_jar.save()
    return html

# Filter links found in the Google result pages HTML code.
# Returns None if the link doesn't yield a valid result.
def filter_result(link, filetype = "pdf"):
    try:
        for blocked_site in blocked:
            if link.startswith(blocked_site):
                return None
        if (link.endswith(filetype) != true):
                return None
        # Valid results are absolute URLs not pointing to a Google domain
        # like images.google.com or googleusercontent.com
        o = urllib.parse.urlparse(link, 'http')
        if o.netloc and 'google' not in o.netloc:
            return link

        # Decode hidden URLs.
        if link.startswith('/url?'):
            link = urllib.parse.parse_qs(o.query)['q'][0]

            # Valid results are absolute URLs not pointing to a Google domain
            # like images.google.com or googleusercontent.com
            o = urllib.parse.urlparse(link, 'http')
            if o.netloc and 'google' not in o.netloc:
                return link

    # Otherwise, or on error, return None.
    except Exception:
        pass
    return None

# Returns a generator that yields URLs.
def search(query, tld='com', lang='en', num=10, start=0, stop=None, pause=2.0):
    """
    Search the given query string using Google.

    @type  query: str
    @param query: Query string. Must NOT be url-encoded.

    @type  tld: str
    @param tld: Top level domain.

    @type  lang: str
    @param lang: Language.

    @type  num: int
    @param num: Number of results per page.

    @type  start: int
    @param start: First result to retrieve.

    @type  stop: int
    @param stop: Last result to retrieve.
        Use C{None} to keep searching forever.

    @type  pause: float
    @param pause: Lapse to wait between HTTP requests.
        A lapse too long will make the search slow, but a lapse too short may
        cause Google to block your IP. Your mileage may vary!

    @rtype:  generator
    @return: Generator (iterator) that yields found URLs. If the C{stop}
        parameter is C{None} the iterator will loop forever.
    """
    
    # Set of hashes for the results found.
    # This is used to avoid repeated results.
    hashes = set()

    # Prepare the search string.
    query = urllib.parse.quote_plus(query)

    # Grab the cookie from the home page.
    #time.sleep(pause)
    #print(url_home % vars())
    get_page(url_home % vars())

    # Prepare the URL of the first request.
    if num == 10:
        url = url_search % vars()
    else:
        url = url_search_num % vars()

    # Loop until we reach the maximum result, if any (otherwise, loop forever).
    while not stop or start < stop:

        # Sleep between requests.
        time.sleep(pause)

        # Request the Google Search results page.
        html = get_page(url)

        # Parse the response and process every anchored URL.
        soup = BeautifulSoup.BeautifulSoup(html)

        anchors = soup.findAll('a')
        for a in anchors:

            # Get the URL from the anchor tag.
            try:
                link = a['href']
            except KeyError:
                continue

            # Filter invalid links and links pointing to Google itself.
            link = filter_result(link)
            if not link:
                continue

            # Discard repeated results.
            h = hash(link)
            if h in hashes:
                continue
            hashes.add(h)

            # Yield the result.
            yield link

        # Prepare the URL for the next request.
        start += num
        if num == 10:
            url = url_next_page % vars()
        else:
            url = url_next_page_num % vars()

def find(query_, tld = "com", lang = "en", filetype = "", pause = 2.0):
    """
    Trying to get a quantity of responces for a query, searching for results and returning result list
    """
    if (filetype == ""):
        query = urllib.parse.quote_plus(query_)
    else:
        query = urllib.parse.quote_plus(query_ + " filetype:" + filetype)

    get_page(url_home % vars())
    url = url_search % vars()
    time.sleep(pause)
    html = get_page(url)

    soup = BeautifulSoup.BeautifulSoup(html)
    stats = soup.find(id = "resultStats")
    if (len(stats) == 0):
        print("No results were found!\nExiting...")
        exit(0)
    #stat = stats.get_text()
    stat = parse_result_stats(stats)
    results = input("Found about {0} results.\nHow much to process? (0 - EXIT): ".format(stat))
    results = int(results)
    if (results == 0):
        print("Exiting...")
        exit(0)
    if (results > convert_int(stat)):
        results = convert_int(stat)

    query = ""
    if (filetype == ""):
        query = query_
    else:
        query = query_ + " filetype:" + filetype

    got_results = 0
    urls = []
    urls = search(query_ + " filetype:pdf")
    for url in urls:
        print(url)
    exit(0)
    for url in search(query_ + " filetype:pdf"):
        if (filetype != ""):
            """!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            Loss in search results statistics - i dont know how to solve this problem
            !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"""
            if (url.endswith(filetype) == False):
                got_results += 1
                continue
        if (got_results >= results):
            break
        urls.append(url)
        got_results += 1
    return urls

# When run as a script, take all arguments as a search query and run it.
if __name__ == "__main__":
    import sys
    query = ' '.join(sys.argv[1])
    if query:
        urls = find(query, filetype = "pdf")
        for url in urls:
            print(url)