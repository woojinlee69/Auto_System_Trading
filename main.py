# -*- coding:utf-8 -*-
import collections
import sys
import threading
import time
import webbrowser

import pandas as pd
from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import *

from AutoConnect import CustomDialog,Auto_Login
from myChart import MyPieChart
from candleChart import MyWindow

import handler
import AutoConnect

form_class = uic.loadUiType("./UI/mainWindow.ui")[0]

CONNECTED = False
TRIGGER_CONNECTED = False
TEST = False

PROGRESS_WIDTH =450
PROGRESS_HEIGHT = 15

STRATEGY_LIST = {}
CODE_LIST = {}

SUMMARY_NUMBERS = 0
SUMMARY_BUYCAL = 0
SUMMARY_ESTIMATECAL = 0
SUMMARY_PREAMOUNT = 0

class get_AccBalance_Runnable(QRunnable):
    def __init__(self,dialog):
        QRunnable.__init__(self)
        self.w = dialog

    def run(self):

        self.account_list = handler.Account_list()
        acc_balance = self.account_list.get_account_list()

        # 이전로직 종료된 후에 아래 메서드로 output 을 가지고 간다.
        QMetaObject.invokeMethod(self.w, "show_AccBalance",
                                 Qt.QueuedConnection,
                                 Q_ARG(dict, acc_balance))


# 로그인 스레드
class ThreadClass(QtCore.QThread):
    def __init__(self, id, pw, cert):
        super(ThreadClass, self).__init__()
        self.access = handler.access()
        self.id = id
        self.pw = pw
        self.cert = cert

    def run(self):
        if CONNECTED == True:
            QMessageBox.about(self, "Message", "크레온 플러스 로그인 중입니다.")
            return

        self.access.get_data_creon(self.id, self.pw, self.cert)
        self.access.login_creon()

# class ThreadClass1(QtCore.QThread):
#     def __init__(self):
#         super(ThreadClass1, self).__init__()
#         self.autologin = handler.autoLogin()
#         self.id = ""
#         self.pw = "!"
#         self.cert = "!"
#
#     def run(self):
#         if CONNECTED == True:
#             QMessageBox.about(self, "Message", "크레온 플러스 로그인 중입니다.")
#             return
#
#         self.autologin.get_data_creon(self.id, self.pw, self.cert)
#         self.autologin.login_creon()

class Form(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.access = handler.access()
        self.autoLogin = AutoConnect.Auto_Login()
        self.acc_control = handler.MarketEye()
        self.account_list = handler.Account_list()

        self.login_Creon.setAutoDefault(True)  # enable Enter key
        self.login_Creon.clicked.connect(self.loginCreon)
        self.pushButton_3.clicked.connect(self.logout)
        self.pushButton.clicked.connect(self.loginCreon)
        self.pieButton.clicked.connect(self.showChart)
        self.pushButton_4.clicked.connect(self.getAllStgList_clicked)
        self.pushButton_5.clicked.connect(self.getStgList_clicked)
        self.pushButton_6.clicked.connect(self.getAllStgList_uncheck_clicked)
        self.tableWidget_3.doubleClicked.connect(self.tableWidget_doubleClicked)
        self.checkBox.stateChanged.connect(self.checkBoxState)
        self.label_3.setText("검색 종목 개수 : ")

        self.showCurrentTime()
        self.showConnection()

        self.progress = QProgressBar(self)
        # self.progress.setGeometry(self.width()/2 - PROGRESS_WIDTH / 2,self.height()/2 - PROGRESS_HEIGHT / 2,
        #                           PROGRESS_WIDTH, PROGRESS_HEIGHT)
        self.progress.setGeometry(self.width()/2 - PROGRESS_WIDTH / 2 + 280,self.height()-25,
                                  PROGRESS_WIDTH, PROGRESS_HEIGHT)

        self.progress.setTextVisible(True)
        self.progress.setFormat('Loading...')
        self.progress.setMaximum(0)
        self.progress.hide()

    def auto_login(self):

        if (CONNECTED == True):
            QMessageBox.about(self, "Message", "크레온 플러스 이미 접속 중입니다.")
            return

        AutoConnect.Auto_Login()

        self.log('자동로그인 중입니다.')


    def loginCreon(self):

        if (CONNECTED == True):
            QMessageBox.about(self, "Message", "크레온 플러스 이미 접속 중입니다.")
            return

        w = CustomDialog()
        values = w.getResults()
        if values:
            id, pw, cert = values
        print("id : ", id, "pw : ", pw, "cert : ", cert)

        if id == '' or pw == '' or cert == '':
            QMessageBox.about(self, "Message", "모든 정보 입력 후 로그인 진행바랍니다.")
            return

        self.threadclass = ThreadClass(id, pw, cert)
        self.threadclass.start()
        self.log('로그인 중입니다.')

    # def loginCreon1(self):
    #
    #     if (CONNECTED == True):
    #         QMessageBox.about(self, "Message", "크레온 플러스 이미 접속 중입니다.")
    #         return
    #
    #     w = CustomDialog()
    #     values = w.getResults()
    #     if values:
    #         id, pw, cert = values
    #     print("id : ", id, "pw : ", pw, "cert : ", cert)
    #
    #     if id == '' or pw == '' or cert == '':
    #         QMessageBox.about(self, "Message", "모든 정보 입력 후 로그인 진행바랍니다.")
    #         return
    #
    #     self.threadclass = ThreadClass1(id, pw, cert)
    #     self.threadclass.start()
    #     self.log('로그인 중입니다.')


    # plot차트로 보기
    def showChart(self):
        nrows = self.tableWidget_2.rowCount()
        sname = []
        samount = []

        if nrows == 0:
            QMessageBox.about(self, "Message", "잔고 조회 후 진행바랍니다.")
            return

        # 보유테이블에서 가져오기
        for row in range(0, nrows):
            name = self.tableWidget_2.item(row, 1).text()
            amount = int(self.tableWidget_2.item(row, 7).text())
            sname.append(name)
            samount.append(amount)
        print("sname", sname)
        print("samount", samount)


        codelist = self.getCodeList()
        print("codelist", codelist)

        # 코스피/코스닥 데이터 가져오기
        smarket = []
        countKospi = 0
        for name in sname:
            stockname = codelist.loc[codelist['name'] == name, 'market'].iloc[0]
            smarket.append(stockname)
            if stockname == 'Kospi':
                countKospi = countKospi + 1
        print("smarket", smarket)

        # 데이터프레임 만들기
        zippedList = list(zip(smarket, sname, samount))
        print("zippedList", zippedList)
        zipdf = pd.DataFrame(zippedList, columns=['market', 'name', 'amount'])
        print('zipdf', zipdf)

        # 데이터 프레임 정렬하기
        zipdf.sort_values(by=['market', 'amount'], ascending=[False, False], inplace=True)
        print('sortzipdf', zipdf)

        # 필터
        kospi_color, kosdaq_color = self.makeColorArray(nrows)
        print('kospi_color', kospi_color)
        print('kosdaq_color', kosdaq_color)

        # 정리
        filtersum_df = zipdf.groupby('market').sum()[::-1]
        big_values = filtersum_df['amount'].tolist()
        big_values = list(map(int, big_values))
        big_colors = ['g', 'b']
        first_color = 'Greens'
        second_color = 'Blues'
        big_labels = ['거래소', '코스닥']
        small_values = zipdf['amount'].tolist()
        small_values = list(map(int, small_values))
        small_labels = zipdf['name'].tolist()

        splitindex = countKospi

        # 차트 만들기
        self.MW = MyPieChart()
        self.MW.initUI(big_values, big_colors, big_labels, small_values, small_labels, splitindex, first_color,
                       second_color)
        self.MW.show()
        self.log('분포차트 로딩 완료하였습니다.')

    def makeColorArray(self, n):
        self.green_sample = ['xkcd:salmon pink', 'xkcd:baby pink', 'xkcd:apple green']
        self.blue_sampe = ['xkcd:sky blue', 'xkcd:light blue', 'xkcd:reddish pink']

        self.gcolors = []
        self.bcolors = []
        for i in range(n):
            j = i % 3
            self.gcolors.append(self.green_sample[j])
            self.bcolors.append(self.blue_sampe[j])

        return self.gcolors, self.bcolors

    def showCurrentTime(self):
        if CONNECTED:
            conStatus = 'Server Connected'
        else:
            conStatus = 'Server Not Connected'
        self.statusBar().showMessage("현재 시간: " + QTime.currentTime().toString("hh:mm:ss") + " | " + conStatus)
        threading.Timer(1, self.showCurrentTime).start()

    def showConnection(self):
        global CONNECTED
        global TRIGGER_CONNECTED
        state = self.access.check_con()
        if state == 0:
            CONNECTED = False
            self.account_numbox.setText("미접속 상태")
            time.sleep(1.5)
            self.account_numbox.setText("")
        else:
            CONNECTED = True
            accounts = handler.Account_list
            self.account_numbox.setText("%s" % self.acc_control.get_acc_num())

            if TRIGGER_CONNECTED == False:
                self.log('로그인 완료하였습니다.')
                TRIGGER_CONNECTED = True

        threading.Timer(3, self.showConnection).start()

    def logout(self):
        buttonreply = QMessageBox.question(self, '크레온 API 연결', 'Creon 플러스 API 연결 해제하시겠습니까? ', QMessageBox.Yes,
                                           QMessageBox.No)
        global CONNECTED

        if buttonreply == QMessageBox.Yes:
            print("QMessageBox.Yes")
            self.access.disconnect()
            CONNECTED = False
            self.log('로그아웃 진행 중입니다.')
        else:
            pass

    def button_clicked(self):

        if CONNECTED == False:
            QMessageBox.about(self, "Message", "크레온 플러스 로그인 후 확인해 주십시오")
            return

        self.chk_AccBalance()


    def chk_AccBalance(self):
        acc_balance = {}

        acc_balance = {
            'A000020': {'종목코드': 'A000020', '종목명': '동화약품', '잔고수량': 9, '수익률': -29.8, '장부가': 11500.0, '평가금액': 72000,
                        '매입금액': 103500, '현재가': 8100, '대비': 2.5},
            'A000225': {'종목코드': 'A000225', '종목명': '유유제약1우', '잔고수량': 12, '수익률': -19.0, '장부가': 8557.0, '평가금액': 83000,
                        '매입금액': 102684, '현재가': 6950, '대비': 0.6},
            'A000270': {'종목코드': 'A000270', '종목명': '기아차', '잔고수량': 3, '수익률': 18.7, '장부가': 33951.0, '평가금액': 120000,
                        '매입금액': 101853, '현재가': 40400, '대비': -0.9}}



        if TEST == False:

            self.progress.show()

            runnable = get_AccBalance_Runnable(self)
            QThreadPool.globalInstance().start(runnable)



    @pyqtSlot(dict)
    def show_AccBalance(self, acc_balance):
        print(acc_balance)

        acc_balance1 = collections.OrderedDict(sorted(acc_balance.items(), key=lambda t: t[1]["수익률"], reverse=True))  # Sorting dict in dict
        numbers = len(acc_balance)
        buy_cal = 0;
        estimate_cal = 0
        profits_cal = 0
        ratio_cal = 0
        pre_amount = 0


        # 테이블 초기화
        self.tableWidget_2.setRowCount(0)


        if TEST == True:
            self.tableWidget_2.setRowCount(3)
            self.tableWidget.setRowCount(1)
        else:
            self.tableWidget_2.setRowCount(numbers)
            self.tableWidget.setRowCount(1)


        i = 0;
        for key, value in acc_balance1.items():

            # 종목명
            code = value['종목코드']
            code_item = QTableWidgetItem(code)
            code_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
            code_item.setFlags(QtCore.Qt.ItemIsEnabled)

            # 종목명
            name = value['종목명']
            name_item = QTableWidgetItem(name)
            name_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
            name_item.setFlags(QtCore.Qt.ItemIsEnabled)

            # 현재가
            curprice = value['현재가']
            curprice_item = QTableWidgetItem()
            curprice_item.setData(Qt.DisplayRole, curprice)
            curprice_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            curprice_item.setFlags(QtCore.Qt.ItemIsEnabled)

            # 전일대비
            getchanges = value['대비']

            changes_item = QTableWidgetItem()
            changes_item.setData(Qt.DisplayRole, getchanges)
            changes_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            changes_item.setFlags(QtCore.Qt.ItemIsEnabled)
            if getchanges > 0:
                changes_item.setForeground(QBrush(QColor(255, 0, 0)))
            elif getchanges < 0:
                changes_item.setForeground(QBrush(QColor(0, 0, 255)))

            # 장부가

            buyunitprice = value['장부가']
            buyunitprice_item = QTableWidgetItem()
            buyunitprice_item.setData(Qt.DisplayRole, buyunitprice)
            buyunitprice_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            buyunitprice_item.setFlags(QtCore.Qt.ItemIsEnabled)

            # 보유량
            hold_item = QTableWidgetItem()
            hold_item.setData(Qt.DisplayRole, value['잔고수량'])
            hold_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            hold_item.setFlags(QtCore.Qt.ItemIsEnabled)

            # 매입금액
            buyprice = value['매입금액']
            buyprice_item = QTableWidgetItem()
            buyprice_item.setData(Qt.DisplayRole, buyprice)
            buyprice_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            buyprice_item.setFlags(QtCore.Qt.ItemIsEnabled)

            buy_cal = buy_cal + buyprice

            #  평가금액
            amount = round(value['현재가'] * value['잔고수량'], 0)
            amount_item = QTableWidgetItem()
            amount_item.setData(Qt.DisplayRole, amount)
            amount_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            amount_item.setFlags(QtCore.Qt.ItemIsEnabled)

            estimate_cal = estimate_cal + amount

            # 수익률
            getpratio = value['수익률']
            pratio_item = QTableWidgetItem()
            pratio_item.setData(Qt.DisplayRole, getpratio)
            pratio_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            pratio_item.setFlags(QtCore.Qt.ItemIsEnabled)
            if getpratio > 0:
                pratio_item.setForeground(QBrush(QColor(255, 0, 0)))
            elif getpratio < 0:
                pratio_item.setForeground(QBrush(QColor(0, 0, 255)))

            if i == 0:
                pre_amount = value['예수금']



            # setSortingEnabled(False -> set Value -> True)
            # https://stackoverflow.com/questions/7960505/strange-qtablewidget-behavior-not-all-cells-populated-after-sorting-followed-b/31444019
            self.tableWidget_2.setSortingEnabled(False)

            self.tableWidget_2.setItem(i, 0, code_item)
            self.tableWidget_2.setItem(i, 1, name_item)
            self.tableWidget_2.setItem(i, 2, curprice_item)
            self.tableWidget_2.setItem(i, 3, changes_item)
            self.tableWidget_2.setItem(i, 4, buyunitprice_item)
            self.tableWidget_2.setItem(i, 5, hold_item)
            self.tableWidget_2.setItem(i, 6, buyprice_item)
            self.tableWidget_2.setItem(i, 7, amount_item)
            self.tableWidget_2.setItem(i, 8, pratio_item)

            i = i + 1

        self.tableWidget_2.resizeRowsToContents()

        self.tableWidget_2.setSortingEnabled(True)
        self.tableWidget_2.horizontalHeader().sortIndicatorChanged.connect(self.tableWidget_2.resizeRowsToContents)

        self.progress.hide()


        # Summary 잔고 현황

        self.showSummary(numbers, buy_cal, estimate_cal, pre_amount)
        global SUMMARY_NUMBERS
        global SUMMARY_BUYCAL
        global SUMMARY_ESTIMATECAL
        global SUMMARY_PREAMOUNT

        SUMMARY_NUMBERS = numbers
        SUMMARY_BUYCAL = buy_cal
        SUMMARY_ESTIMATECAL = estimate_cal
        SUMMARY_PREAMOUNT = pre_amount


        self.log('잔고조회 완료하였습니다.')


    def showSummary(self, numbers, buy_cal, estimate_cal, pre_amount):

        # 종목 수량
        sname = 0
        if self.checkBox.isChecked() == True:
            sname = str(numbers)
        else:
            sname = '*' * len(str(numbers))
        sname_item = QTableWidgetItem()
        sname_item.setData(Qt.DisplayRole, sname)
        sname_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
        sname_item.setFlags(QtCore.Qt.ItemIsEnabled)

        # 총 매입
        sbuy = 0
        if self.checkBox.isChecked() == True:
            sbuy = str(format(buy_cal, ','))
        else:
            sbuy = '*' * len(str(buy_cal))

        sbuy_item = QTableWidgetItem()
        sbuy_item.setData(Qt.DisplayRole, sbuy)
        sbuy_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
        sbuy_item.setFlags(QtCore.Qt.ItemIsEnabled)

        # 총 평가
        sestimate = 0
        if self.checkBox.isChecked() == True:
            sestimate = str(format(estimate_cal, ','))

        else:
            sestimate = '*' * len(str(estimate_cal))

        sestimate_item = QTableWidgetItem()
        sestimate_item.setData(Qt.DisplayRole, sestimate)
        sestimate_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
        sestimate_item.setFlags(QtCore.Qt.ItemIsEnabled)

        # 총 손익
        sprofits = 0
        if self.checkBox.isChecked() == True:
            sdiff = estimate_cal - buy_cal
            sprofits = str(format(sdiff, ','))
        else:
            sprofits = '*' * len(str(estimate_cal - buy_cal))


        sprofits_item = QTableWidgetItem()
        sprofits_item.setData(Qt.DisplayRole, sprofits)
        sprofits_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
        sprofits_item.setFlags(QtCore.Qt.ItemIsEnabled)
        if self.checkBox.isChecked() == True:
            if sdiff > 0:
                sprofits_item.setForeground(QBrush(QColor(255, 0, 0)))
            elif sdiff < 0:
                sprofits_item.setForeground(QBrush(QColor(0, 0, 255)))


        # 총 수익률
        pdiff = 0
        if self.checkBox.isChecked() == True:
            pdiff = (sdiff / buy_cal) * 100

            spdiff = str(format(pdiff, '.1f'))
        else:
            spdiff = '***'

        spdiff_item = QTableWidgetItem()

        spdiff_item.setData(Qt.DisplayRole, spdiff)
        spdiff_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
        spdiff_item.setFlags(QtCore.Qt.ItemIsEnabled)
        if self.checkBox.isChecked() == True:
            if pdiff > 0:
                spdiff_item.setForeground(QBrush(QColor(255, 0, 0)))
            elif pdiff < 0:
                spdiff_item.setForeground(QBrush(QColor(0, 0, 255)))




        # 예수금
        spre = 0
        if self.checkBox.isChecked() == True:
            spre = str(format(pre_amount, ','))
        else:
            spre = '*' * len(str(pre_amount))

        spre_item = QTableWidgetItem()
        spre_item.setData(Qt.DisplayRole, spre)
        spre_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
        spre_item.setFlags(QtCore.Qt.ItemIsEnabled)

        # 추정 자산
        stot = 0
        if self.checkBox.isChecked() == True:
            stot = str(format(estimate_cal + pre_amount, ','))
        else:
            stot = '*' * len(str(estimate_cal + pre_amount))

        stot_item = QTableWidgetItem()
        stot_item.setData(Qt.DisplayRole, stot)
        stot_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
        stot_item.setFlags(QtCore.Qt.ItemIsEnabled)

        # set Item
        self.tableWidget.setItem(0, 0, sname_item)
        self.tableWidget.setItem(0, 1, sbuy_item)
        self.tableWidget.setItem(0, 2, sestimate_item)
        self.tableWidget.setItem(0, 3, sprofits_item)
        self.tableWidget.setItem(0, 4, spdiff_item)
        self.tableWidget.setItem(0, 5, spre_item)
        self.tableWidget.setItem(0, 6, stot_item)

        self.tableWidget.resizeRowsToContents()



    def checkBoxState(self):
        nrows = self.tableWidget.rowCount()
        if nrows == 0:
            return


        self.showSummary(SUMMARY_NUMBERS, SUMMARY_BUYCAL, SUMMARY_ESTIMATECAL, SUMMARY_PREAMOUNT)

    def getAllStgList_clicked(self):
        if CONNECTED == False:
            QMessageBox.about(self, "Message", "크레온 플러스 로그인 후 진행 바랍니다.")
            return

        listtype = {}
        stglist = handler.Stg_list()
        listtype =  stglist.get_stg_list()
        global STRATEGY_LIST
        STRATEGY_LIST = listtype

        self.listWidget.clear()
        for i in range(len(listtype)):
            sname = listtype.iloc[i].loc['전략명']
            item = QListWidgetItem(listtype.iloc[i].loc['전략명'])
            # could be Qt.Unchecked; setting it makes the check appear
            item.setCheckState(Qt.Unchecked)
            self.listWidget.addItem(item)

        self.log('전략 리스트 로딩 완료했습니다.')

    def getAllStgList_uncheck_clicked(self):
        global STRATEGY_LIST
        self.listWidget.clear()
        for i in range(len(STRATEGY_LIST)):
            sname = STRATEGY_LIST.iloc[i].loc['전략명']
            item = QListWidgetItem(STRATEGY_LIST.iloc[i].loc['전략명'])
            item.setCheckState(Qt.Unchecked)
            self.listWidget.addItem(item)
        self.log('체크 해제 완료했습니다.')

    def getStgList_clicked(self):

        global STRATEGY_LIST
        global CODE_LIST

        if len(STRATEGY_LIST) == 0:
            QMessageBox.about(self, "Message", "전략 리스트를 먼저 가져오세요")
            return


        namelist = []
        idlist = []
        resultlist = [] # [{'code': 'A000270', '종목명': '기아차'}, {'code': 'A001810', '종목명': '무림SP'},

        stglist = handler.Stg_list()


        for index in range(len(STRATEGY_LIST)):

            item = self.listWidget.item(index)
            if item.checkState() == Qt.Checked:
                name = item.text()
                namelist.append(name)
                id = STRATEGY_LIST.loc[STRATEGY_LIST['전략명'] == name, 'ID'].iloc[0]
                idlist.append(id)

                sresult = stglist.get_stg_list_by_id(id)
                # [{'code': 'A000270', '종목명': '기아차'}, {'code': 'A002870', '종목명': '신풍제지'},
                # 종목명리스트만으로 변경
                result = []
                for i in range(len(sresult)):
                    result.append(sresult[i]['종목명'])

                print('result',result)
                resultlist.append(result)

        if not namelist:
            QMessageBox.about(self, "Message", "전략 리스트를 선택하기시 바랍니다.")
            return


        print('namelist',namelist)
        print('listtype',idlist)
        print('resultlist cnt', len(resultlist))
        print('resultlist', resultlist)


        # 교집합 찾기

        flist = set(resultlist[0]).intersection(*resultlist)
        print('flist', flist)
        print('type(flist)',type(flist))

        codelist = self.getCodeList()

        self.tableWidget_3.setRowCount(len(flist))
        self.tableWidget_3.setSortingEnabled(False)


        for id, value in enumerate(flist):

            # 종목명
            name = value
            name_item = QTableWidgetItem(name)
            name_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
            name_item.setFlags(QtCore.Qt.ItemIsEnabled)


            # 코드
            code = codelist.loc[codelist['name'] == name, 'code'].iloc[0]
            code_item = QTableWidgetItem(code)
            code_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
            code_item.setFlags(QtCore.Qt.ItemIsEnabled)



            self.tableWidget_3.setItem(id, 0, code_item)
            self.tableWidget_3.setItem(id, 1, name_item)


        self.tableWidget_3.resizeRowsToContents()
        self.tableWidget_3.setSortingEnabled(True)
        self.tableWidget_3.horizontalHeader().sortIndicatorChanged.connect(self.tableWidget_2.resizeRowsToContents)


        model = QStandardItemModel()
        for name in namelist:
            model.appendRow(QStandardItem(name))
        self.listView.setModel(model)
        self.listView.setEditTriggers(QAbstractItemView.NoEditTriggers)

        print(len(flist))
        stext = '검색 종목 개수 : ' + str(len(flist))
        print(stext)
        self.label_3.setText(stext)

        self.log('전략 리스트 검색 완료했습니다.')



    # In QtDesigner, and in the property editor select in the contextMenuPolicy the option CustomContextMenu.
    # https: // jeanbilheux.pages.ornl.gov / post / right_click_menu_in_pyqt_table /
    def h3_table_right_click(self, position):
        print("goto....")

        print(position)

        it = self.tableWidget_2.itemAt(position)
        if it is None: return
        c = it.column()
        r = it.row()

        item = self.tableWidget_2.item(r, 1)
        code = self.tableWidget_2.item(r, 0)
        item_text = item.text()
        code_text = code.text()
        print("item_text : ", item_text, ", code_text : ", code_text)

        item_range = QtWidgets.QTableWidgetSelectionRange(0, c, self.tableWidget_2.rowCount() - 1, c)
        self.tableWidget_2.setRangeSelected(item_range, True)

        top_menu = QMenu()
        menu = top_menu.addMenu("Menu")

        chart = menu.addAction("차트보기")
        menu.addSeparator()
        info = menu.addMenu("주식 정보")

        info1 = info.addAction("네이버 금융")
        info2 = info.addAction("기타 2")

        action = menu.exec_(self.tableWidget_2.viewport().mapToGlobal(position))
        print("action : ", action)
        if action == chart:
            # self.showChart(item_text, 'D')
            self.newWindow = MyWindow(item_text)

            # self.newWindow.show()

        elif action == info1:
            url = 'https://finance.naver.com/item/main.nhn?code=' + code_text[1:]
            # url = 'https://finance.naver.com/item/main.nhn?code=263720'
            webbrowser.open(url)

        elif action == info2:
            QMessageBox.about(self, "Message", "info2")

    def tableWidget_doubleClicked(self):
        row = self.tableWidget_3.currentIndex().row()
        column = self.tableWidget_3.currentIndex().column()
        print(row, column)

        item = self.tableWidget_3.item(row, 1) # 클릭한 row 의 종목명
        item_text = item.text() # 종목명
        self.newWindow = MyWindow(item_text) # 차트 화면 불러오기



    def getCodeList(self):
        # 코드리스트 가져오기
        global CODE_LIST
        if len(CODE_LIST) == 0:
            getcodelist = handler.Code_list()
            CODE_LIST = getcodelist.get_code_list()

        return CODE_LIST

    def log(self, text):
        curtime = QTime.currentTime().toString("hh:mm:ss")
        self.textBrowser.append('[ ' + curtime + ' ] ' + text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Form()
    window.setWindowTitle("Auto_System_Trading by WJ")
    window.show()
    sys.exit(app.exec())