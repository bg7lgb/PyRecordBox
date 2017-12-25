#-*-coding:utf-8 -*-
"""
    WinRecordBox.py -- PyRecordBox的GUI版本
    1、提供来电显示，回拨功能。
    2、来电号码可通过websocket向客户端广播，用于与应用系统集成，进行弹屏显示。
    author: bg7lgb@gmail.com
"""
try:
    import Tkinter as tk
    import tkFont
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    import tkinter.font as tkFont
    import tkinter.ttk as ttk

import logging, time, json
import threading, ConfigParser
from logging.handlers import RotatingFileHandler
from ctypes import *
from wsgiref.simple_server import make_server
from ws4py.server.wsgirefserver import WSGIServer, WebSocketWSGIRequestHandler
from ws4py.server.wsgiutils import WebSocketWSGIApplication

#from PhoneWebSocket import PhoneWebSocket
import PhoneWebSocket
from RecordBox import RecordBox

host = ''
port = 0
clbox = None 
_rboxCallback = None
logger = logging.getLogger('PyRecordBox')


# callback function, call by recordbox dll.
def rboxCallback(uboxHnd, eventID, param1, param2, param3, param4):
#    logger.debug('rboxCallback called')
    if clbox:
        clbox.handleEvent(uboxHnd, eventID, param1, param2, param3, param4)

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

class CallListBox(object):
    def __init__(self):
        global rbox, _rboxCallback, host, port

        self.tree = None
        self._setup_widgets()
        self._build_tree()
        
        self.call = ['','','','']

        # 第一条线路的handle，第二条线路的handle比它增加1
        self.uboxHnd  = -1

        self.rbox = RecordBox()
        _rboxCallback = self.rbox.makeCallback(rboxCallback)
        self.rbox.open_logfile()
        self.rbox.open(_rboxCallback)

        # 录音盒的线路
        # line_no,也就是uboxHnd句柄，用来标识不同的线路
        # 目前程序只能支持1路和2路的设备
        self.lines = [{"uboxHnd":-1, "line_no":-1, "event":"", "call_id":"", "status":""}, 
            {"uboxHnd":-1, "line_no":-1, "event":"", "call_id":""}]

        self.server = make_server(host, port, server_class=WSGIServer, 
#        self.server = make_server('127.0.0.1', 9000, server_class=WSGIServer, 
            handler_class=WebSocketWSGIRequestHandler,
            app=WebSocketWSGIApplication(handler_cls=PhoneWebSocket.PhoneWebSocket))
        self.server.initialize_websockets_manager()

        self.svr_thread = threading.Thread(target=self.server.serve_forever)
        self.svr_thread.setDaemon(True)
        self.svr_thread.start()
#        threading.Thread(target=self.server.serve_forever).start()

    def _setup_widgets(self):
        msg = ttk.Label(wraplength="4i", justify="left", anchor="n",
            padding=(10, 2, 10, 6), text=u"来电记录")
        msg.pack(fill='x')
        container = ttk.Frame()
        container.pack(fill='both', expand=True)

        self.call_header = [u'线路', u'电 话 号 码', u'来 电 时 间', u'状态']

        # create a treeview with dual scrollbars
        self.tree = ttk.Treeview(columns=self.call_header, show="headings")
        vsb = ttk.Scrollbar(orient="vertical",
            command=self.tree.yview)
        hsb = ttk.Scrollbar(orient="horizontal",
            command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set,
            xscrollcommand=hsb.set)
        self.tree.grid(column=0, row=0, sticky='nsew', in_=container)
        vsb.grid(column=1, row=0, sticky='ns', in_=container)
        hsb.grid(column=0, row=1, sticky='ew', in_=container)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

        btnDial = ttk.Button(text=u"拨号", command=self.dial)
        btnDial.grid(column = 0, row = 2, in_=container)

        self.statusBar = ttk.Label(text=u"", justify='left',relief='sunken') 
        self.statusBar.grid(column=0, row = 3, sticky='we', columnspan=2, in_=container)


    def _build_tree(self):
        for col in self.call_header:
            self.tree.heading(col, text=col.title(),
                command=lambda c=col: sortby(self.tree, c, 0))
            # adjust the column's width to the header string
            self.tree.column(col,
                width=tkFont.Font().measure(col.title()))

    def displayMessage(self, message):
        self.statusBar['text'] = message

    def quit(self):
        global root
        self.rbox.close()
        self.rbox.close_logfile()
        self.server.manager.close_all()
        root.destroy()

    def dial(self):
        '''从下拉列表中选中一条记录进行拨号'''
        index = self.tree.selection()
        item = self.tree.item(index)
        line = item['values'][0]
        phone_no = str(item['values'][1])
        self.dialout(line, phone_no)
#        self.rbox.dial(self.uboxHnd, phone_no)

    def dialout(self, line, phone_no):
        '''将phone_no从录音盒的指定line外呼'''
        logger.debug(u'线路 %d 拨号 %s' %(line, phone_no))
#        self.rbox.dial(self.uboxHnd, phone_no)
#        self.rbox.dial(line, phone_no)
        self.rbox.dial(self.lines[line-1]["uboxHnd"], phone_no)

    def handleEvent(self, uboxHnd, eventID, param1, param2, param3, param4):
#        self.uboxHnd = uboxHnd
        message = {}
        if eventID == 1:
            #第一次收到事件，把第一条线路的handle保存起来
            if self.uboxHnd == -1:
                self.uboxHnd = uboxHnd
            self.lines[uboxHnd - self.uboxHnd]["uboxHnd"] = uboxHnd
            self.lines[uboxHnd - self.uboxHnd]["line_no"] = uboxHnd - self.uboxHnd + 1
            self.lines[uboxHnd - self.uboxHnd]["call_id"] = ""
            self.lines[uboxHnd - self.uboxHnd]["event"] = "plug_in"
            #print uboxHnd
            #print self.lines
            self.displayMessage(u'线路 %d 设备插入 id:%d' %(self.lines[uboxHnd-self.uboxHnd]["line_no"],eventID))
            logger.debug(u"线路 %d 设备插入 id: %d" %(self.lines[uboxHnd-self.uboxHnd]["line_no"], eventID))
            message['event']='plug_in'
        elif eventID == 2:
            if self.uboxHnd != -1:
                self.uboxHnd = -1;
            self.lines[uboxHnd - self.uboxHnd]["uboxHnd"] = -1
            self.lines[uboxHnd - self.uboxHnd]["line_no"] = -1
            self.lines[uboxHnd - self.uboxHnd]["call_id"] = ""
            self.lines[uboxHnd - self.uboxHnd]["event"] = "plug_out"
            
            self.displayMessage(u'线路 %d 设备拨出 id:%d' %(self.lines[uboxHnd-self.uboxHnd]["line_no"], eventID))
            logger.debug(u"线路 %d 设备拨出 id: %d" %(self.lines[uboxHnd-self.uboxHnd]["line_no"], eventID))
            message['event']='plug_out'
        elif eventID == 3:
            self.lines[uboxHnd - self.uboxHnd]["event"] = "alarm"
            self.displayMessage(u'线路 %d 设备报警 id:%d' %(self.lines[uboxHnd-self.uboxHnd]["line_no"], eventID))
            logger.debug(u"线路 %d 设备报警 id: %d" %(self.lines[uboxHnd-self.uboxHnd]["line_no"], eventID))
            message['event']='alarm'
        elif eventID == 10:
            self.lines[uboxHnd - self.uboxHnd]["event"] = "reset"
            self.displayMessage(u'线路 %d 设备复位 id:%d' %(self.lines[uboxHnd-self.uboxHnd]["line_no"], eventID))
            logger.debug(u"线路 %d 设备复位 id: %d" %(self.lines[uboxHnd-self.uboxHnd]["line_no"], eventID))
            message['event']='reset'
        elif eventID == 11:
            self.lines[uboxHnd - self.uboxHnd]["event"] = "ringing"
            self.displayMessage(u'线路 %d 设备振铃 id:%d' %(self.lines[uboxHnd-self.uboxHnd]["line_no"], eventID))
            logger.debug(u"线路 %d 设备振铃 id: %d" %(self.lines[uboxHnd-self.uboxHnd]["line_no"], eventID))
            message['event']='ringing'
        elif eventID == 12:
            self.lines[uboxHnd - self.uboxHnd]["event"] = "offhook"
            self.displayMessage(u'线路 %d 设备摘机 id:%d' %(self.lines[uboxHnd-self.uboxHnd]["line_no"], eventID))
            logger.debug(u"线路 %d 设备摘机 id: %d" %(self.lines[uboxHnd-self.uboxHnd]["line_no"], eventID))
            message['event']='offhook'

            # 振铃时，收到摘机事件，表明已接听电话
            if self.lines[uboxHnd-self.uboxHnd]["status"] == "ringing":
            #if self.status == 'ringing':
                self.call[3] = u'已接'
                # 修改来电状态为已接 
                self.tree.set(self.index, column=3, value=self.call[3])
        elif eventID == 13:
            self.lines[uboxHnd - self.uboxHnd]["event"] = "dangling"
            self.displayMessage(u'线路 %d 线路悬空 id:%d' %(self.lines[uboxHnd-self.uboxHnd]["line_no"], eventID))
            logger.debug(u"线路 %d 线路悬空 id: %d" %(self.lines[uboxHnd-self.uboxHnd]["line_no"], eventID))
            message['event']='dangling'
        elif eventID == 15:
            self.lines[uboxHnd - self.uboxHnd]["event"] = "ring_cancel"
            self.displayMessage(u'线路 %d 振铃取消 id:%d' %(self.lines[uboxHnd-self.uboxHnd]["line_no"], eventID))
            logger.debug(u"线路 %d 振铃取消 id: %d" %(self.lines[uboxHnd-self.uboxHnd]["line_no"], eventID))
            message['event']='ring_cancel'
           
            # 振铃时，收到振铃取消事件后，清空当前呼叫记录和状态
            if self.lines[uboxHnd-self.uboxHnd]["status"] == "ringing":
            #if self.status=='ringing':
                self.call = ['','','','']
                self.lines[uboxHnd-self.uboxHnd]["status"] = ""
                #self.status  = ''

        elif eventID == 21:
            self.displayMessage(u'线路 %d 来电 id:%d' %(self.lines[uboxHnd-self.uboxHnd]["line_no"], eventID))
            logger.debug(u"线路 %d 来电 id: %d" %(self.lines[uboxHnd-self.uboxHnd]["line_no"], eventID))

            callid = cast(param1, c_char_p)
            self.call[0] = self.lines[uboxHnd-self.uboxHnd]["line_no"]
            self.call[1] = callid.value
            self.call[2] = time.strftime('%Y-%m-%d %H:%M')
            self.call[3] = u'未接'
            #self.status  = 'ringing'
            self.lines[uboxHnd - self.uboxHnd]["status"] = "ringing"
            self.lines[uboxHnd - self.uboxHnd]["event"] = "caller_id"
            self.lines[uboxHnd - self.uboxHnd]["call_id"] = callid.value

            # 插入来电记录
            self.index = self.tree.insert('', index=0, values=self.call)

            self.displayMessage(u'线路 %d 来电号码 %s' %(self.lines[uboxHnd-self.uboxHnd]["line_no"], callid.value))
            logger.debug(u"线路 %d 来电号码 %s" %(self.lines[uboxHnd-self.uboxHnd]["line_no"], callid.value))

            message['event']='caller_id'
            message['phone_no'] = self.call[1]
#            self.server.manager.broadcast(self.call[0])

        elif eventID == 22:
            self.displayMessage(u'线路 %d 按键事件 id:%d' %(self.lines[uboxHnd-self.uboxHnd]["line_no"], eventID))
            logger.debug(u"线路 %d 按键事件 id: %d" %(self.lines[uboxHnd-self.uboxHnd]["line_no"], eventID))
            self.lines[uboxHnd - self.uboxHnd]["event"] = "dtmf"
            message['event']='dtmf'

        elif eventID == 30:
            self.displayMessage(u'线路 %d 设备挂机 id:%d' %(self.lines[uboxHnd-self.uboxHnd]["line_no"], eventID))
            logger.debug(u"线路 %d 设备挂机 id: %d" %(self.lines[uboxHnd-self.uboxHnd]["line_no"], eventID))
            message['event']='onhook'
            #收到设备挂机事件，清空当前呼叫记录和状态
            self.call = ['', '','','']
            self.lines[uboxHnd-self.uboxHnd]["status"] = ""
            self.lines[uboxHnd - self.uboxHnd]["event"] = "offhook"
            self.lines[uboxHnd - self.uboxHnd]["call_id"] = "" 
            #self.status  = ''
        elif eventID == 31:
            self.displayMessage(u'线路 %d 设备停振 id:%d' %(self.lines[uboxHnd-self.uboxHnd]["line_no"], eventID))
            logger.debug(u"线路 %d 设备停振 id: %d" %(self.lines[uboxHnd-self.uboxHnd]["line_no"], eventID))
            self.lines[uboxHnd - self.uboxHnd]["event"] = "ring_stop"
            message['event']='ring_stop'
        else:
            self.displayMessage(u'线路 %d 其它事件 id:%d' %(self.lines[uboxHnd-self.uboxHnd]["line_no"], eventID))
            logger.debug(u"线路 %d 其它事件 id: %d" %(self.lines[uboxHnd-self.uboxHnd]["line_no"], eventID))
            self.lines[uboxHnd - self.uboxHnd]["event"] = "others"
            message['event']='others'

        json_text = json.dumps(message)
        self.server.manager.broadcast(json_text)       


if __name__ == '__main__':
    configLogger()
    readConfig()

    root = tk.Tk()
    root.title(u"来电管理程序")
    root.iconbitmap('call.ico')
    root.geometry("400x300")

    #listbox = CallListBox()
    clbox = CallListBox()
    if clbox:
        root.protocol("WM_DELETE_WINDOW", clbox.quit)

    PhoneWebSocket.pws_app = clbox

    root.mainloop()


