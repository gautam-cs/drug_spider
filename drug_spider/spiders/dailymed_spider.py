import scrapy
from scrapy import Selector


class QuotesSpider(scrapy.Spider):
  name = "drugs"

  def start_requests(self):
    urls = [
      'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=437868f5-1c9e-4b0f-8a03-77df8ac0900d',
    ]
    for url in urls:
      yield scrapy.Request(url=url, callback=self.parse)

  def parse(self, response):
    page = response.url.split("/")[-2]
    filename = 'quotes-%s.html' % page
    with open(filename, 'wb') as f:
      f.write(response.body)
      sel = Selector(text=response.body)
      for i in range(1,24):
        a = sel.xpath(f'//*[@id="anch_dj_dj-dj_{i}"]/text()').extract()
        '//*[@id="anch_dj_dj-dj_1"]'
        b = sel.xpath(f'//*[@id="drug-information"]/div/ul/li[1]/div[1]/text()').extract()
        print(a, ':  ', b)
        input()
    self.log('Saved file %s' % filename)
