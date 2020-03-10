import pandas as pd
import ast
import json
#from modules.JsonWalker import JsonWalker
from LargeJsonReader.modules import JsonWalker

class LargeJsonReader(object):
    """
    Python class. Allow to read and extract informations from very large Json file (size > 10Go).
    This class read character by characters and recogize elementary dictionary present in the json file.
    Its restitute there under a list of string interpratable as dictionaries.

    You can use this list of strings to create a normalize DataFrame or to save as mush lighter json file.
    
    Attributes: 
    - version : current version of the class
    - jsonFilePath (str): mandatory, the path of you very large json
    - encoding (str): mandatory, the encode type. Default utf-8
    - streamer (object): cursor use to read the json file.
    - char (str): current readed character.
    - result (list): the list which contain dictionaries under string format.
    - isEOF (bool): True if char is the last character of the file, False otherwise.

    EOF = End Of File

    Using:

    """
    def __init__(self, jsonFilePath: str = "", outputJsonFilePath: str = "", encoding: str = "utf-8"):
        self.__version__ = "0.9.0"
        self.jsonFilePath = jsonFilePath
        self.outputJsonFilePath = outputJsonFilePath
        self.encoding = encoding
        self.streamer = None
        self.char = ''

        self.limit = -1
        self.results = []
        self.isEOF: bool = False

    def _openStream(self):
        "Open the file and load if in 'streamer'"
        self.streamer = open(self.jsonFilePath, encoding=self.encoding)

    def _closeStream(self):
        "Close the streamer."
        self.streamer.close()

    def _EOF(self, char : str):
        "True if char = '', False otherwise"
        return True if char == '' else False

    def _popFirst(self):
        "Take the fist element of result and if '[' if present in the first place take the rest of the string"
        dtc = self.results[0]

        if dtc[0] == "[":
            dtc = dtc[1:]
            self.results[0] = dtc

    def _popLast(self):
        "Same as _popFirst but for the last element of the last dictionary"
        dtc = self.results[-1]

        if dtc[-1] == "]":
            dtc = dtc[:1]
            self.results[-1] = dtc

    def _cleanResultsList(self):
        "If an element if the result list is empty it wille be remove"
        for reccord in self.results:
            if reccord == '':
                popReccord = self.results.pop(self.results.index(reccord))

    def _readNextChar(self):
        "Read the next char in the file and check if is this is the last"
        self.char = self.streamer.read(1)
        self.isEOF = self._EOF(self.char)

    def readOneDict(self):
        """Use a stacking method to know if is the end of the current dictionary.        

        Inputs: None

        Outpus:
        - the current dictionary under a string format.
        """
        dictStack = []
        first = True
        i = 0
        temp = []
        out = ""
        canAdd = False

        if self.isEOF == False: # if is the last character the loop dont launch
            while len(dictStack) > 0 or first and self.isEOF == False:

                self._readNextChar()
                i+=1

                if self.char == "{":
                    first = False
                    canAdd = True
                    dictStack.append("{")
                elif self.char == "}":
                    dictStack.pop(-1)
                else:
                    pass

                if canAdd:
                    temp.append(self.char)

            out = "".join(e for e in temp)
            print(out)
        return out

    def _formatOutputJsonFileName(self, k : int = 999):
        spliting = self.outputJsonFilePath.split(".")
        out = "{0}_{1}.{2}".format(spliting[0],k,spliting[1])
        return out

    def readDict(self):
        "Read the dicionary flag by steamer and fill the 'results' list with each sub_dictionary under string format"
        self._openStream()
        k = 0 # counter

        while self.isEOF == False:

            self.results.append(self.readOneDict())
            k+=1

            if k == self.limit and self.isEOF == False:

                self._cleaning()

                tempOutputJsonFilePath = self._formatOutputJsonFileName(k)
                self.saveJsonFile(tempOutputJsonFilePath)
                k = 0

        self._closeStream()
        self._cleaning()

    def _cleaning(self):
        "Clean results and delete ('[', ']') characters. Usefull to have a clear ouput "
        self._cleanResultsList
        self._popFirst()
        self._popLast()

    def saveJsonFile(self, outputJsonFileName : str = "myJsonFile.jon"):
        
        dditc = self.toDict()

        outStreamer = open(outputJsonFileName, 'w', encoding= self.encoding)

        outStreamer.write(json.dumps(dditc))

        outStreamer.close()

    def toDict(self):
        "Return a dictionary which it contain all results."
        STR = ",".join(reccord for reccord in self.results)
        DTC = ast.literal_eval(STR)
        return DTC

    def _oneSTRtoDTC(self, STR : str):
        "Return the string in parameter as dictionary. Warning, the string must be a 'string convertible'"
        DTC = ast.literal_eval(STR)
        return DTC

    def extractFields(self):
        """Extract the field present in all dictionaries contain into 'results'.
            The format is:

            [(field1, level), (field2, level)....].
            Level 0 : keys at the high level of dictionary.
            And Level increment.
        
        """
        jw = JsonWalker.JsonWalker()

        keys = set(())
        for dtc in self.toDict():
            tmpKeys = ""
            tmpKeys = jw.extractuniqueKeys(dtc)
            for element in set(tmpKeys):
                keys.add(element)
        return keys

if __name__ == "__main__":
    
    jsonPath = "C:\\Users\\GDognin\\DATA\\Informatique\\Developpements_python\\json\\largeExample.json"

    print(jsonPath)
    ljr = LargeJsonReader(jsonPath, 'myJson.json')
    ljr.limit = 4

    ljr.readDict()