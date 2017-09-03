# -*- coding: utf-8 -*-
import os, sys, time
import threading
from pywinauto.application import Application
from pywinauto import timings
from pywinauto import taskbar
import win32api, win32con
import win32com.client

import psutil
from bokeh.server import task
from pywinauto import taskbar

class Login(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.__suspend = False
        self.__exit = False


    def run(self):
        print("Auto Login Start")
        time.sleep(3)
        #C:\Users\Administrator\git\haedong\Haedong\Haedong\module\
        PROCNAME = "kfopcomms.exe"
        haedongPid = 0
        
        for proc in psutil.process_iter():
            if proc.name() == PROCNAME:
                print(proc.pid)
                haedongPid = proc.pid 
        
        
        app = Application().connect(process = haedongPid)
        
        title = "영웅문W Login"
        dlg = timings.WaitUntilPasses(20, 0.5, lambda: app.window_(title=title))
        
        pass_ctrl = dlg.Edit2
        pass_ctrl.SetFocus()
        pass_ctrl.TypeKeys('khj1342')
        
        pass_ctrl = dlg.Edit3
        pass_ctrl.SetFocus()
        pass_ctrl.TypeKeys('godqhr134@')
        
        btn_ctrl = dlg.Button0
        btn_ctrl.Click()
        
        self._stop()

    def _stop(self):
        self.__exit = True

def test():

    
    right_click(1710,1055)
    time.sleep(1)
    left_click(1750,1015)
    time.sleep(1)
    left_click(850,480)
    mouse_move(1000,600)
    time.sleep(1)
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys("4045") 
    time.sleep(1)
    left_click(1000,600)
    time.sleep(1)
    left_click(980,640)


    sys.exit()
        
def right_click(x,y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,x,y,0,0)
def left_click(x,y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)    

def mouse_move(x,y):
    win32api.SetCursorPos((x,y))


def init():
    _auto_login = Login()
    _auto_login.start()
   
if __name__ == "__main__":
    #test()
    #_auto_login = Login()
    #_auto_login.start()
    contract_cnt = 2
    if contract_cnt != 1 and contract_cnt  !=2:
        print("a")
    else:
        print('b')