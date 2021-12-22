import sys

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import mpl_finance
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import handler


class MyWindow(QWidget):
    def __init__(self, code, parent=None):
        super(MyWindow, self).__init__(parent)

        self.callbyothers = True
        self.getchartfirst = True

        self.setupUI(code)
        self.show()


    def setupUI(self,code):

        self.code = code
        self.resize(1200, 800);
        self.setWindowTitle("PyChart Viewer v0.1")
        # self.setWindowIcon(QIcon('icon.png'))

        self.code_list = self.makeCodeList()



        names = self.code_list["name"]
        print("self.code_list", self.code_list)



        #종목명
        self.codeText = QLabel("종목코드 : ")



        completer = QCompleter(names)

        self.lineEdit = QLineEdit()
        self.lineEdit.setCompleter(completer)


        self.dayButton = QPushButton("일봉")
        self.monthButton = QPushButton("월봉")
        self.weekButton = QPushButton("주봉")

        self.numberText = QLabel("  조회 데이터수 : ")
        self.numberEdit = QLineEdit('200')





        self.fig = plt.figure(constrained_layout=False)
        self.canvas = FigureCanvas(self.fig)


        self.rightLayout = QHBoxLayout()

        self.rightLayout.addWidget(self.codeText)
        self.rightLayout.addWidget(self.lineEdit)
        # self.rightLayout.addWidget(self.codeName)
        self.rightLayout.addWidget(self.dayButton)
        self.rightLayout.addWidget(self.weekButton)
        self.rightLayout.addWidget(self.monthButton)
        self.rightLayout.addWidget(self.numberText)
        self.rightLayout.addWidget(self.numberEdit)
        self.rightLayout.addStretch(1)


        self.leftLayout = QVBoxLayout()
        self.leftLayout.addWidget(self.canvas)



        self.layout = QVBoxLayout()
        self.layout.addLayout(self.rightLayout)
        self.layout.addLayout(self.leftLayout)

        self.layout.setStretchFactor(self.rightLayout, 0)
        self.layout.setStretchFactor(self.leftLayout, 1)


        self.setLayout(self.layout)

        self.gs = self.fig.add_gridspec(4, 8)

        self.ax = self.fig.add_subplot(self.gs[:-1, :])
        self.ax2 = self.fig.add_subplot(self.gs[-1, :])





        self.dayButton.clicked.connect(self.pushButtonClicked_day)
        self.dayButton.setAutoDefault(True)  # enable Enter key


        self.weekButton.clicked.connect(self.pushButtonClicked_week)
        self.weekButton.setAutoDefault(True)  # enable Enter key


        self.monthButton.clicked.connect(self.pushButtonClicked_mon)
        self.monthButton.setAutoDefault(True)  # enable Enter key

        if self.callbyothers == True:
            self.lineEdit.setText(code)
            self.pushButtonClicked_day()
            self.callbyothers = False


    def makeCodeList(self):
        print("makeCodeList started..")

        codelist = handler.Code_list()
        print("handler.Code_list() completed")
        self.code_list = codelist.get_code_list()
        return self.code_list



    def chk_ohlcv(self, code, type, num):
        aaa = handler.OHLCV_list()
        c = aaa.get_ohlcv_list(code, type, num)
        print("get_ohlcv_list return....")
        print(c)
        print(c['date'])
        return c

    def pushButtonClicked_day(self):
        self.pushButtonClicked('D')
    def pushButtonClicked_week(self):
        self.pushButtonClicked('W')
    def pushButtonClicked_mon(self):
        self.pushButtonClicked('M')

    def pushButtonClicked(self,type):
        print("pushButtonClicked.... type : ", type)

        cname = self.lineEdit.text()
        num =  self.numberEdit.text()

        code = self.code_list.loc[self.code_list['name'] == cname, 'code'].iloc[0]

        print("code :", code, ", name : ", cname)

        if len(num) == 0:
            self.drawChart(code, type)
        else:
            self.drawChart(code, type, num)



    def drawChart(self, code, type, num = 200):
        df1 = self.chk_ohlcv(code, type, num)
        print(df1)
        # df = df1.set_index("date")
        print("=======================================")
        # print(df['close'])
        df = df1
        print("=======================================")
        # df['MA5'] = df['close'].rolling(window=5).mean()
        # df['MA10'] = df['close'].rolling(window=10).mean()
        # df['MA20'] = df['close'].rolling(window=20).mean()
        # df['MA60'] = df['close'].rolling(window=60).mean()

        print(df)
        print("num : ", num)



        if self.getchartfirst == False:

            self.ax.clear()
            self.ax2.clear()
            self.canvas.draw()

        self.getchartfirst = False


        day_list = []
        name_list = []


        for i, row in df.iterrows():

            print('i : ', i , " , day : ", row['date'])
            day_list.append(i)
            if i % 70 * int(df.size/200) == 0:
                name_list.append(row['date'].strftime('%Y-%m-%d'))
            else:
                name_list.append("")




        self.ax.plot(day_list, df['close'], label='Close')
        self.ax.plot(day_list, df['MA5'], label='MA5')
        self.ax.plot(day_list, df['MA10'], label='MA10')
        self.ax.plot(day_list, df['MA20'], label='MA20')
        self.ax.plot(day_list, df['MA60'], label='MA60')
        self.ax.legend(loc='upper right')

        self.ax.legend(loc='upper left')


        self.ax.grid(axis='y')

        # self.ax.xaxis.set_major_locator(ticker.FixedLocator(df.index))
        # self.ax.xaxis.set_major_formatter(ticker.FixedFormatter(df.date))

        mpl_finance.candlestick2_ohlc(self.ax, df['open'], df['high'], df['low'], df['close'], width=0.5, colorup='r',
                                      colordown='b')

        # ax2 = self.fig.add_subplot(gs[-1, :])
        self.ax2.bar(day_list, df['vol'],color=df.positive.map({True: 'r', False: 'b'}))

        #
        # date_form = DateFormatter("%m/%d")
        # self.ax.xaxis.set_major_formatter(date_form)
        # # Ensure ticks fall once every other week (interval=2)
        # self.ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))

        self.ax.xaxis.set_major_locator(ticker.FixedLocator(day_list))
        self.ax.xaxis.set_major_formatter(ticker.FixedFormatter(name_list))

        self.ax2.xaxis.set_major_locator(ticker.FixedLocator(day_list))
        self.ax2.xaxis.set_major_formatter(ticker.FixedFormatter(name_list))

        self.ax2.grid(axis='y')


        self.canvas.draw_idle()




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow("A000020")
    window.show()
    app.exec_()