#
# from PyQt5 import uic, QtWidgets
# from PyQt5.QtWidgets import QDialog
#
#
# form_class = uic.loadUiType("./UI/login.ui")[0]
#
# from pywinauto import application
# import time
# import os
#
# os.system('taskkill /IM coStarter* /F /T')
# os.system('taskkill /IM CpStart* /F /T')
# os.system('taskkill /IM DibServer* /F /T')
# os.system('wmic process where "name like \'%coStarter%\'" call terminate')
# os.system('wmic process where "name like \'%CpStart%\'" call terminate')
# os.system('wmic process where "name like \'%DibServer%\'" call terminate')
# time.sleep(5)
#
# app = application.Application()
# app.start('C:\CREON\STARTER\coStarter.exe /prj:cp /id:lwj7713 /pwd:dn6974! /pwdcert:dnwls7713! /autostart')
# time.sleep(60)

from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QDialog
import win32com.client
from pywinauto import application
import os
import time

form_class = uic.loadUiType("./ui/login.ui")[0]

class CustomDialog(QDialog, form_class):
    def __init__(self):
        super(CustomDialog, self).__init__()
        self.setupUi(self)


        # set initials values to widgets
        self.inputPw.setEchoMode(QtWidgets.QLineEdit.Password)
        self.inputCert.setEchoMode(QtWidgets.QLineEdit.Password)

    def getResults(self):
        if self.exec_() == QDialog.Accepted:
            # get all values
            val1 = self.inputId.text()
            val2 = self.inputPw.text()
            val3 =self.inputCert.text()
            return val1, val2,val3
        else:
            return None

class Auto_Login:
    def __init__(self):
        self.obj_CpUtil_CpCybos = win32com.client.Dispatch('CpUtil.CpCybos')

    def kill_client(self):
        os.system('taskkill /IM coStarter* /F /T')
        os.system('taskkill /IM CpStart* /F /T')
        os.system('taskkill /IM DibServer* /F /T')
        os.system('wmic process where "name like \'%coStarter%\'" call terminate')
        os.system('wmic process where "name like \'%CpStart%\'" call terminate')
        os.system('wmic process where "name like \'%DibServer%\'" call terminate')

    def connect(self, id_, pwd, pwdcert):
        if not self.connected():
            self.disconnect()
            self.kill_client()
            app = application.Application()
            app.start(
                'C:\CREON\STARTER\coStarter.exe /prj:cp /id: /pwd:! /pwdcert:! /autostart'.format(
                    id=id_, pwd=pwd, pwdcert=pwdcert
                )
            )
        while not self.connected():
            time.sleep(1)
        return True

    def connected(self):
        b_connected = self.obj_CpUtil_CpCybos.IsConnect
        if b_connected == 0:
            return False
        return True

    def disconnect(self):
        if self.connected():
            self.obj_CpUtil_CpCybos.PlusDisconnect()