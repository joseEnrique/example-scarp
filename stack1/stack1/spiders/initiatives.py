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

    #item = InitiativeItem()
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
        #yield scrapy.Request("http://www.congreso.es/portal/page/portal/Congreso/Congreso/Iniciativas?_piref73_2148295_73_1335437_1335437.next_page=/wc/servidorCGI&CMD=VERLST&BASE=IW10&PIECE=IWD0&FMT=INITXD1S.fmt&FORM1=INITXLUS.fmt&DOCS=8-8&QUERY=%28I%29.ACIN1.+%26+%28005%29.SINI.",callback=self.oneinitiative)

        #yield scrapy.Request("http://www.congreso.es/portal/page/portal/Congreso/Congreso/Iniciativas/Indice%20de%20Iniciativas?_piref73_1335503_73_1335500_1335500.next_page=/wc/servidorCGI&CMD=VERLST&BASE=IW11&PIECE=IWA1&FMT=INITXD1S.fmt&FORM1=INITXLUS.fmt&DOCS=1-1&QUERY=%28I%29.ACIN1.+%26+%28080%29.SINI.",callback=self.oneinitiative)
        yield scrapy.Request("http://www.congreso.es/portal/page/portal/Congreso/Congreso/Iniciativas/Indice%20de%20Iniciativas?_piref73_1335503_73_1335500_1335500.next_page=/wc/servidorCGI&CMD=VERLST&BASE=IW11&PIECE=IWC1&FMT=INITXD1S.fmt&FORM1=INITXLUS.fmt&DOCS=13-13&QUERY=%28I%29.ACIN1.+%26+%28162%29.SINI.",callback=self.oneinitiative)


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


        ##DEPENDE DE DONDE ESTEN SITUADOS LOS BOLETINES
        #si no estan los ultimos
        bol = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"\
         and text()="Boletines:" ]/following-sibling::\
        p[@class="apartado_iniciativa"][1]/preceding-sibling::p[preceding-sibling::p[. = "Boletines:"]]')


        #si estan los ultimos
        bol1= Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"\
            and text()="Boletines:" ]/following-sibling::\
           p[@class="texto"]')

        #switch para saber si esta el ultimo o no
        if bol:
            boletines = bol
        elif not bol:
            boletines = bol1
        else:
            boletines = False



        listautors=[]


        for autor in autors:
            add = autor.xpath("a/b/text()").extract()
            if not add:
                add = autor.xpath("./text()").extract()
            listautors.append(add)

        item = InitiativeItem()

        item['title'] = title
        item['url'] = response.url
        item['autor'] = listautors
        item["publications"]=[]


        if boletines:
            urls = boletines.xpath("a/@href").extract()
            listurls = []

            for url in urls:
                newsletter_url = urlparse.urljoin(response.url, url)
                listurls.append(newsletter_url)
            #se quita duplicadas
            listurls= list(set(listurls))
            last_url = listurls[-1]
            number = self.getnumber(last_url)
            self.dellastelement(listurls)
            yield scrapy.Request(last_url,callback=self.recursiveletters, dont_filter = False,  meta={'pag': number, 'item':item,'urls':listurls, 'isfirst': True, 'next':False })


        else:
            yield item



        #if len(listautors)>1:
        #    autor = ' - '.join( elem[0] for elem in listautors)
        #else:
        #    autor = listautors[0][0]







    def recursiveletters(self, response):
        number = response.meta['pag']
        item = response.meta['item']
        listurls = response.meta['urls']
        isfirst = response.meta['isfirst']
        urls = response.meta['next']
        if isfirst=="a":
            #pdb.set_trace()
            pass

        pages = Selector(response).xpath('//p/a/@name').extract()
        if pages:
            #aqui se busca
            haspage = [ch for ch in pages if re.search('gina' + number + '\)', ch)]
        else:
            haspage = True
        #pdb.set_trace()
        try:
            firstopage = re.search('gina(.+?)\)', pages[0]).group(1)
        except:
            firstopage= "1"

        if not haspage and int(number)!= int(firstopage)-1 and pages:
            #solo hasta siguiente
            urlstopass = Selector(response).xpath('//p[@class="texto_completo"]/a[not(text()="Siguiente\n    >>")]/@href').extract()
            urlstopass = list(set(urlstopass))

            next_url = False
            if urlstopass and not urls:

                urls = [i for i in urlstopass[0:len(urlstopass)]]
                url = urls[0]
                next_url = urlparse.urljoin(response.url, url)
                self.delfirstelement(urls)
            elif urls:
                url = urls[0]
                next_url = urlparse.urljoin(response.url, url)
                self.delfirstelement(urls)

            else:
                #No lo encuentra porque esta mal organizado
                pdb.set_trace()
                err = "Errror  "+number + " URL: "+response.url

                item["publications"].append(err)

                yield item

            if next_url:
                if isfirst:
                    yield scrapy.Request(next_url,callback=self.recursiveletters, dont_filter = False,  meta={'pag': number, 'item':item,'urls':listurls, 'isfirst':True,'next':urls })
                else:
                    yield scrapy.Request(next_url,callback=self.recursiveletters, dont_filter = False,  meta={'pag': number, 'item':item,'urls':listurls, 'isfirst':False, 'next':urls })


        else:
        # si encuentras


            if isfirst:
                if haspage:
                    if not listurls:
                        item["publications"].append(self.searchpages(response, number))
                        yield item


                    else:
                        last_url = listurls[-1]
                        number = self.getnumber(last_url)
                        self.dellastelement(listurls)
                        item["publications"].append(self.searchpages(response, number))

                        yield scrapy.Request(last_url, callback=self.recursiveletters, dont_filter=False,
                                             meta={'pag': number, 'item': item, 'urls': listurls, 'isfirst': "a",
                                                   'next': False})


                    #este es el que devuelve el objeto, cuando no quedan urls
                    # Este es el esencial
            elif not listurls and not isfirst:
                    if haspage:
                        item["publications"].append(self.searchpages(response, number))
                        yield item

                        #
            else:
                if haspage:
                    last_url = listurls[-1]
                    number = self.getnumber(last_url)
                    self.dellastelement(listurls)
                    item["publications"].append(self.searchpages(response,number))
                    yield scrapy.Request(last_url,callback=self.recursiveletters, dont_filter = False,  meta={'pag': number, 'item':item,'urls':listurls, 'isfirst':False , 'next':False})



    def searchpages(self,response, number):

        pages = Selector(response).xpath('//p/a/@name').extract()
        haspage = [ch for ch in pages if re.search('gina' + number + '\)', ch)]


        pdb.set_trace()
        if haspage:

            publications = self.extracttext(response, number)

            return publications
        else:
            if number=="1":
                return self.extracttext(response, number)
            else:

                try:
                    return "Error  "+number + " URL: "+response.url
                except:
                    return "ERROR"






    def extracttext(self, response,number):
        pages = Selector(response).xpath('//p/a/@name').extract()
        text = Selector(response).xpath('//div[@class="texto_completo"]').extract()

        result = []
        control = False

        try:
            firstopage = self.getnumber(pages[0])
        except:
            firstopage= "1"
            control = True

        # selecciona del texto solo la pagina que nos resulta útil
        splittext = text[0].split("<br><br>")
        for i in splittext:
                # pdb.set_trace()
            if re.search("gina" + number + '\)', i):
                control = True
                continue
            elif int(number) < int(firstopage):
                control = True
            if control and re.search('gina' + str(int(number) + 1) + '\)', i):
                break
            if control:
                result.append(i)
        pdb.set_trace()
        return self.removeHTMLtags(self.concatlist(result))

    #http://www.congreso.es/portal/page/portal/Congreso/Congreso/Iniciativas?_piref73_2148295_73_1335437_1335437.next_page=/wc/servidorCGI&CMD=VERLST&BASE=iwi6&FMT=INITXLTS.fmt&DOCS=1-50&DOCORDER=FIFO&OPDEF=Y&QUERY=%28I%29.ACIN1.
    def concatlist(self, list):
        return ' '.join( elem for elem in list)

    def dellastelement(self,list):

        del list[-1]
        return list

    def delfirstelement(self, list):

        del list[0]
        return list


    def getnumber(self,url):
        try:
            found = re.search('gina(.+?)\)', url).group(1)
        except:
            found = False
        return found


    def removeHTMLtags(self,text):
        import re
        TAG_RE = re.compile(r'<[^>]+>')
        BLANK = re.compile(r'\n')
        text = TAG_RE.sub('', text)
        return BLANK.sub('', text)