#-*- coding:utf-8 -*-

import sys, ctypes

@ctypes.CFUNCTYPE(None, ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong) 
def uboxCallback(uboxHnd, eventID, param1, param2, param3, param4):
    print uboxHnd, eventID

class PyRecordBox(object):
    def __init__(self):
        self.dll = None

    def readConfig(self):
        pass
    
    def uboxOpen(self):
        if self.dll:
            self.dll.ubox_open.restype = ctypes.c_int
            rt =  self.dll.ubox_open(uboxCallback, ctypes.c_int(0))
            if rt:
                print 'open device fail', rt
            else:
                print 'open device success'

    def uboxClose(self):
        if self.dll:
            self.dll.ubox_close()
        
        
    def run(self):
        self.dll = ctypes.WinDLL('phonic_ubox.dll')
        if not self.dll:
            print 'load phonic_ubox.dll failed.'
            sys.exit(1)
        self.uboxOpen()

        while True:
            cmd = raw_input('>')
            if cmd == 'quit':
                self.uboxClose()
                sys.exit(0)
            else:
                continue

if __name__ == "__main__":
    box = PyRecordBox()
    box.run()
