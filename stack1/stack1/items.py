# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
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
    type = Field()
    tramitacion = Field()
    restramitacion = Field()
