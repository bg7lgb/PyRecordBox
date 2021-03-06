#-*- coding: utf-8 -*-

import sys, logging
from ctypes import *

rbox = None 
_rboxCallback = None

logger = logging.getLogger('PyRecordBox.Recordbox')
#logger = logging.getLogger('PyRecordBox.PhoneWebSocket')

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

        self.api.ubox_open.argtype = [self.c_rboxCallback, c_int]
        self.api.ubox_open.restype = c_int
       
        # ubox_open, second parameter is loglevel,
        # 0 --- log all message, 1-- log error and warning message only
        # loglevel这个参数好象不起作用
        rt = self.api.ubox_open(callback_func, c_int(0))
        if rt:
            logger.error('打开设备出错. 错误代码: %d' %rt)
            return False
        else:
            logger.info('打开设备成功.')

    def close(self):
        self.api.ubox_close()

    def open_logfile(self):
        self.api.ubox_open_logfile.argtype = [c_long]
        self.api.ubox_open_logfile.restype = None
        self.api.ubox_open_logfile(c_long(0))

    def close_logfile(self):
        self.api.ubox_close_logfile()
       
    def handleEvent(self, uboxHnd, eventID, param1, param2, param3, param4):
#        print eventID
        logger.info("eventID: %d" %eventID)

    def dial(self, uboxHnd, phone_no):
        """ 对传入的phone_no进行拨号，对于无软摘机功能的Fi3001B和Fi3002B，要手动摘机；
        对于有软摘机功能的Fi31001A和Fi3102A，直接软件拨号，但上层程序需要软摘机，延时1-2秒，
        再调用拨号 """
        self.api.ubox_send_dtmf.argtype = [c_ulong, c_char_p]
        self.api.ubox_send_dtmf.restype = c_int
        rt = self.api.ubox_send_dtmf(uboxHnd, phone_no)
        if rt:
            logger.error('拨号失败 %s' %phone_no)
        else:
            logger.info('拨号成功 %s' %phone_no)

if __name__ == "__main__":
    try:
        rbox = RecordBox()
        _rboxCallback = rbox.makeCallback(rboxCallback)
        rbox.open_logfile()
        rbox.open(_rboxCallback)
        a = input()
    except KeyboardInterrupt:
        rbox.close()
        rbox.close_logfile()
