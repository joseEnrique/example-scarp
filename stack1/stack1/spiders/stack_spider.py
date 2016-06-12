from scrapy import Spider
from scrapy.selector import Selector
import pdb

from scrapy.item import Item, Field


class InitiativeItem(Item):
    title = Field()
    url = Field()



class StackSpider(Spider):
    name = "stack1"
    allowed_domains = ["http://www.congreso.es/"]
    start_urls = [
        "http://www.congreso.es/portal/page/portal/Congreso/Congreso/Iniciativas/Busqueda%20Avanzada",
    ]

    def parse(self, response):
        questions = Selector(response).xpath('//select[@id="selectLeg"]//option/@value')
        formurl = Selector(response).xpath('//form[@id="formCambiarLegislatura"]/@action')
        print formurl.extract()
        #pdb.set_trace()
        for i in questions:
            a= i.extract()
            print i.extract()


    #http://www.congreso.es/portal/page/portal/Congreso/Congreso/Iniciativas?_piref73_2148295_73_1335437_1335437.next_page=/wc/servidorCGI&CMD=VERLST&BASE=iwi6&FMT=INITXLTS.fmt&DOCS=1-50&DOCORDER=FIFO&OPDEF=Y&QUERY=%28I%29.ACIN1.
