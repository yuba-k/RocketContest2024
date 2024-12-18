import logging
import logging.config

class MyLogging():
    def __init__(self):
        with open('../config/logconfig.ini','r',encoding='utf-8') as f:
            logging.config.fileConfig(f)
        self.logger = logging.getLogger('root')

    def write(logmessage,loglevel):
        if loglevel=="DEBUG":
            logger.debug(f"{logmessage}")
        elif loglevel=="INFO":
            logger.info(f"{logmessage}")
        elif loglevel=="WARNING":
            logger.warning(f"{logmessage}")
        elif loglevel=="ERROR":
            logger.error(f"{logmessage}")
        elif loglevel=="CRITICAL":
            logger.critical(f"{logmessage}")

def main():
    log = MyLogging()
    log.write("k-5","ERROR")

if __name__ == "__main__":
    main()