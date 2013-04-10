import urllib.request, urllib.error, urllib.parse

def getgoogleurl(search,siteurl=False):
    if siteurl==False:
        return 'http://www.google.com/search?q='+urllib.parse.quote(search)+'&oq='+urllib.parse.quote(search)
    else:
        return 'http://www.google.com/search?q=site:'+urllib.parse.quote(siteurl)+'%20'+urllib.parse.quote(search)+'&oq=site:'+urllib.parse.quote(siteurl)+'%20'+urllib.parse.quote(search)

def getgooglelinks(search,siteurl=False):
   #google returns 403 without user agent
   headers = {'User-agent':'Mozilla/11.0'}
   req = urllib.request.Request(getgoogleurl(search,siteurl),None,headers)
   site = urllib.request.urlopen(req)
   data = site.read()
   site.close()

   #no beatifulsoup because google html is generated with javascript
   start = data.find('<div id="res">')
   end = data.find('<div id="foot">')
   if data[start:end]=='':
      #error, no links to find
      return False
   else:
      links =[]
      data = data[start:end]
      start = 0
      end = 0        
      while start>-1 and end>-1:
          #get only results of the provided site
          if siteurl==False:
            start = data.find('<a href="/url?q=')
          else:
            start = data.find('<a href="/url?q='+str(siteurl))
          data = data[start+len('<a href="/url?q='):]
          end = data.find('&amp;sa=U&amp;ei=')
          if start>-1 and end>-1: 
              link =  urllib.parse.unquote(data[0:end])
              data = data[end:len(data)]
              if link.find('http')==0:
                  links.append(link)
      return links

links = getgooglelinks('python')
for link in links:
       print(link)