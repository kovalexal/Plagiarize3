"""
Simple Google Search
Using Google AJAX Search API
But Google blocks me, when trying to get a lot of results
"""

import json
import urllib.request, urllib.parse
from random import randint
from time import sleep

user_agents = [
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

def getSearchResults(searchfor, maxnum = 10, ask = False, pause = 2.0):
  '''
  Getting num search results from google (as urls)
  If ask == true then it will be asked, how many results do the user want to load
  '''

  got_num = 0
  urls = []

  Headers = {
    'User-Agent' : user_agents[randint(0, len(user_agents) - 1)]
  }

  '''
  if (ask == True):
    query = urllib.parse.urlencode({'q': searchfor})
    url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&start=%d&%s' % (got_num, query)
    request = urllib.request.Request(url, headers = Headers)
    search_response = urllib.request.urlopen(request, timeout = 5)
    search_results = search_response.read().decode("utf8")
    results = json.loads(search_results)
    data = results['responseData']
    print('Total results: %s' % data['cursor']['estimatedResultCount'])
    num = int(input("How much results do you want to load? "))
  '''  

  Headers = {
    'User-Agent' : user_agents[randint(0, len(user_agents) - 1)]
  }

  asked = True
  if (ask == False):
    asked = True
  else:
    asked = False

  num = maxnum
  while (got_num < num):
    query = urllib.parse.urlencode({'q': searchfor})
    url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&start=%d&%s' % (got_num, query)
    request = urllib.request.Request(url, headers = Headers)
    search_response = urllib.request.urlopen(request, timeout = 5)
    search_results = search_response.read().decode("utf8")
    results = json.loads(search_results)
    data = results['responseData']
    """
    if (asked == False):
      print('Total results: %s' % data['cursor']['estimatedResultCount'])
      num = int(input("How much results do you want to load? "))
      asked == True
    """
    hits = data['results']
    #print('Top %d hits:' % len(hits))
    #got_num += len(hits)
    for h in hits:
      if (got_num >= num):
        return urls
      got_num += 1
      urls.append(h['url'])
    sleep(pause)
    #for h in hits: print(' ', h['url'])
    #print('For more results, see %s' % data['cursor']['moreResultsUrl'])
  return urls

if __name__ == "__main__":
  import sys
  query = "".join(sys.argv[1])
  query += " filetype:pdf"

  query_number = int(sys.argv[2])
  urls = getSearchResults(query, query_number, ask = True)
  for url in urls:
    print(url)
