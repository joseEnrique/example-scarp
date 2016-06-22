# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
from scrapy.item import Item, Field


class InitiativeItem(Item):
    title = Field()
    url = Field()
    autor = Field()



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
