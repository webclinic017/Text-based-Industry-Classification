import pandas as pd
import scrapy
import logging
import pathlib


class BusinessInsiderDescSpider(scrapy.Spider):
    '''
    Script to scrape company description
    Time Taken: 108.6s
    ** DELETE PREVIOUS CSV FILE BEFORE RUNNING AS SCRAPY APPENDS TO EXISTING FILE INSTEAD OF OVERWRITING **
    - 1 desc missing for russell ( maybe d)
    '''
    name = "businessinsider_desc"
    
    INDEX = 'snp'
    NUM_INVALID_TICKERS = 0
    INVALID_URLS = []
    
    ticker_df = pd.read_csv('data_in/%s_tickers_df.csv' %INDEX)
    tickers = ticker_df.Ticker

    # start_url is scrapy naming convention, dont change
    # (dont need to implement start_requests with this)
    start_urls = ['https://markets.businessinsider.com/stocks/'+ticker+'-stock'
                      for ticker in tickers]
    # This variable ensures 404 pages are handled
    handle_httpstatus_list = [404]
    
    custom_settings = {
            'LOG_LEVEL': logging.WARNING, # Scrapy logs alot of stuff at a lower setting
            'FEEDS': {pathlib.Path('data_out/%s_desc_%s.csv' %(INDEX, name[:-5])): {'format': 'csv'}}, # When writing to this file, the additional scrapes will be appended not overwritten
            'FEED_EXPORT_ENCODING': 'utf-8-sig' # not utf-8 so as to force csv to open in utf-8, if not will have wierd characters        
        }
    
    @staticmethod
    def get_ticker_from_url(url):
        ticker = url.split('/')[-1][:-6].upper()
        if ticker == 'BBX_MINERALS': # One exception
            ticker = 'BBX'
        return ticker
        
    def parse(self, response):
        url = response.request.url
        ticker = self.get_ticker_from_url(url)
        desc = response.xpath('/html/body/main/div/div[4]/div[2]/div[6]/div/text()').extract() # list of descriptions
        desc = [s.strip().replace('\n', ' ') for s in desc]
        if desc:
            print('VALID: %s'%ticker)
        else:
            # Usually ticker exists but no desc available
            self.NUM_INVALID_TICKERS +=1
            self.INVALID_URLS.append(url)
            print('INVALID TICKER: %s'%url)
        yield {
            'Ticker': ticker,
            'Description': desc
            }


