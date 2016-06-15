import urlparse
import scrapy
from scrapy import Spider
from scrapy.selector import Selector
import pdb

from scrapy.item import Item, Field


class InitiativeItem(Item):
    title = Field()
    url = Field()



class StackSpider(Spider):
    name = "stack1"
    allowed_domains = ["http://www.congreso.es/","www.congreso.es"]
    start_urls = [
        "http://www.congreso.es/portal/page/portal/Congreso/Congreso/Iniciativas/Indice%20de%20Iniciativas",
    ]


    def parse(self, response):
        list_types = Selector(response).xpath('//div[@class="listado_1"]//ul/li/a/@href')


        for types in list_types:
            href=  types.extract()
            initiative_url = urlparse.urljoin(response.url, href)


            yield scrapy.Request(initiative_url,callback=self.initiatives)







    def initiatives(self, response):
        first_url = Selector(response).xpath('//div[@class="resultados_encontrados"]/p/a/@href').extract()[0]

        num_inis = Selector(response).xpath('//div[@class="SUBTITULO_CONTENIDO"]/span/text()').extract()

        split = first_url.partition("&DOCS=1-1")


        yield scrapy.Request("http://www.congreso.es/portal/page/portal/Congreso/Congreso/Iniciativas/Indice%20de%20Iniciativas?_piref73_1335503_73_1335500_1335500.next_page=/wc/servidorCGI&CMD=VERLST&BASE=IW11&PIECE=IWC1&FMT=INITXD1S.fmt&FORM1=INITXLUS.fmt&DOCS=10-10&QUERY=%28I%29.ACIN1.+%26+%28213%29.SINI.",callback=self.oneinitiative)

        #for i in range(1,int(num_inis[0])+1):
        #    new_url = split[0]+"&DOCS="+str(i)+"-"+str(i)+split[2]
        #    initiative_url = urlparse.urljoin(response.url, new_url)
        #    yield scrapy.Request(initiative_url,callback=self.oneinitiative)


    def oneinitiative(self,response):
        title = Selector(response).xpath('//p[@class="titulo_iniciativa"]/text()').extract()[0]
        filter = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"]/text()')

        #test = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa" and text()="Autor:\n"]/following-sibling::p[@class="texto" and preceding-sibling::p[] ]')
        test = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa" and text()="Autor:\n" ]/following-sibling::p[@class="texto" and  following-sibling::p[not(@class="apartado_iniciativa")]]').extract()



        pdb.set_trace()
        item = InitiativeItem()
        item['title']= title
        item['url'] = response.url








        return item

    #http://www.congreso.es/portal/page/portal/Congreso/Congreso/Iniciativas?_piref73_2148295_73_1335437_1335437.next_page=/wc/servidorCGI&CMD=VERLST&BASE=iwi6&FMT=INITXLTS.fmt&DOCS=1-50&DOCORDER=FIFO&OPDEF=Y&QUERY=%28I%29.ACIN1.
