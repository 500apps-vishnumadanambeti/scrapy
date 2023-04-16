import scrapy
from scrapy import Selector

class TimesjobSpider(scrapy.Spider):
    name = "timesjob"
    allowed_domains = ["www.timesjobs.com"]
    start_urls = ["https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords=python&txtLocation="]

    def __init__(self, *args, **kwargs):
        super(TimesjobSpider, self).__init__(*args, **kwargs)
        self.page_count = 0

    def parse(self, response):
        # Extract job URLs
        job_urls = response.xpath("//ul[@class='new-joblist']/li/header/h2/a/@href").getall()
        for job_url in job_urls:
            yield scrapy.Request(url=job_url, callback=self.parse_job)

        self.page_count += 1
        if self.page_count >= 10:
            return

        # Extract URL for next page, if available
        next_page_url = response.css(".pagination li a[rel='next']::attr(href)").get()
        if next_page_url:
            yield scrapy.Request(url=next_page_url, callback=self.parse)

    def parse_job(self, response):
        # Define job_dict to store extracted data
        print(response.url,">>>>>>>>>>>>>>>>>>>...................")
        job_dict = {}

        # Extract job title
        title = response.xpath("//div[@class='jd-header wht-shd-bx']/h1/text()").get()
        company_name = response.xpath("//div[@class='jd-header wht-shd-bx']/h2/text()").get()  
        job_dict['title'] = title.replace('"', "").strip()
        job_dict['company_name'] = company_name.replace('"', "").strip()
        test = response.xpath("//div[@class='jd-header wht-shd-bx']/ul[@class='top-jd-dtl clearfix']/li").getall()
        print(test)
        for i in test:
            sel = Selector(text=i)
            li_title = sel.xpath('//text()').get().strip()
            li_text = sel.xpath('//li/text()').get().strip()
            if li_title == "₹":
                li_title = "package"
            if li_title.strip() != "":
                job_dict[li_title] = li_text.replace('"', "").strip()
        yield job_dict




