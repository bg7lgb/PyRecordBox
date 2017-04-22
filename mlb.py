#-*-coding:utf-8 -*-

try:
    import Tkinter as tk
    import tkFont
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    import tkinter.font as tkFont
    import tkinter.ttk as ttk

import logging, time
from ctypes import *
from RecordBox import RecordBox
from PyRecordBox import configLogger, readConfig

rbox = None 
_rboxCallback = None
logger = logging.getLogger('PyRecordBox')

#logger = logging.getLogger('PyRecordBox.Recordbox')
#logger = logging.getLogger('PyRecordBox.PhoneWebSocket')

# callback function, call by recordbox dll.
def rboxCallback(uboxHnd, eventID, param1, param2, param3, param4):
    logger.debug('rboxCallback called')
    if rbox:
        rbox.handleEvent(uboxHnd, eventID, param1, param2, param3, param4)


class CallListBox(object):
    def __init__(self):
        global rbox, _rboxCallback

        self.tree = None
        self._setup_widgets()
        self._build_tree()
        
        self.call = ['','','']

        self.rbox = RecordBox()
        _rboxCallback = self.rbox.makeCallback(rboxCallback)
        self.rbox.open_logfile()
        self.rbox.open(_rboxCallback)

    def _setup_widgets(self):
        msg = ttk.Label(wraplength="4i", justify="left", anchor="n",
            padding=(10, 2, 10, 6), text=u"来电记录")
        msg.pack(fill='x')
        container = ttk.Frame()
        container.pack(fill='both', expand=True)

        self.call_header = [u'电话号码', u'时间', u'状态']

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

        btnDial = ttk.Button(text=u"拨号")
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
        root.destroy()

    def handleEvent(self, uboxHnd, eventID, param1, param2, param3, param4):
        if eventID == 1:
            self.displayMessage(u'设备插入 id:%d' %eventID)
            logger.info(u"设备插入 id: %d" %eventID)
        elif eventID == 2:
            self.displayMessage(u'设备拨出 id:%d' %eventID)
            logger.info(u"设备拨出 id: %d" %eventID)
        elif eventID == 3:
            self.displayMessage(u'设备报警 id:%d' %eventID)
            logger.info(u"设备报警 id: %d" %eventID)
        elif eventID == 10:
            self.displayMessage(u'设备复位 id:%d' %eventID)
            logger.info(u"设备复位 id: %d" %eventID)
        elif eventID == 11:
            self.displayMessage(u'设备振铃 id:%d' %eventID)
            logger.info(u"设备振铃 id: %d" %eventID)
        elif eventID == 12:
            self.displayMessage(u'设备摘机 id:%d' %eventID)
            logger.info(u"设备摘机 id: %d" %eventID)

            # 振铃时，收到摘机事件，表明已接听电话
            if self.status == 'ringing':
                self.call[2] = u'已接'
                # 修改来电状态为已接 
                self.tree.set(self.index, column=2, value=self.call[2])
        elif eventID == 13:
            self.displayMessage(u'线路悬空 id:%d' %eventID)
            logger.info(u"线路悬空 id: %d" %eventID)
        elif eventID == 15:
            self.displayMessage(u'振铃取消 id:%d' %eventID)
            logger.info(u"振铃取消 id: %d" %eventID)
           
            # 振铃时，收到振铃取消事件后，清空当前呼叫记录和状态
            if self.status=='ringing':
                self.call[0] = ''
                self.call[1] = ''
                self.call[2] = ''
                self.status  = ''

        elif eventID == 21:
            self.displayMessage(u'来电号码 id:%d' %eventID)
            logger.info(u"来电号码 id: %d" %eventID)

            callid = cast(param1, c_char_p)
            self.call[0] = callid.value
            self.call[1] = time.strftime('%Y-%m-%d %H:%M')
            self.call[2] = u'未接'
            self.status  = 'ringing'
            # 插入来电记录
            self.index = self.tree.insert('', index=0, values=self.call)

            self.displayMessage(u'来电号码 号码: %s' %callid.value)
            logger.info(u"来电号码 号码: %s" %callid.value)
            #self.broadcast(callid.value)

        elif eventID == 22:
            self.displayMessage(u'按键事件 id:%d' %eventID)
            logger.info(u"按键事件 id: %d" %eventID)
        elif eventID == 30:
            self.displayMessage(u'设备挂机 id:%d' %eventID)
            logger.info(u"设备挂机id: %d" %eventID)
            #收到设备挂机事件，清空当前呼叫记录和状态
            self.call[0] = ''
            self.call[1] = ''
            self.call[2] = ''
            self.status  = ''
        elif eventID == 31:
            self.displayMessage(u'设备停振 id:%d' %eventID)
            logger.info(u"设备停振 id: %d" %eventID)
        else:
            self.displayMessage(u'其它事件 id:%d' %eventID)
            logger.info(u"其它事件 id: %d" %eventID)


if __name__ == '__main__':
    configLogger()
    readConfig()

    root = tk.Tk()
    root.title(u"普罗米修斯来电管理程序")
    root.iconbitmap('call.ico')
    root.geometry("400x300")

    #listbox = CallListBox()
    rbox = CallListBox()
    if rbox:
        root.protocol("WM_DELETE_WINDOW", rbox.quit)
    root.mainloop()

