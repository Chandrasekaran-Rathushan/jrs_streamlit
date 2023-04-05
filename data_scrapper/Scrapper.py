import os

from scrapy.crawler import  CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor

from data_scrapper.data_scrapper.spiders.linkedin_people_profile import LinkedInPeopleProfileSpider


class Scrapper:
    def __init__(self, **kwargs):
        # The path seen from where it is getting called (view.py)
        settings_file_path = 'data_scrapper.data_scrapper.settings'
        os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)

        self.username = kwargs['username']
        self.process = CrawlerRunner(get_project_settings())
        self.spider = LinkedInPeopleProfileSpider

    def run_spiders(self):
        self.process.crawl(self.spider, username=self.username)
        d = self.process.join()
        d.addBoth(lambda _: reactor.stop())
        reactor.run()
