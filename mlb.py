#-*-coding:utf-8 -*-

try:
    import Tkinter as tk
    import tkFont
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    import tkinter.font as tkFont
    import tkinter.ttk as ttk


class CallListBox(object):
    def __init__(self):
        self.tree = None
        self._setup_widgets()
        self._build_tree()
        self.displayMessage(u"开始")

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

#        for item in car_list:
#            self.tree.insert('', 'end', values=item)
#            # adjust column's width if necessary to fit each value
#            for ix, val in enumerate(item):
#                col_w = tkFont.Font().measure(val)
#                if self.tree.column(call_header[ix],width=None)<col_w:
#                    self.tree.column(call_header[ix], width=col_w)

    def displayMessage(self, message):
        self.statusBar['text'] = message



#car_list = [
#('Hyundai', 'brakes') 
#('Honda', 'light') ,
#('Lexus', 'battery') ,
#('Benz', 'wiper') ,
#('Ford', 'tire') ,
#('Chevy', 'air') ,
#('Chrysler', 'piston') ,
#('Toyota', 'brake pedal') ,
#('BMW', 'seat')
#]


if __name__ == '__main__':
    root = tk.Tk()
    root.title(u"普罗米修斯来电管理程序")
    root.iconbitmap('call.ico')
    listbox = CallListBox()
    root.mainloop()
  
