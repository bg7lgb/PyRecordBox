#-*- coding:utf-8 -*-

""" PyRecordBox.py """

import sys
from ctypes import *
import ConfigParser, logging
from logging.handlers import RotatingFileHandler

from wsgiref.simple_server import make_server
from ws4py.server.wsgirefserver import WSGIServer, WebSocketWSGIRequestHandler
from ws4py.server.wsgiutils import WebSocketWSGIApplication

from PhoneWebSocket import PhoneWebSocket
    
host = ''
port = 0
logger = logging.getLogger('PyRecordBox')

def configLogger():
    handler = RotatingFileHandler('PyRecordBox.log', maxBytes=10000000, backupCount = 5) 
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger = logging.getLogger('PyRecordBox')
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    return logger
   
def readConfig():
    global host, port, logger
    config = ConfigParser.ConfigParser()
    config.read('PyRecordBox.ini')
    host = config.get('websocket', 'host')
    port = int(config.get('websocket', 'port'))
    level = config.get('log', 'level')

    if level == 'INFO':
        logger.setLevel(logging.INFO)
    elif level == 'WARNING':
        logger.setLevel(logging.WARNING)
    elif level == 'DEBUG':
        logger.setLevel(logging.DEBUG)
    elif level == 'ERROR':
        logger.setLevel(logging.ERROR)
    elif level == 'CRITICAL':
        logger.setLevel(logging.CRITICAL)
    else:
        logger.setLevel(logging.NOSET)

class PyRecordBox(object):
    def run(self):
        global host, port 
        logger.info('PyRecordBox is running...')
        
        self.server = make_server(host, port, server_class=WSGIServer,
            handler_class=WebSocketWSGIRequestHandler,
            app=WebSocketWSGIApplication(handler_cls=PhoneWebSocket))
        self.server.initialize_websockets_manager()
        self.server.serve_forever()

    def openDevice(self):
        pass

if __name__ == '__main__':
    configLogger()
    readConfig()
    ubox = PyRecordBox()
    ubox.run()

