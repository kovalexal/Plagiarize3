import http.cookiejar
import os
import time
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import urllib.parse
import socket
import urllib.error
from random import randint

try:
    import bs4 as BeautifulSoup
except ImportError:
    import BeautifulSoup

# URL templates to make Google searches.
url_search        = "http://www.google.%(domain)s/search?hl=%(language)s&q=%(search_query)s&btnG=Google+Search"
url_next_page     = "http://www.google.%(domain)s/search?hl=%(language)s&q=%(search_query)s&start=%(start)d"

# Sites to block
blocked = [
    "http://www.youtube.com",
    "http://www.blogger.com"
]

user_agents = [
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.0.1) Gecko/20060111 Firefox/1.5.0.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 (FM Scene 4.6.1)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 (.NET CLR 3.5.30729) (Prevx 3.0.5)",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)",
    "Mozilla/5.0 (compatible; Yahoo! Slurp/3.0; http://help.yahoo.com/help/us/ysearch/slurp)",
    "Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14",
    "Mozilla/5.0 (Windows NT 6.0; rv:2.0) Gecko/20100101 Firefox/4.0 Opera 12.14",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0) Opera 12.14",
    "Opera/12.80 (Windows NT 5.1; U; en) Presto/2.10.289 Version/12.02",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.13) Gecko/20101213 Opera/9.80 (Windows NT 6.1; U; zh-tw) Presto/2.7.62 Version/11.01",
    "Opera/9.80 (X11; Linux i686; U; en) Presto/2.5.27 Version/10.60"
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

def get_page(url):
    """
    Gets a page from url
    """
    request = urllib.request.Request(url)
    request.add_header("User-Agent", user_agents[randint(0, len(user_agents) - 1)])
    cookie_jar.add_cookie_header(request)

    got_result = 0
    while not(got_result):
        try:
            responce = urllib.request.urlopen(request)
            got_result = 1
        except (socket.gaierror, urllib.error.URLError, urllib.error.HTTPError):
            print("No internet connection found!")
            ans = input("Do you want to try again? (\"y\" or \"n\"): ")
            if (ans != "y"):
                exit(0)

    cookie_jar.extract_cookies(responce, request)
    html = responce.read()
    responce.close()
    cookie_jar.save()
    return html

def parse_result_stats(stats):
    """
    Parse result stats and get a string of results quantity
    """
    stat = stats.get_text()
    result_list = stat.split()
    if ("About" in result_list):
        return result_list[1]
    if ("result" or "results" in result_list):
        return result_list[0]
    return ""

def convert_int(str_in):
    '''
    Convert str to int
    '''
    if (len(str_in) == 0):
        return 0
    number = 0
    for i in range(len(str_in)):
        if (str_in[i] >= '0' and str_in[i] <= '9'):
            number *= 10
            number += int(str_in[i])
    return number

def cast_result(link, filetype= ""):
    try:
        for blocked_site in blocked:
            if (link.startswith(blocked_site)):
                return None

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
                if (filetype == "pdf" and link.endswith(filetype) == False):
                    return None
                return link
    except Exception:
        pass
    return None

def search(query, tld = "com", lang = "en", pause = 2.0, filetype = "pdf"):
    """
    Gets links from google search
    """
    # Hashes are used to avoid repeated results
    hashes = set()

    # Preparing the search string
    if (filetype == ''):
        query = urllib.parse.quote_plus(query)
    else:
        query = urllib.parse.quote_plus(query + " filetype:" + filetype)

    search_url = url_search % {"domain" : tld, "language" : lang, "search_query" : query}

    html = get_page(search_url)

    soup = BeautifulSoup.BeautifulSoup(html)
    stats = soup.find(id = "resultStats")
    stat = parse_result_stats(stats)
    if (stat == ""):
        print("No results were found!")
        print("Exiting...")
        exit(0)
    results = input("Found about {0} results.\nHow much to process? (0 - EXIT): ".format(stat))
    results = convert_int(results)
    if (results > convert_int(stat)):
        results = convert_int(stat)
    
    results_found = 0
    links = []
    start = 0
    while (results_found < results):
        time.sleep(pause)
        soup = BeautifulSoup.BeautifulSoup(html)

        anchors = soup.findAll("a")
        for a in anchors:
            try:
                link = a["href"]
            except KeyError:
                continue

            link = cast_result(link, filetype = "pdf")
            if not link:
                continue

            h = hash(link)
            if (h in hashes):
                continue
            hashes.add(h)

            if (results_found < results):
                links.append(link)
                results_found += 1
            else:
                break
        start = results_found
        search_url = url_next_page % {"domain" : tld, "language" : lang, "search_query" : query, "start" : start}
        time.sleep(pause)
        html = get_page(search_url)
    return links

if __name__ == "__main__":
    import sys
    print(search(query = sys.argv[1], pause = 0.5))