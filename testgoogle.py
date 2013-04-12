import google
from google import get_page
try:
    import bs4 as BeautifulSoup
except ImportError:
    import BeautifulSoup

url = "http://www.google.com/search?hl=en&q=Dog&btnG=Google+Search"

def get_obj():
    print(url)
    html = get_page(url)
    soup = BeautifulSoup.BeautifulSoup(html)
    results = soup.find(id = "resultStats")
    stat = results.get_text()
    print(stat)
