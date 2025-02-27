import logging
import logging.config
import csv
import datetime

class MyLogging():
    def __init__(self):
        with open('../config/logconfig.ini','r',encoding='utf-8') as f:
            logging.config.fileConfig(f)
        self.logger = logging.getLogger('root')

    def write(self,logmessage,loglevel):
        if loglevel=="DEBUG":
            self.logger.debug(f"{logmessage}")
        elif loglevel=="INFO":
            self.logger.info(f"{logmessage}")
        elif loglevel=="WARNING":
            self.logger.warning(f"{logmessage}")
        elif loglevel=="ERROR":
            self.logger.error(f"{logmessage}")
        elif loglevel=="CRITICAL":
            self.logger.critical(f"{logmessage}")

def init():
    with open("../logs/gpslog.csv","w") as f:
        pass
    with open("../logs/degree.csv","w") as f:
        pass

def forCSV(lat,lon):
    with open("../logs/gpslog.csv","a") as f:
        wrt = csv.writer(f)
        wrt.writerow([datetime.datetime.now(),lat,lon])
def forLATLON(temp1,temp2):
    with open("../logs/degree.csv","a") as f:
        wrt = csv.writer(f)
        wrt.writerow([datetime.datetime.now(),temp1,temp2])

def main():
    log = MyLogging()
    log.write("k-5","ERROR")

if __name__ == "__main__":
    main()
