import json

class JsonWalker(object):

    def __init__(self):
        self.__version__ = "0.9.0"
        self.keys = []
        self.display = True
        self.indentChar = "--"


    def exploreDict(self, ddict : dict , indent : int):

        for k,v in ddict.items():

            self.keys.append((k,indent))

            if type(v) == list:
                self.exploreList(v, indent+1)

            elif type(v) == dict:
                self.exploreDict(v, indent+1)

            else:
                indents = self.indentChar * indent
                if self.display : print("%s %s : %s"%(indents, k, v))

    def exploreList(self, lst, indent):

        for elem in lst:

            if type(elem) == list:
                self.exploreList(elem, indent+1)
            
            elif type(elem) == dict:
                self.exploreDict(elem, indent+1)
            
            else:
                indents = self.indentChar * indent
            if self.display: print("%s %s"%(indents, elem))
    
    def exploreJson(self, jsonDict):
        
        if type(jsonDict) == list:
            for subDict in jsonDict:
                self.exploreDict(subDict, 0)
        else:
            self.exploreDict(jsonDict, 0)

    def extractuniqueKeys(self, jsonDict):
        self.display = False
        self.exploreJson(jsonDict)
        self.display = True
        return set(self.keys)

    