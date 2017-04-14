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
from RecordBox import RecordBox

host = ''
port = 0
uboxlog = 0
logger = logging.getLogger('PyRecordBox')
rbox = None
_rboxCallback = None

# callback function, call by record box dll.
def rboxCallback(uboxHnd, eventID, param1, param2, param3, param4):
    if rbox:
        rbox.handleEvent(uboxHnd, eventID, param1, param2, param3, param4)

def configLogger():
    handler = RotatingFileHandler('PyRecordBox.log', maxBytes=10000000, backupCount = 5) 
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger = logging.getLogger('PyRecordBox')
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    return logger
   
def readConfig():
    global host, port, logger, uboxlog
    config = ConfigParser.ConfigParser()
    config.read('PyRecordBox.ini')
    host = config.get('websocket', 'host')
    port = int(config.get('websocket', 'port'))
    level = config.get('log', 'level')
    uboxlog = int(config.get('log','uboxlog'))

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
        global host, port , rbox, uboxlog
        logger.info('PyRecordBox is running...')
        
        rbox = self

        self.rbox = RecordBox()
        _rboxCallback = self.rbox.makeCallback(rboxCallback)

        if uboxlog:
            self.rbox.open_logfile()

        self.rbox.open(_rboxCallback)

        try:
            self.server = make_server(host, port, server_class=WSGIServer,
                handler_class=WebSocketWSGIRequestHandler,
                app=WebSocketWSGIApplication(handler_cls=PhoneWebSocket))
            self.server.initialize_websockets_manager()
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.rbox.close()
            self.rbox.close_logfile()

    def handleEvent(self, uboxHnd, eventID, param1, param2, param3, param4):
        if eventID == 1:
            print u'设备插入 id:', eventID
            logger.info(u"设备插入 id: %d" %eventID)
        elif eventID == 2:
            print u'设备拨出 id:', eventID
            logger.info(u"设备拨出 id: %d" %eventID)
        elif eventID == 3:
            print u'设备报警 id:', eventID
            logger.info(u"设备报警 id: %d" %eventID)
        elif eventID == 10:
            print u'设备复位 id:', eventID
            logger.info(u"设备复位 id: %d" %eventID)
        elif eventID == 11:
            print u'设备振铃 id:', eventID
            logger.info(u"设备振铃 id: %d" %eventID)
        elif eventID == 12:
            print u'设备摘机 id:', eventID
            logger.info(u"设备摘机 id: %d" %eventID)
        elif eventID == 13:
            print u'线路悬空 id:', eventID
            logger.info(u"线路悬空 id: %d" %eventID)
        elif eventID == 15:
            print u'振铃取消 id:', eventID
            logger.info(u"振铃取消 id: %d" %eventID)
        elif eventID == 21:
            print u'来电号码 id:', eventID
            logger.info(u"来电号码 id: %d" %eventID)
            callid = cast(param1, c_char_p)
            print callid.value
            logger.info(u"来电号码id: %d" %eventID)
            self.broadcast(callid.value)
        elif eventID == 22:
            print u'按键事件 id:', eventID
            print param1
            logger.info(u"按键事件 id: %d" %eventID)
        elif eventID == 30:
            print u'设备挂机 id:', eventID
            logger.info(u"设备挂机id: %d" %eventID)
        elif eventID == 31:
            print u'设备停振 id:', eventID
            logger.info(u"设备停振 id: %d" %eventID)
        else:
            print eventID
            logger.info(u"其它事件 id: %d" %eventID)

    def broadcast(self, message):
        """ send message to all connected clients"""
        self.server.manager.broadcast(message)

if __name__ == '__main__':
    try:
        configLogger()
        readConfig()
        prb = PyRecordBox()
        prb.run()
    except KeyboardInterrupt:
        if uboxlog:
            prb.rbox.close_logfile()
        prb.rbox.close()
