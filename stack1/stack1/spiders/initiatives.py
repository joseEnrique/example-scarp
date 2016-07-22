# -*- coding: utf-8 -*-
import re
import urlparse
import scrapy
from scrapy import Spider
from scrapy.selector import Selector
import pdb
from scrapy.contrib.linkextractors import LinkExtractor

from scrapy.item import Item, Field


class InitiativeItem(Item):
    ref = Field()
    title = Field()
    autor = Field()
    url = Field()
    A = Field()
    B = Field()
    D = Field()
    C = Field()
    DS = Field()
    tramitacion = Field()
    restramitacion = Field()




class StackSpider(Spider):

    #item = InitiativeItem()
    name = "initiatives"
    allowed_domains = ["http://www.congreso.es/","www.congreso.es"]
    start_urls = [
        "http://www.congreso.es/portal/page/portal/Congreso/Congreso/Iniciativas/Indice%20de%20Iniciativas",
    ]


    def parse(self, response):
        zsas = ""
        zsas = "http://www.congreso.es/portal/page/portal/Congreso/Congreso/Iniciativas?_piref73_2148295_73_1335437_1335437.next_page=/wc/servidorCGI&CMD=VERLST&BASE=IWI9&PIECE=IWI9&FMT=INITXD1S.fmt&FORM1=INITXLUS.fmt&DOCS=7-7&QUERY=%28I%29.ACIN1.+%26+%28121%29.SINI."
        yield scrapy.Request(zsas,callback=self.oneinitiative)


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
        #only one este tiene dos boletines
        #yield scrapy.Request("http://www.congreso.es/portal/page/portal/Congreso/Congreso/Iniciativas/Indice%20de%20Iniciativas?_piref73_1335503_73_1335500_1335500.next_page=/wc/servidorCGI&CMD=VERLST&BASE=IW11&PIECE=IWA1&FMT=INITXD1S.fmt&FORM1=INITXLUS.fmt&DOCS=5-5&QUERY=%28I%29.ACIN1.+%26+%28125%29.SINI.",callback=self.oneinitiative)

        #one with link
        #yield scrapy.Request("http://www.congreso.es/portal/page/portal/Congreso/Congreso/Iniciativas/Indice%20de%20Iniciativas?_piref73_1335503_73_1335500_1335500.next_page=/wc/servidorCGI&CMD=VERLST&BASE=IW11&PIECE=IWC1&FMT=INITXD1S.fmt&FORM1=INITXLUS.fmt&DOCS=1-1&QUERY=%28I%29.ACIN1.+%26+%28186%29.SINI.",callback=self.oneinitiative)

        #some
        #yield scrapy.Request("http://www.congreso.es/portal/page/portal/Congreso/Congreso/Iniciativas?_piref73_2148295_73_1335437_1335437.next_page=/wc/servidorCGI&CMD=VERLST&BASE=IW10&PIECE=IWD0&FMT=INITXD1S.fmt&FORM1=INITXLUS.fmt&DOCS=8-8&QUERY=%28I%29.ACIN1.+%26+%28005%29.SINI.",callback=self.oneinitiative)

        #yield scrapy.Request("http://www.congreso.es/portal/page/portal/Congreso/Congreso/Iniciativas/Indice%20de%20Iniciativas?_piref73_1335503_73_1335500_1335500.next_page=/wc/servidorCGI&CMD=VERLST&BASE=IW11&PIECE=IWA1&FMT=INITXD1S.fmt&FORM1=INITXLUS.fmt&DOCS=1-1&QUERY=%28I%29.ACIN1.+%26+%28080%29.SINI.",callback=self.oneinitiative)

        #ESTE DABA RUIDO
        #yield scrapy.Request("http://www.congreso.es/portal/page/portal/Congreso/Congreso/Iniciativas/Indice%20de%20Iniciativas?_piref73_1335503_73_1335500_1335500.next_page=/wc/servidorCGI&CMD=VERLST&BASE=IW11&PIECE=IWC1&FMT=INITXD1S.fmt&FORM1=INITXLUS.fmt&DOCS=25-25&QUERY=%28I%29.ACIN1.+%26+%28212%29.SINI.",callback=self.oneinitiative)


        #for i in range(1,int(num_inis[0])+1):
        #    new_url = split[0]+"&DOCS="+str(i)+"-"+str(i)+split[2]
        #    initiative_url = urlparse.urljoin(response.url, new_url)
        #    yield scrapy.Request(initiative_url,callback=self.oneinitiative)

    def oneinitiative(self,response):

        title = Selector(response).xpath('//p[@class="titulo_iniciativa"]/text()').extract()[0]
        expt = re.search('\(([0-9]{3}\/[0-9]{6})\)', title).group(1)

        #filter = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"]/text()')

        autors = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"\
         and contains(.,"Autor:") ]/following-sibling::\
        p[@class="apartado_iniciativa"][1]/preceding-sibling::p[preceding-sibling::p[contains(.,"Autor:")]]')

        ##DEPENDE DE DONDE ESTEN SITUADOS LOS BOLETINES
        #si no estan los ultimos
        bol = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"\
         and text()="Boletines:" ]/following-sibling::\
        p[@class="apartado_iniciativa"][1]/preceding-sibling::p[preceding-sibling::p[. = "Boletines:"]]')

        #si estan los ultimos
        bol1= Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"\
            and text()="Boletines:" ]/following-sibling::\
           p[@class="texto"]')


        ds = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"\
         and text()="Diarios de Sesiones:" ]/following-sibling::\
        p[@class="apartado_iniciativa"][1]/preceding-sibling::p[preceding-sibling::p[. = "Diarios de Sesiones:"]]')


        ds1 = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"\
            and text()="Diarios de Sesiones:" ]/following-sibling::\
           p[@class="texto"]')


        # para las tramitaciones
        tn = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"\
         and contains(.,"seguida por la iniciativa:") ]/following-sibling::\
        p[@class="apartado_iniciativa"][1]/preceding-sibling::p[preceding-sibling::p[contains(.,"seguida por la iniciativa:")]]')

        tn1 = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"\
            and contains(.,"seguida por la iniciativa:") ]/following-sibling::\
           p[@class="texto"]')

                # para resultado de las  tramitaciones
        restr = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"\
         and contains(.,"Resultado de la tramitac") ]/following-sibling::\
        p[@class="apartado_iniciativa"][1]/preceding-sibling::p[preceding-sibling::p[contains(.,"Resultado de la tramitac")]]')

        restr1 = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"\
            and contains(.,"Resultado de la tramitac") ]/following-sibling::\
           p[@class="texto"]')
        #para ponentes por si los hubiera

        pon = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"\
         and contains(.,"Ponentes:") ]/following-sibling::\
        p[@class="apartado_iniciativa"][1]/preceding-sibling::p[preceding-sibling::p[contains(.,"Ponentes:")]]')

        pon1 = Selector(response).xpath('//div[@class="ficha_iniciativa"]/p[@class="apartado_iniciativa"\
            and contains(.,"Ponentes:") ]/following-sibling::\
           p[@class="texto"]')


        #switch para saber si esta el ultimo o no
        boletines = None
        diarios = None
        tramitacion = None
        restramitacion= None
        ponentes = None

        if bol:
            boletines = bol
        elif not bol:
            boletines = bol1

        if ds:
            diarios = ds
        elif not ds:
            diarios = ds1

        if tn:
            tramitacion = tn
        elif not tn:
            tramitacion = tn1

        if restr:
            restramitacion = restr
        elif not restr:
            restramitacion = restr1

        if pon:
            ponentes = pon
        elif not pon:
            ponentes = pon1

    #######





        listautors=[]



        for autor in (autors):
            add = autor.xpath("a/b/text()").extract()
            if not add:
                add = autor.xpath("./text()").extract()[0]
            else:
                add= add[0]
            listautors.append(add)

        if ponentes:
            for ponente in ponentes:
                add = ponente.xpath("a/b/text()").extract()
                if not add:
                    try:
                        add = ponente.xpath("./text()").extract()[0]
                        listautors.append(add)
                    except:
                        pass
                else:
                    if add:
                        add= add[0]
                        listautors.append(add)


        item = InitiativeItem()

        item['ref'] = expt
        item['title'] = title
        item['url'] = response.url
        item['autor'] = listautors
        item["A"]=[]
        item["B"]=[]
        item["D"]=[]
        item["C"]=[]
        item["DS"]=[]
        if  tramitacion:
            #cogemos la ultima tramitacion
            tr = tramitacion.extract()[0].strip().split('<br>')[-1]
            item["tramitacion"]=tr
        if  restramitacion:
            #cogemos el ultimo resultado de la tramitacion
            rtr = restramitacion.extract()[0].strip().split('<br>')[-1]
            item["restramitacion"]=rtr

        #un boletin  es una lista con tipo y url
        if boletines or diarios:
            listurls=[]
            if boletines:

                for boletin in boletines:
                    text=boletin.xpath("text()").extract()
                    try:

                        serie= re.search('m. (.+?)-', text[0]).group(1)
                        haswordcongress = re.search('Congreso', text[0])

                    except:
                        serie = False
                        haswordcongress = False
                    url = boletin.xpath("a/@href").extract()

                    if serie and haswordcongress :
                        listserie =[]
                        listserie.append(serie)
                        listserie.append(url[0])
                        listurls.append(listserie)



                #se quita duplicadas
                #listurls= list(set(listurls))
            if diarios:



                for diario in diarios:
                    text=diario.xpath("text()").extract()

                    url = diario.xpath("a/@href").extract()

                    if  re.search('Congreso', text[0]) :
                        listDS =[]
                        listDS.append("DS")
                        listDS.append(url[0])
                        listurls.append(listDS)




            if listurls:
                first_url = self.geturl(listurls[0])
                onlyserie = self.getserie(listurls[0])

                number = self.getnumber(first_url)
                self.delfirstelement(listurls)


                yield scrapy.Request(self.createUrl(response.url,first_url),callback=self.recursiveletters, dont_filter = True,
                                     meta={'pag': number, 'item':item,'urls':listurls, 'isfirst': True, 'next':False,
                                           'serie': onlyserie })
            else:
                yield item


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

        itemserie = response.meta['serie']

        pages = Selector(response).xpath('//a/@name').extract()

        #si tiene paginador lo descartamos
        descarte = Selector(response).xpath('//p[@class="texto_completo"]')




        try:
            firstopage = re.search('gina(.+?)\)', pages[0]).group(1)
        except:
            firstopage= "1"


        if pages and not (str(int(firstopage)-1)==number):
            #aqui se busca
            haspage = [ch for ch in pages if re.search('gina' + number + '\)', ch)]
        else:
            haspage = True




        if descarte :
            if listurls:
                first_url = self.geturl(listurls[0])
                onlyserie = self.getserie(listurls[0])

                number = self.getnumber(first_url)
                self.delfirstelement(listurls)
                yield scrapy.Request(self.createUrl(response.url,first_url),callback=self.recursiveletters,
                                 dont_filter = True,  meta={'pag': number, 'item':item,'urls':listurls,
                                                             'isfirst':isfirst ,'serie':onlyserie})
            else:

                yield item

        elif isfirst and not descarte:
            if haspage:
                if not listurls:
                    if itemserie=="A":
                        item["A"].append(self.searchpages(response, number,item["ref"]))
                    elif itemserie=="B":
                        item["B"].append(self.searchpages(response, number,item["ref"]))
                    elif itemserie=="D":
                        item["D"].append(self.searchpages(response, number,item["ref"]))
                    elif itemserie=="C":
                        item["C"].append(self.searchpages(response, number,item["ref"]))
                    elif itemserie=="DS":
                        item["DS"].append(self.searchDS(response, number,item["ref"]))

                    yield item


                else:

                    if itemserie=="A":
                        item["A"].append(self.searchpages(response, number,item["ref"]))
                    elif itemserie=="B":
                        item["B"].append(self.searchpages(response, number,item["ref"]))
                    elif itemserie=="D":
                        item["D"].append(self.searchpages(response, number,item["ref"]))
                    elif itemserie=="C":
                        item["C"].append(self.searchpages(response, number,item["ref"]))
                    elif itemserie=="DS":
                            item["DS"].append(self.searchDS(response, number,item["ref"]))

                    first_url = self.geturl(listurls[0])
                    onlyserie = self.getserie(listurls[0])

                    number = self.getnumber(first_url)
                    self.delfirstelement(listurls)


                    yield scrapy.Request(self.createUrl(response.url,first_url), callback=self.recursiveletters, dont_filter=True,
                                             meta={'pag': number, 'item': item, 'urls': listurls, 'isfirst': False,
                                                    'serie':onlyserie})
            #no tiene pagina
            else:
                if not listurls:

                    if itemserie=="A":
                        item["A"].append(self.searchpages(response, number,item["ref"]))
                    elif itemserie=="B":
                        item["B"].append(self.searchpages(response, number,item["ref"]))
                    elif itemserie=="D":
                        item["D"].append(self.searchpages(response, number,item["ref"]))
                    elif itemserie=="C":
                        item["C"].append(self.searchpages(response, number,item["ref"]))
                    elif itemserie=="DS":
                        item["DS"].append(self.searchDS(response, number,item["ref"]))
                    yield item
                else:
                    if itemserie=="A":
                        item["A"].append(self.searchpages(response, number,item["ref"]))
                    elif itemserie=="B":
                        item["B"].append(self.searchpages(response, number,item["ref"]))
                    elif itemserie=="D":
                        item["D"].append(self.searchpages(response, number,item["ref"]))
                    elif itemserie=="C":
                        item["C"].append(self.searchpages(response, number,item["ref"]))
                    elif itemserie=="DS":
                        item["DS"].append(self.searchDS(response, number,item["ref"]))
                    first_url = self.geturl(listurls[0])
                    onlyserie = self.getserie(listurls[0])

                    number = self.getnumber(first_url)
                    self.delfirstelement(listurls)

                    yield scrapy.Request(self.createUrl(response.url,first_url), callback=self.recursiveletters, dont_filter=True,
                                             meta={'pag': number, 'item': item, 'urls': listurls, 'isfirst': "a",
                                                    'serie':onlyserie})






                    #este es el que devuelve el objeto, cuando no quedan urls
                    # Este es el esencial
        elif not listurls and not isfirst and not descarte:
                if haspage:
                    if itemserie=="A":
                        item["A"].append(self.searchpages(response, number,item["ref"]))
                    elif itemserie=="B":
                        item["B"].append(self.searchpages(response, number,item["ref"]))
                    elif itemserie=="D":
                        item["D"].append(self.searchpages(response, number,item["ref"]))
                    elif itemserie=="C":
                        item["C"].append(self.searchpages(response, number,item["ref"]))
                    elif itemserie=="DS":
                        item["DS"].append(self.searchDS(response, number,item["ref"]))
                    yield item
                else:
                    yield item


        elif not descarte:
            if itemserie=="A":
                item["A"].append(self.searchpages(response, number,item["ref"]))
            elif itemserie=="B":
                item["B"].append(self.searchpages(response, number,item["ref"]))
            elif itemserie=="D":
                item["D"].append(self.searchpages(response, number,item["ref"]))
            elif itemserie=="C":
                item["C"].append(self.searchpages(response, number,item["ref"]))
            elif itemserie=="DS":
                item["DS"].append(self.searchDS(response, number,item["ref"]))

            first_url = self.geturl(listurls[0])
            onlyserie = self.getserie(listurls[0])

            number = self.getnumber(first_url)
            self.delfirstelement(listurls)
            yield scrapy.Request(self.createUrl(response.url,first_url),callback=self.recursiveletters,
                                 dont_filter = True,  meta={'pag': number, 'item':item,'urls':listurls,
                                                             'isfirst':False ,'serie':onlyserie})
        else:
            yield item


    def searchDS(self,response,number,ref):
        text = Selector(response).xpath('//div[@class="texto_completo"]').extract()
        return self.removeForDS(text[0])


    def searchpages(self,response, number, expt):

        pages = Selector(response).xpath('//a/@name').extract()
        haspage = [ch for ch in pages if re.search('gina' + number + '\)', ch)]
        if haspage:

            publications = self.extracttext(response, number,expt)

            return publications
        else:
            if number=="1":
                return self.extracttext(response, number,expt)
            else:

                try:
                    return "Error  "+number + " URL: "+response.url
                except:
                    return "ERROR"



    def extracttext(self,response,number,ref):
        textfragment = self.fragmenttxt(response,number)
        res = ""


        #Es el texto entero y no hay que fragmentar
        if not self.checkownRef(textfragment,ref):
            return self.removeHTMLtags(textfragment)

        diffexpt=re.findall('[0-9]{3}\/[0-9]{6}',textfragment)

        numexpt=re.findall(ref,textfragment)

        texto = self.extractbyref(textfragment,ref,number)
        pages = Selector(response).xpath('//a/@name').extract()
        numbers = []
            #bbusca mas texto
        for page in pages:
            num = self.getnumber(page)
            if int(num)> int(number):
                textfragment = self.fragmenttxt(response, num)
                texto += self.extractother(textfragment, ref)

                if not self.checkownRef(textfragment, ref) and self.checkotherRef(textfragment):
                    break
        res = self.removeHTMLtags(texto)




        return res



            #re.search('[0-9]{3}\/[0-9]{6}',textfragment)


    def extractbyref(self,text,ref, number=None):
        splittext = text.split("<br><br>")
        control = False
        result = []



        for line in splittext:
            if self.checkownRef(line,ref):
                control = True
            if not self.checkownRef(line, ref) and self.checkotherRef(line):
                control = False
            if control:
                result.append(line)



        return self.concatlist(result)


    def extractother(self,text,ref):
        splittext = text.split("<br><br>")
        control = True
        result = []


        for line in splittext:
            if control:
                result.append(line)
            if not self.checkownRef(line, ref) and self.checkotherRef(line):
                control = False



        return self.concatlist(result)






    def fragmenttxt(self, response,number):
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
            #if re.search("gina" + number + '\)', i):
            if self.checkPage(i,number):
                control = True
                continue
            elif int(number) < int(firstopage):
                control = True
            if control  and self.checkPage(i,str(int(number)+1)):
                break
            if control:
                result.append(i)


        return self.concatlist(result)

    #http://www.congreso.es/portal/page/portal/Congreso/Congreso/Iniciativas?_piref73_2148295_73_1335437_1335437.next_page=/wc/servidorCGI&CMD=VERLST&BASE=iwi6&FMT=INITXLTS.fmt&DOCS=1-50&DOCORDER=FIFO&OPDEF=Y&QUERY=%28I%29.ACIN1.


    def concatlist(self, list):
        if list:
            return '<br><br>'.join( elem for elem in list)
        else:
            return ''

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
        TAG_RE = re.compile(r'<[^>]+>')
        BLANK = re.compile(r'\n')
        text = TAG_RE.sub('', text)
        return BLANK.sub('', text)

    def removeForDS(self,text):
        TAG_RE = re.compile(r'<[^>]+>')
        BLANK = re.compile(r'\n')
        PAGES = re.compile(r'.*gina\n .*[0-9]\n\n')
        text = PAGES.sub('',text)
        text = TAG_RE.sub('', text)
        return BLANK.sub('', text)


    def checkPage(self, line, number):
        control = True
        regexps = ["gina" + number + '\)','name=']

        for rege in regexps:
            if not re.search(rege,line):
                control= False
                break
        return control
    def checkownRef(self, line, ref):
        control = True
        if not re.search(ref,line):
            control = False
        return control

    def checkotherRef(self, line):
        control = True
        if not re.search('[0-9]{3}\/[0-9]{6}',line):
            control = False

        return control

    def geturl(self,list):
        return list[1]


    def getserie(self, list):
        return list[0]

    def createUrl(self,base,href):
        url = urlparse.urljoin(base, href)
        return url

