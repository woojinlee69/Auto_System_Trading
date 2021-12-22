import sys

import matplotlib
import matplotlib.cm
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import *
# 한글 설정
from matplotlib import font_manager, rc
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from pandas import DataFrame as df

font_name = font_manager.FontProperties(fname="C:/Windows/Fonts/malgun.ttf").get_name()
rc('font', family=font_name)


class MyPieChart(QWidget):
    def __init__(self, parent=None):
        super(MyPieChart, self).__init__(parent)

    def initUI(self, big_values, big_colors, big_labels, small_values, small_labels, splitindex, first_color,
               second_color):
        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)

        self.big_values = big_values
        self.big_colors = big_colors
        self.big_labels = big_labels
        self.small_values = small_values
        self.small_labels = small_labels
        self.splitindex = splitindex
        self.first_color = first_color
        self.second_color = second_color

        layout = QVBoxLayout()

        cb = QComboBox()
        cb.addItem('종목별 비중')
        cb.addItem('종목별 평가금액')
        cb.activated[str].connect(self.onComboBoxChanged)
        layout.addWidget(cb)



        layout.addWidget(self.canvas)
        self.layout = layout

        self.onComboBoxChanged(cb.currentText())

        self.resize(1000, 800)
        self.setLayout(self.layout)


    def onComboBoxChanged(self, text):
        if text == '종목별 비중':
            self.doGraph1()
        elif text == '종목별 평가금액':
            self.doGraph2()

    def doGraph1(self):

        self.fig.clear()
        ax = self.fig.add_subplot(111)


        self.smallcolors = self.getcolor(self.small_values, self.splitindex, self.first_color, self.second_color)
        print(self.smallcolors)

        ax.pie(self.small_values, radius=1, colors=self.smallcolors, labels=self.small_labels, autopct='%.1f%%',
                pctdistance=0.85, shadow=True, wedgeprops=dict(width=0.3, edgecolor='white'), textprops={'fontsize': 6}, startangle=90)

        ax.pie(self.big_values, radius=0.7, colors=self.big_colors, labels=self.big_labels, autopct='%.1f%%',
                pctdistance=0.8, labeldistance=0.4, shadow=True, wedgeprops=dict(width=0.3, edgecolor='white'), textprops={'fontsize': 10}, startangle=90)

        ax.axis('equal')

        print(' plt.axis(equal)')
        print('self.small_values', len(self.small_values))
        print('self.smallcolor', len(self.smallcolors))
        print('self.small_labels', len(self.small_labels))
        print('self.big_values', len(self.big_values))
        print('self.big_colors', len(self.big_colors))
        print('self.big_labels', len(self.big_labels))

        self.canvas.draw_idle()

    def getcolor(self, smallValue, splitindex, firstColor, secondColor):

        firstSection = smallValue[:splitindex]
        secondSection = smallValue[splitindex:]
        print('firstSection, secondSection', firstSection, secondSection)

        # 최대값, 최소값으로 하기엔 색깔이 연하거나 너무 진해서 양쪽으로 마진을 주기로함
        firstMin = 0
        firstMax = max(firstSection) * 1.5
        secondMin = 0
        secondMax = max(secondSection) * 1.5

        print('firstMin, firstMax,secondMin,secondMax', firstMin, firstMax, secondMin, secondMax)

        firstNorm = matplotlib.colors.Normalize(vmin=firstMin, vmax=firstMax)
        secondNorm = matplotlib.colors.Normalize(vmin=secondMin, vmax=secondMax)

        firstmap = matplotlib.cm.get_cmap(firstColor)
        firstarr = []
        for i in firstSection:
            rgba = firstmap(firstNorm(i))
            firstarr.append(rgba)

        secondmap = matplotlib.cm.get_cmap(secondColor)
        secondarr = []
        for i in secondSection:
            rgba = secondmap(secondNorm(i))
            secondarr.append(rgba)

        print('firstarr', firstarr)
        print('secondarr', secondarr)
        return firstarr + secondarr

    def doGraph2(self):

        inputvalue = {}
        inputvalue['종목명'] = self.small_labels
        inputvalue['평가금액'] = self.small_values
        df_inputvalue = df(inputvalue)
        df_inputvalue1 = df_inputvalue.sort_values(by=['평가금액'], ascending=False)
        print(df_inputvalue1)

        self.fig.clear()

        ax = self.fig.add_subplot(111)

        ax.bar(df_inputvalue1['종목명'].tolist(), list(map(int, df_inputvalue1['평가금액'].tolist())), align='center', alpha=0.5)
        print('int list ', list(map(int, df_inputvalue1['평가금액'].tolist())))
        ax.set_xlabel('종목명')

        ax.tick_params(axis='both', which='major', labelsize=8)
        ax.tick_params(axis='both', which='minor', labelsize=6)

        ax.yaxis.grid()  # horizontal lines
        # ax.xaxis.grid()  # vertical lines

        ax.set_ylabel('평가금액')
        ax.set_title('종목별 평가금액')

        # plt.xticks(rotation=45)

        self.canvas.draw_idle()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyPieChart()

    big_values = [6984712, 10705748]
    big_colors = ['b', 'g']
    big_labels = ['거래소', '코스닥']
    small_values = [172425, 147500, 147210, 142400, 141800, 135720, 128370, 124800, 121750, 116640, 115720, 113680,
                    111100, 110110, 109830, 108680, 108625, 107880, 107100, 106835, 104470, 103200, 102600, 100740,
                    100510, 100230, 99900, 98100, 96800, 95040, 94290, 94050, 93600, 93075, 92400, 91980, 91300, 89760,
                    89310, 88160, 87750, 87500, 87360, 87220, 86800, 86000, 85918, 83850, 83720, 82450, 81800, 81630,
                    81000, 80172, 80100, 79200, 78910, 76715, 75000, 74250, 73170, 72935, 70560, 70392, 70200, 66650,
                    64570, 63960, 63470, 58630, 58050, 57400, 54500, 54090, 41100, 182820, 167100, 163800, 158400,
                    142800, 142500, 141705, 138960, 135300, 133740, 130000, 128960, 128180, 126650, 126480, 124230,
                    123970, 122265, 120800, 119210, 119000, 118400, 118400, 114790, 112200, 111720, 111650, 110490,
                    109725, 109150, 109010, 108330, 108300, 107460, 107120, 106030, 105840, 104595, 103460, 103275,
                    102900, 101680, 101640, 99400, 98890, 98640, 98560, 98280, 98010, 97730, 97470, 96690, 96145, 96140,
                    95550, 94325, 93125, 93000, 92200, 92180, 91800, 91800, 91625, 91125, 90480, 89600, 89600, 89400,
                    88790, 87824, 87780, 87420, 87084, 85800, 85536, 84785, 84750, 84075, 83875, 81795, 77520, 77100,
                    76995, 76000, 75950, 75900, 75900, 75760, 75300, 75240, 72675, 72240, 72160, 70850, 70125, 69000,
                    68445, 68055, 65670, 64285, 62886, 61710, 60258, 59160, 57800, 54040, 51120, 50540, 49770, 48930,
                    40050]

    small_labels = ['한창제지', '보령제약', 'KC코트렐', '백광소재', '현대차3우B', '디피씨', '신일산업', '기아차', '삼성출판사', '수산중공업', 'SK네트웍스', '한국카본',
                    '동원수산', '애경유화', '현대약품', '대현', '한농화성', '극동유화', '대덕전자1우', '케이탑리츠', '고려산업', '두올', '태경산업', '삼호개발',
                    '화승알앤에이', '진양홀딩스', 'SK디스커버리우', '동서', '대신증권우', 'CJ씨푸드', '일진디스플', '우성사료', '넷마블', 'IHQ', 'KTcs',
                    '동방아그로', 'DB금융투자', 'JB금융지주', '한전산업', '대우부품', '일성건설', '유나이티드제약', '유유제약1우', '백광산업', '대한해운', '코오롱인더우',
                    '한국전자홀딩스', '광전자', '넥센', 'AJ네트웍스', '롯데정보통신', 'DSR', '사조대림', '우리종금', '한국전력', '대우조선해양', '지투알',
                    'SH에너지화학', '사조씨푸드', '영보화학', '동화약품', '무림페이퍼', '문배철강', '서울식품', 'DRB동일', 'NI스틸', '대동공업', '동양',
                    'LG헬로비전', '티웨이항공', '대한항공우', '한라', 'GS글로벌', '한국자산신탁', '제이콘텐트리', 'S&K폴리텍', 'SDN', '오공', '파세코', '화신정공',
                    '에스에이엠티', '인지디스플레', '하츠', '디케이디앤아이', '피엔티', '파워로직스', '오성첨단소재', '이스트소프트', '이루온', '현대공업', 'KNN',
                    '유비케어', '광진윈텍', '국일신동', '로보로보', '대신정보통신', '코미코', '네오위즈홀딩스', '영풍정밀', '대성엘텍', '해마로푸드서비스', 'KCI',
                    '삼영엠텍', 'GH신소재', '지에스이', '에이텍', '삼화네트웍스', '아비코전자', '한컴위드', '에이티넘인베스트', '디지틀조선', '아바텍', '구영테크',
                    '아세아텍', '티비씨', '피제이메탈', '동국알앤에스', '파워넷', '에스피지', '풍강', 'KTH', '성우하이텍', '한국큐빅', 'KT서브마린', '삼일기업공사',
                    '동국산업', '이글루시큐리티', '케이씨티', '에스에이티', '코데즈컴바인', '경창산업', '갤럭시아컴즈', '바이오톡스텍', '크루셜텍', '가온미디어', '현우산업',
                    'YTN', '디스플레이텍', 'SBI인베스트먼트', '팅크웨어', '자이글', '한국팩키지', '동양에스텍', '동우팜투테이블', '대호피앤씨', '대성창투', '디지아이',
                    '큐캐피탈', '세보엠이씨', '한국캐피탈', 'TS인베스트먼트', '시그네틱스', 'TPC', 'KG ETS', '대주산업', '플랜티넷', '삼현철강', '삼본전자',
                    '조아제약', '기산텔레콤', '체리부로', '세운메디칼', '서린바이오', '룽투코리아', '코맥스', '코리아에스이', '이건홀딩스', '무림SP', '신진에스엠',
                    '피에스텍', '신화콘텍', '정다운', '엘컴텍', '포메탈', '유성티엔에스', '휘닉스소재', '에스에프씨', '세종텔레콤', 'HRS', '국순당', '하림지주',
                    '네이처셀', '성도이엔지', '서한', '이화전기', '코오롱티슈진']
    splitindex = 75
    first_color = 'Blues'
    second_color = 'Greens'

    window.initUI(big_values, big_colors, big_labels, small_values, small_labels, splitindex, first_color, second_color)
    window.show()
    app.exec_()