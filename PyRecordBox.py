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
logger = logging.getLogger('PyRecordBox')
rbox = None
_rboxCallback = None

# callback function, call by record box dll.
def rboxCallback(uboxHnd, eventID, param1, param2, param3, param4):
    logger.debug('rboxCallback called')
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
        global host, port , rbox
        logger.info('PyRecordBox is running...')
        
        rbox = self
        print rbox

        self.rbox = RecordBox()
        _rboxCallback = self.rbox.makeCallback(rboxCallback)
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
            print '�豸���� id:', eventID
            logger.info("�豸���룬id: %d" %eventID)
        elif eventID == 2:
            print '�豸���� id:', eventID
            logger.info("�豸������id: %d" %eventID)
        elif eventID == 3:
            print '�豸���� id:', eventID
            logger.info("�豸������id: %d" %eventID)
        elif eventID == 10:
            print '�豸��λ id:', eventID
            logger.info("�豸��λ��id: %d" %eventID)
        elif eventID == 11:
            print '�豸���� id:', eventID
            logger.info("�豸���壬id: %d" %eventID)
        elif eventID == 12:
            print '�豸ժ�� id:', eventID
            logger.info("�豸ժ����id: %d" %eventID)
        elif eventID == 13:
            print '��·���� id:', eventID
            logger.info("��·���գ�id: %d" %eventID)
        elif eventID == 15:
            print '����ȡ�� id:', eventID
            logger.info("����ȡ����id: %d" %eventID)
        elif eventID == 21:
            print '�������� id:', eventID
            logger.info("�������У�id: %d" %eventID)
            callid = cast(param1, c_char_p)
            print callid.value
            logger.info("�������У�id: %d" %eventID)
            self.broadcast(callid.value)
        elif eventID == 22:
            print '�����¼� id:', eventID
            print param1
            logger.info("�����¼���id: %d" %eventID)
        elif eventID == 30:
            print '�豸�һ� id:', eventID
            logger.info("�豸�һ���id: %d" %eventID)
        elif eventID == 31:
            print '�豸ͣ�� id:', eventID
            logger.info("�豸ͣ��id: %d" %eventID)
        else:
            print eventID
            logger.info("�����¼���id: %d" %eventID)

    def broadcast(self, message):
        self.server.manager.broadcast(message)

if __name__ == '__main__':
    try:
        configLogger()
        readConfig()
        prb = PyRecordBox()
        prb.run()
    except KeyboardInterrupt:
        prb.rbox.close_logfile()
        prb.rbox.close()
#        rbox.closeUbox() 
#        api.ubox_close()
