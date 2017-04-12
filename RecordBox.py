#-*- coding: utf-8 -*-

import sys, logging
from ctypes import *

rbox = None 
_rboxCallback = None

logger = logging.getLogger('RecordBox')
logger = logging.getLogger('PyRecordBox.PhoneWebSocket')

# callback function, call by recordbox dll.
def rboxCallback(uboxHnd, eventID, param1, param2, param3, param4):
    logger.debug('rboxCallback called')
    if rbox:
        rbox.handleEvent(uboxHnd, eventID, param1, param2, param3, param4)

class RecordBox(object):
    def __init__(self):
        self.api = WinDLL('phonic_ubox.dll')

    def makeCallback(self, callback_func):
        self.c_rboxCallback = WINFUNCTYPE(None, c_ulong, c_int, c_ulong, c_ulong, c_ulong, c_ulong)       
        return self.c_rboxCallback(callback_func)

    def open(self, callback_func):
#        global _rboxCallback

        self.api.ubox_open.argtype = [self.c_rboxCallback, c_int]
        self.api.ubox_open.restype = c_int
       
        rt = self.api.ubox_open(callback_func, c_int(0))
        if rt:
            logger.error('open recordbox fail. error no: %d' %rt)
            return False
        else:
            logger.info('open recordbox success.')

    def close(self):
        self.api.ubox_close()

    def open_logfile(self):
        self.api.ubox_open_logfile.argtype = [c_long]
        self.api.ubox_open_logfile.restype = None
        self.api.ubox_open_logfile(c_long(0))

    def close_logfile(self):
        self.api.ubox_close_logfile()
       
    def handleEvent(self, uboxHnd, eventID, param1, param2, param3, param4):
        print eventID
        logger.info("eventID: %d" %eventID)

if __name__ == "__main__":
    try:
        rbox = RecordBox()
        _rboxCallback = rbox.makeCallback(rboxCallback)
        rbox.open_logfile()
        rbox.open(_rboxCallback)
        a = raw_input()
    except KeyboardInterrupt:
        rbox.close()
        rbox.close_logfile()
