import configparser

class Config_reader():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('../config/cansat.ini', encoding='utf-8')

    def reader(self,key,value,style):
        var = self.config.get(key,value)
        if style == "intenger":
            var = int(var,0)
        return var