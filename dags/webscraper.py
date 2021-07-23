import requests
import pandas as pd
from lxml import html
from urllib.parse import urljoin
from tld import get_tld
from newspaper import Article

# import nltk 
# nltk.download('punkt')

CRAWL_URL = "https://www.bajajfinserv.in/"
CRAWL_URL_MATCH = get_tld(CRAWL_URL, as_object=True)

class MyCrawler:
    def __init__(self, start_page):
        self.visited_url = {}
        self.queue_url = [start_page]
        self.summary = {}
        self.keywords = {}


    def get_url_list(self, url):
        print('crawling: %s'%(url))
        try:
            url = url.lower()
            
            article = Article(url)
            article.download()
            article.parse()
            article.nlp()
            
            # print(article.keywords)
            # print(article.summary)
            # print(url)
           
            response = requests.get(url, timeout=10.0)
            raw_html = response.text
            parsed_html = html.fromstring(raw_html)
        except:
            return
        
        url_title_item = parsed_html.xpath('//title')
        url_title = '(NO TITLE)'
        try:
            url_title = url_title_item[0].text
        except:
            url_title = '(ERROR TITLE)'
        self.visited_url[url] = url_title
        self.summary[url] = article.summary
        self.keywords[url] = article.keywords
    
        for a in parsed_html.xpath('//a'):
            raw_url = a.get('href')
            if raw_url is None:
                continue
            
            parsed_url = urljoin(url, raw_url)
            if parsed_url not in list(self.visited_url.keys()) and parsed_url not in self.queue_url:
                self.queue_url.append(parsed_url)
    
    def output_result(self):
        result = pd.DataFrame()
        urls = list(self.visited_url.keys())
        titles = list(self.visited_url.values())
        summary = list(self.summary.values())
        keywords = list(self.keywords.values())

        print(summary)
        print(keywords)
        
        result['TITLE'] = titles
        result['URL'] = urls
        result['SUMMARY'] = summary
        result['KEYWORDS'] = keywords
        print('saving')
        result.to_csv('result.csv', encoding='utf-8-sig')
        print('saved')
        
    def start_crawling(self, threshold=-1):
        while threshold != 0:
            this_url = self.queue_url[0]
            
            try:
                if get_tld(this_url, as_object=True).fld != CRAWL_URL_MATCH.fld:
                    self.queue_url = self.queue_url[1:]
                else:
                    self.get_url_list(this_url)
            except:
                print('error') 
                self.queue_url = self.queue_url[1:]
            
            if len(self.queue_url) == 1:
                break
            else:
                self.queue_url = self.queue_url[1:]
                
            threshold -= 1
        
        self.output_result()
        print('DONE!')
        
        
        
# myCrawler = DeepCrawler(CRAWL_URL)
# myCrawler.start_crawling(threshold=10)