# -*- coding: utf-8 -*-
import re
import pdb

dicc = {

    u'Autorización de Convenios Internacionales': ["C","DS"],
    u'Comisión permanente':["D"],
    u'Competencias en relación con la Corona':["A"],



}





class Terms(object):
    @staticmethod
    def getDict():
        return dicc
    @staticmethod
    def getTypetext(key):
        return Terms.getDict()[key]
    @staticmethod
    def getKeys():
        return Terms.getDict().keys()
    @staticmethod
    def getValues():
        return Terms.getDict().values()

    @staticmethod
    def getType(string):
        return [type for type in Terms.getKeys() if re.search(type, string)][0]



    @staticmethod
    def filterBytype(string):
        res = False
        # elimino los art y demas
        newchain =  re.sub('( [\(|\{].*?.$)|(.$)', '' , string.strip())
        for type in Terms.getKeys():
            if re.match(newchain,type):

                res= True
                break
        return res

    @staticmethod
    def isTextvalid(type,serie):
        res = False
        values = Terms.getTypetext(type)
        for a in values:
            if re.search(a,serie):
                res = True
                break
        return res


    @staticmethod
    def whatisthis(s):
        if isinstance(s, str):
            print "ordinary string"
        elif isinstance(s, unicode):
            print "unicode string"
        else:
            print "not a string"
