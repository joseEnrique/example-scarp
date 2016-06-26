# -*- coding: utf-8 -*-
import re
import urlparse
import scrapy
from scrapy import Spider
from scrapy.selector import Selector
import pdb
from scrapy.contrib.linkextractors import LinkExtractor

from scrapy.item import Item, Field
from scrapy.spiders import Rule


class InitiativeItem(Item):
    title = Field()
    autor = Field()
    url = Field()
    publications = Field()



class StackSpider(Spider):
    count = 0
    countaux= 0
    item = InitiativeItem()
    name = "initiatives"
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
        #TEST FOR A initiative
        #only one
        #yield scrapy.Request("http://www.congreso.es/portal/page/portal/Congreso/Congreso/Iniciativas/Indice%20de%20Iniciativas?_piref73_1335503_73_1335500_1335500.next_page=/wc/servidorCGI&CMD=VERLST&BASE=IW11&PIECE=IWA1&FMT=INITXD1S.fmt&FORM1=INITXLUS.fmt&DOCS=5-5&QUERY=%28I%29.ACIN1.+%26+%28125%29.SINI.",callback=self.oneinitiative)

        #one with link
        #yield scrapy.Request("http://www.congreso.es/portal/page/portal/Congreso/Congreso/Iniciativas/Indice%20de%20Iniciativas?_piref73_1335503_73_1335500_1335500.next_page=/wc/servidorCGI&CMD=VERLST&BASE=IW11&PIECE=IWC1&FMT=INITXD1S.fmt&FORM1=INITXLUS.fmt&DOCS=1-1&QUERY=%28I%29.ACIN1.+%26+%28186%29.SINI.",callback=self.oneinitiative)

        #some
        #yield scrapy.Request("http://www.congreso.es/portal/page/portal/Congreso/Congreso/Iniciativas?_piref73_2148295_73_1335437_1335437.next_page=/wc/servidorCGI&CMD=VERLST&BASE=IW11&PIECE=IWC1&FMT=INITXD1S.fmt&FORM1=INITXLUS.fmt&DOCS=3-3&QUERY=%28I%29.ACIN1.+%26+%28189%29.SINI.",callback=self.oneinitiative)
        yield scrapy.Request("http://www.congreso.es/portal/page/portal/Congreso/Congreso/Iniciativas/Indice%20de%20Iniciativas?_piref73_1335503_73_1335500_1335500.next_page=/wc/servidorCGI&CMD=VERLST&BASE=IW11&PIECE=IWA1&FMT=INITXD1S.fmt&FORM1=INITXLUS.fmt&DOCS=5-5&QUERY=%28I%29.ACIN1.+%26+%28125%29.SINI.",callback=self.oneinitiative)


        #for i in range(1,int(num_inis[0])+1):
        #    new_url = split[0]+"&DOCS="+str(i)+"-"+str(i)+split[2]
        #    initiative_url = urlparse.urljoin(response.url, new_url)
        #    yield scrapy.Request(initiative_url,callback=self.oneinitiative)

    def oneinitiative(self,response):
        title = Selector(response).xpath('//p[@class="titulo_iniciativa"]/text()').extract()[0]
        filter = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"]/text()')

        autors = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"\
         and text()="Autor:\n" ]/following-sibling::\
        p[@class="apartado_iniciativa"][1]/preceding-sibling::p[preceding-sibling::p[. = "Autor:\n"]]')


        boletines = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"\
            and text()="Boletines:" ]/following-sibling::\
           p[@class="texto"]')
        if boletines:
            self.count = len(boletines)

        listautors=[]
        listboletines = []

        for autor in autors:
            add = autor.xpath("a/b/text()").extract()
            if not add:
                add = autor.xpath("./text()").extract()
            listautors.append(add)

        self.item['title'] = title
        self.item['url'] = response.url
        self.item['autor'] = listautors
        self.item["publications"] = []


        for boletin in boletines:
            url = boletin.xpath("a/@href").extract()[0]
            #pdb.set_trace()
            if url:
                #pdb.set_trace()
                try:
                    found = re.search('gina(.+?)\)', url).group(1)
                except:
                    found = "Nothing"
                listboletines.append(found)

                newsletter_url = urlparse.urljoin(response.url, url)
                yield scrapy.Request(newsletter_url,callback=self.extractnewsletters,meta={'pag':found })




        #if len(listautors)>1:
        #    autor = ' - '.join( elem[0] for elem in listautors)
        #else:
        #    autor = listautors[0][0]



        #return item

    def extractnewsletters(self,response):
        number = response.meta['pag']

        try:
            urls = Selector(response).xpath('//p[@class="texto_completo"]/a/@href').extract()
        except:
            urls = False
        if not urls:

            prueba = yield scrapy.Request(response.url, callback=self.searchpages, meta={'pag': number})



        else:
            urls.append(response.url)
            for i in urls:
                newsletter_url = urlparse.urljoin(response.url, i)
                prueba = yield scrapy.Request(newsletter_url, callback=self.searchpages, meta={'pag': number})
        pdb.set_trace()







    def searchpages(self,response):
        number = response.meta['pag']

        pages = Selector(response).xpath('//div[@class="texto_completo"]/p/a/@name').extract()
        haspage = [ch for ch in pages if re.search('gina' + number + '\)', ch)]
        ae = self.count
        if haspage:
            self.countaux+=1
            publications = self.extracttext(response, number)
            self.item["publications"].append(publications)
            if self.countaux == self.count:
                return self.item
        return "Entra"






    def extracttext(self, response,number):
        text = Selector(response).xpath('//div[@class="texto_completo"]').extract()
        pages = Selector(response).xpath('//div[@class="texto_completo"]/p/a/@name').extract()
        #if is first
        firstofpage = re.search('gina(.+?)\)', pages[0]).group(1)

        #pdb.set_trace()

        # text split
        splittext = text[0].split("<br><br>")
        result = []
        control = False

        # selecciona del texto solo la pagina que nos resulta útil
        for i in splittext:
            # pdb.set_trace()
            if re.search("gina" + number + '\)', i):
                control = True
                continue
            elif int(number) < int(firstofpage):
                control = True
            if control and re.search('gina' + str(int(number) + 1) + '\)', i):
                break
            if control:
               result.append(i)

        return self.concatlist(result)

    #http://www.congreso.es/portal/page/portal/Congreso/Congreso/Iniciativas?_piref73_2148295_73_1335437_1335437.next_page=/wc/servidorCGI&CMD=VERLST&BASE=iwi6&FMT=INITXLTS.fmt&DOCS=1-50&DOCORDER=FIFO&OPDEF=Y&QUERY=%28I%29.ACIN1.
    def concatlist(self, list):
        return ' '.join( elem for elem in list)