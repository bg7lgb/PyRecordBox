#-*- coding:utf-8 -*-

from tkinter import *           
import sys, time

class App():
    def __init__(self, master):
        
        message = StringVar()

        # 已接电话 
        Label(master, text = "已接电话").grid(row=0,column=0)

        lb_answered = Listbox(master)
        scr_answered = Scrollbar(master)
        lb_answered.configure(yscrollcommand=scr_answered.set)
        scr_answered['command'] = lb_answered.yview
        lb_answered.grid(row=1, column=0, sticky=W, padx=2)
        scr_answered.grid(row=1, column=1, sticky=N+S )

        # 未接电话
        Label(master, text = "未接电话").grid(row=0,column=2)

        lb_missed = Listbox(master)
        scr_missed = Scrollbar(master)
        lb_missed.configure(yscrollcommand=scr_missed.set)
        scr_missed['command'] = lb_missed.yview
        lb_missed.grid(row=1, column=2, sticky=E, padx=2)
        scr_missed.grid(row=1, column=3, sticky=N+S )



        cb_call = Button(master, text ="回拨", command = self.dial)
        cb_exit = Button(master, text ="退出", command = self.exit)

        cb_call.grid(row = 2, column=0, pady = 2)
        cb_exit.grid(row = 2, column=2, pady = 2)

        statusbar = Label(master, text ="录音机", border=1,anchor=W,\
            relief=SUNKEN,textvariable=message)
        statusbar.grid(row = 3, columnspan=4, sticky=W+E)


    def dial(self):
        print("dial")

    def exit(self):
        sys.exit(0)


if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop()
        
