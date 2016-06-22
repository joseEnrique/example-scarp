import urlparse


from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.item import Item, Field
import pdb

from dateutil.parser import parse




class MemberItem(Item):
    name = Field()
    second_name = Field()
    avatar = Field()
    group = Field()
    email = Field()
    web = Field()
    twitter= Field()
    division= Field()
    inscription_date = Field()
    termination_date = Field()
    party_name = Field()
    party_logo = Field()





class MemberSpider(CrawlSpider):
    name = 'members'
    allowed_domains = ['congreso.es', ]
    start_urls = ['http://www.congreso.es/portal/page/portal/Congreso'
                           '/Congreso/Diputados?_piref73_1333056_73_1333049_13'
                           '33049.next_page=/wc/menuAbecedarioInicio&tipoBusqu'
                           'eda=completo&idLegislatura=10' ]

    rules = []
    rules.append(
            Rule(LinkExtractor(
                allow=['fichaDiputado\?idDiputado=\d+&idLegislatura=10'], unique=True),
                       callback='parse_member'))
    rules.append(
            Rule(LinkExtractor(
                allow=['busquedaAlfabeticaDiputados&paginaActual=\d+&idLeg'
                       'islatura=10'
                       '&tipoBusqueda=completo'], unique=True), follow=True))







    def parse_member(self, response):
        x = HtmlXPathSelector(response)


        # extract full name of member
        names = x.select('//div[@class="nombre_dip"]/text()').extract()
        # extra text like member's state
        curriculum = x.select('//div[@class="texto_dip"]/ul/li/div[@class="dip'
                              '_rojo"]')

        # email, twitter ....
        extra_data = x.select('//div[@class="webperso_dip"]/div/a/@href')
        avatar = x.select('//div[@id="datos_diputado"]/p[@class="logo_g'
                          'rupo"]/img[@name="foto"]/@src').extract()

        item = MemberItem()

        if names:
            second_name, name = names[0].split(',')
            item['name'] = name.strip()
            item['second_name'] = second_name.strip()
            if avatar:
                item['avatar'] = 'http://www.congreso.es' + avatar[0]
            if curriculum:
                state = curriculum.re('(?<=Diputad[ao] por)[\s]*[\w\s]*')
                if state:
                    item['division'] = state[0].strip()
                group = curriculum.select('a/text()')
                prueba = x.select('//div[@id="datos_diputado"]/p[@cl'
                                            'ass="logo_grupo"]/a/img/@src').\
                                            extract()[0]
                #pdb.set_trace()
                if group:
                    # url is in list, extract it
                    item['group'] = group.extract()[0]
                    item['party_logo'] = 'http://www.congreso.es' + x.select('//div[@id="datos_diputado"]/p[@cl'
                                            'ass="logo_grupo"]/a/img/@src').\
                                            extract()[0]
                    item['party_name'] = x.select('//div[@id="datos_diputado"]/p[@clas'
                                          's="nombre_grupo"]/text()').extract()[0]


                    # add dates of inscription and termination
                    ins_date = curriculum.re('(?i)(?<=fecha alta:)[\s]*[\d\/]*')
                    if ins_date:
                        item['inscription_date'] = parse\
                                                   (ins_date[0], dayfirst=True)
                    term_date = curriculum.re('(?i)(?<=caus\xf3 baja el)[\s]*['
                                             '\d\/]*')
                    if term_date:
                        item['termination_date'] = parse\
                                                 (term_date[0], dayfirst=True)

            if extra_data:
                web_data = x.select('//div[@class="webperso_dip"]/div[@class="'
                                    'webperso_dip_parte"]/a/@href')
                if web_data:
                    web = web_data.re('[http|https]*://.*')
                    if web:
                        item['web'] = web[0]
                email = extra_data.re('mailto:[\w.-_]*@[\w.-_]*')
                if email:
                    item['email'] = email[0].replace('mailto:', '')
                twitter = extra_data.re('[http|https]*://(?:twitter.com)/[\w]*')
                if twitter:
                    item['twitter'] = twitter[0]

        return item

