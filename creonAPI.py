'''
대신증권 관련 함수 모음
'''
import ctypes
import datetime
import os

import win32com.client
from pandas import DataFrame as df
from pywinauto import application

from pywinauto import application
import time
import os

g_objCodeMgr = win32com.client.Dispatch('CpUtil.CpStockCode')
g_objCpStatus = win32com.client.Dispatch('CpUtil.CpCybos')
g_objCpTrade = win32com.client.Dispatch('CpTrade.CpTdUtil')
def login(user_info):
    print("login(user_info):")
    id = user_info[0]
    pw = user_info[1]
    cert = user_info[2]

    app = application.Application()
    app.start("C:\CREON\STARTER\coStarter.exe //prj:cp /id:%s /pwd:%s /pwdcert:%s /autostart" % (id, pw, cert))

    return

# CYBOS Plus 접속 여부 확인
# in : X
# Out : con_flag(int)
def check_con():
    # 연결 여부 체크
    objCpCybos = win32com.client.Dispatch("CpUtil.CpCybos")
    con_flag = objCpCybos.IsConnect
    print("check_con() : ", con_flag)
    return con_flag


def disconnect():
    print("disconnect 호출됨")

    objCpCybos = win32com.client.Dispatch("CpUtil.CpCybos")
    objCpCybos.PlusDisconnect()
    kill_client()

def kill_client():
    print("def kill_client(self):_started")
    os.system('taskkill /IM coStarter* /F /T')
    os.system('taskkill /IM CpStart* /F /T')
    os.system('taskkill /IM DibServer* /F /T')
    os.system('wmic process where "name like \'%coStarter%\'" call terminate')
    os.system('wmic process where "name like \'%CpStart%\'" call terminate')
    os.system('wmic process where "name like \'%DibServer%\'" call terminate')
    print("def kill_client(self):_ended")

# 유저 정보 호출
## in : flag (int, 입력 가능 값 : 0, 1)
##      n (만약 멀티로 계좌를 돌릴 경우를 대비하여 넣어놓았음)
## out : flag에 따른 유저 정보
def get_user_info(flag, n):
    objTrade = win32com.client.Dispatch("CpTrade.CpTdUtil")
    initCheck = objTrade.TradeInit(0)
    if (initCheck != 0):
        print("주문 초기화 실패")
        # exit()
        return

    # 계좌번호 및 상품구분 정보 호출
    acc = objTrade.AccountNumber[n]  # 계좌번호
    accFlag = objTrade.GoodsList(acc, 1)  # 주식상품 구분

    trader_info = [acc, accFlag]

    return trader_info[flag]


# 가격정보 호출 (기술적 지표값 제작용)
## in : stock_code(str), date(int), call_list(array)
## out : past_data(dataframe)
## date는 n일전 형식으로 넣을것.
def call_price_data_day(code, date, call_list):
    # 연결 여부 체크
    objCpCybos = win32com.client.Dispatch("CpUtil.CpCybos")
    bConnect = objCpCybos.IsConnect
    if (bConnect == 0):
        print("PLUS가 정상적으로 연결되지 않음. ")
        exit()

    # 차트 객체 구하기
    objStockChart = win32com.client.Dispatch("CpSysDib.StockChart")

    objStockChart.SetInputValue(0, code)  # 종목 코드
    objStockChart.SetInputValue(1, ord('2'))  # 개수로 조회
    objStockChart.SetInputValue(4, date)  # 최근 100일 치
    objStockChart.SetInputValue(5, [0, 2, 3, 4, 5, 8])  # 날짜,시가,고가,저가,종가,거래량
    objStockChart.SetInputValue(6, ord('D'))  # '차트 주가 - 일간 차트 요청
    objStockChart.SetInputValue(9, ord('1'))  # 수정주가 사용
    objStockChart.BlockRequest()

    len = objStockChart.GetHeaderValue(3)
    temp = []

    for i in range(len):
        day = objStockChart.GetDataValue(0, i)
        open = objStockChart.GetDataValue(1, i)
        high = objStockChart.GetDataValue(2, i)
        low = objStockChart.GetDataValue(3, i)
        close = objStockChart.GetDataValue(4, i)
        vol = objStockChart.GetDataValue(5, i)

        temp.append([day, open, high, low, close, vol])


# 매수
## Input : 계좌번호, 종목코드, 가격, 수량
## Output : 체결여부
def buy(acc, code, price, amount):
    # 연결 여부 체크
    objCpCybos = win32com.client.Dispatch("CpUtil.CpCybos")
    bConnect = objCpCybos.IsConnect
    if (bConnect == 0):
        print("PLUS가 정상적으로 연결되지 않음. ")
        exit()

    # 주문 초기화
    objTrade = win32com.client.Dispatch("CpTrade.CpTdUtil")
    initCheck = objTrade.TradeInit(0)
    if (initCheck != 0):
        print("주문 초기화 실패")
        # exit()
        return

    # 주식 매수 주문
    accFlag = objTrade.GoodsList(acc, 1)  # 주식상품 구분
    print(acc, accFlag[0])
    objStockOrder = win32com.client.Dispatch("CpTrade.CpTd0311")
    objStockOrder.SetInputValue(0, "2")  # 2: 매수
    objStockOrder.SetInputValue(1, acc)  # 계좌번호
    objStockOrder.SetInputValue(2, accFlag[0])  # 상품구분 - 주식 상품 중 첫번째
    objStockOrder.SetInputValue(3, code)  # 종목코드 - A003540 - 대신증권 종목
    objStockOrder.SetInputValue(4, amount)  # 매수수량 10주
    objStockOrder.SetInputValue(5, price)  # 주문단가  - 14,100원
    objStockOrder.SetInputValue(7, "0")  # 주문 조건 구분 코드, 0: 기본 1: IOC 2:FOK
    objStockOrder.SetInputValue(8, "01")  # 주문호가 구분코드 - 01: 보통

    # 매수 주문 요청
    objStockOrder.BlockRequest()

    rqStatus = objStockOrder.GetDibStatus()
    rqRet = objStockOrder.GetDibMsg1()
    print("통신상태", rqStatus, rqRet)
    if rqStatus != 0:
        exit()


# 매도
## Input : 계좌번호, 종목코드, 가격, 수량
## Output : 체결여부
def sell(acc, code, price, amount):
    # 연결 여부 체크
    objCpCybos = win32com.client.Dispatch("CpUtil.CpCybos")
    bConnect = objCpCybos.IsConnect
    if (bConnect == 0):
        print("PLUS가 정상적으로 연결되지 않음. ")
        exit()

    # 주문 초기화
    objTrade = win32com.client.Dispatch("CpTrade.CpTdUtil")
    initCheck = objTrade.TradeInit(0)
    if (initCheck != 0):
        print("주문 초기화 실패")
        # exit()
        return

    # 주식 매도 주문
    accFlag = objTrade.GoodsList(acc, 1)  # 주식상품 구분
    print(acc, accFlag[0])
    objStockOrder = win32com.client.Dispatch("CpTrade.CpTd0311")
    objStockOrder.SetInputValue(0, "1")  # 1: 매도
    objStockOrder.SetInputValue(1, acc)  # 계좌번호
    objStockOrder.SetInputValue(2, accFlag[0])  # 상품구분 - 주식 상품 중 첫번째
    objStockOrder.SetInputValue(3, code)  # 종목코드 - A003540 - 대신증권 종목
    objStockOrder.SetInputValue(4, amount)  # 매도수량 10주
    objStockOrder.SetInputValue(5, price)  # 주문단가  - 14,100원
    objStockOrder.SetInputValue(7, "0")  # 주문 조건 구분 코드, 0: 기본 1: IOC 2:FOK
    objStockOrder.SetInputValue(8, "01")  # 주문호가 구분코드 - 01: 보통

    # 매도 주문 요청
    objStockOrder.BlockRequest()

    rqStatus = objStockOrder.GetDibStatus()
    rqRet = objStockOrder.GetDibMsg1()
    print("통신상태", rqStatus, rqRet)
    if rqStatus != 0:
        exit()


def get_account_balance_origin():
    total_bal = {}
    g_objCpTrade = win32com.client.Dispatch('CpTrade.CpTdUtil')
    acc = g_objCpTrade.AccountNumber[0]
    accFlag = g_objCpTrade.GoodsList(acc, 1)

    objRq = win32com.client.Dispatch("CpTrade.CpTd6033")
    objRq.SetInputValue(0, acc)  # 계좌번호
    objRq.SetInputValue(1, accFlag[0])  # 상품구분 - 주식 상품 중 첫번째
    objRq.SetInputValue(2, 50)  # 요청 건수(최대 50)
    dicflag1 = {ord(' '): '현금',
                ord('Y'): '융자',
                ord('D'): '대주',
                ord('B'): '담보',
                ord('M'): '매입담보',
                ord('P'): '플러스론',
                ord('I'): '자기융자',
                }

    while True:
        objRq.BlockRequest()
        # 통신 및 통신 에러 처리
        rqStatus = objRq.GetDibStatus()
        rqRet = objRq.GetDibMsg1()
        print("통신상태", rqStatus, rqRet)
        if rqStatus != 0:
            return False

        cnt = objRq.GetHeaderValue(7)
        print(cnt)

        for i in range(cnt):
            item = {}
            code = objRq.GetDataValue(12, i)  # 종목코드
            item['종목코드'] = code
            item['종목명'] = objRq.GetDataValue(0, i)  # 종목명
            item['현금신용'] = dicflag1[objRq.GetDataValue(1, i)]  # 신용구분
            print(code, '현금신용', item['현금신용'])
            item['대출일'] = objRq.GetDataValue(2, i)  # 대출일
            item['잔고수량'] = objRq.GetDataValue(7, i)  # 체결잔고수량
            item['매도가능'] = objRq.GetDataValue(15, i)
            item['장부가'] = objRq.GetDataValue(17, i)  # 체결장부단가
            # item['평가금액'] = objRq.GetDataValue(9, i)  # 평가금액(천원미만은 절사 됨)
            # item['평가손익'] = objRq.GetDataValue(11, i)  # 평가손익(천원미만은 절사 됨)
            # 매입금액 = 장부가 * 잔고수량
            item['매입금액'] = item['장부가'] * item['잔고수량']
            item['현재가'] = 0
            item['대비'] = 0
            item['거래량'] = 0

            # 잔고 추가
            #                key = (code, item['현금신용'],item['대출일'] )
            key = code
            # caller.jangoData[key] = item
            total_bal[key] = item

            # if len(caller.jangoData) >= 200:  # 최대 200 종목만,
            if len(total_bal) >= 200:  # 최대 200 종목만,
                break

        # if len(caller.jangoData) >= 200:
        if len(total_bal) >= 200:
            break
        if (objRq.Continue == False):
            break
    print("보유종목 개수 : ", len(total_bal))
    return total_bal


# PLUS 실행 기본 체크 함수
def InitPlusCheck():
    # 프로세스가 관리자 권한으로 실행 여부
    g_objCpStatus = win32com.client.Dispatch('CpUtil.CpCybos')
    g_objCpTrade = win32com.client.Dispatch('CpTrade.CpTdUtil')

    if ctypes.windll.shell32.IsUserAnAdmin():
        print('정상: 관리자권한으로 실행된 프로세스입니다.')
    else:
        print('오류: 일반권한으로 실행됨. 관리자 권한으로 실행해 주세요')
        return False

    # 연결 여부 체크
    if (g_objCpStatus.IsConnect == 0):
        print("PLUS가 정상적으로 연결되지 않음. ")
        return False

    # 주문 관련 초기화
    if (g_objCpTrade.TradeInit(0) != 0):
        print("주문 초기화 실패")
        return False

    return True


# 코드별 현재가/대비
def curprice_Request(codes):
    results = {}

    # 요청 필드 배열 - 종목코드, 시간, 대비부호 대비, 현재가, 거래량, 종목명
    rqField = [0, 1, 2, 3, 4, 10, 17]  # 요청 필드

    # 관심종목 객체 구하기
    objRq = win32com.client.Dispatch("CpSysDib.MarketEye")

    # 요청 필드 세팅 - 종목코드, 종목명, 시간, 대비부호, 대비, 현재가, 거래량
    objRq.SetInputValue(0, rqField)  # 요청 필드
    objRq.SetInputValue(1, codes)  # 종목코드 or 종목코드 리스트
    objRq.BlockRequest()

    # 현재가 통신 및 통신 에러 처리
    rqStatus = objRq.GetDibStatus()
    rqRet = objRq.GetDibMsg1()
    print("통신상태", rqStatus, rqRet)
    if rqStatus != 0:
        return False

    cnt = objRq.GetHeaderValue(2)
    print("현재가 code cnt : ", cnt)
    for i in range(cnt):
        item = {}

        code = objRq.GetDataValue(0, i)
        item['종목코드'] = code  # 코드
        # rpName = objRq.GetDataValue(1, i)  # 종목명
        # rpDiffFlag = objRq.GetDataValue(3, i)  # 대비부호
        item['대비'] = objRq.GetDataValue(3, i)  # 대비
        item['현재가'] = objRq.GetDataValue(4, i)  # 현재가
        item['현재가_천'] = format(item['현재가'], ',')

        item['vol'] = objRq.GetDataValue(5, i)  # 거래량


        # caller.curDatas[item['code']] = item

        key = code
        # caller.jangoData[key] = item
        results[key] = item


    return results


def get_account_balance():
    total_bal = {}

    # 주문 초기화
    objTrade = win32com.client.Dispatch("CpTrade.CpTdUtil")
    initCheck = objTrade.TradeInit(0)
    if (initCheck != 0):
        print("주문 초기화 실패")
        # exit()
        return

    g_objCpTrade = win32com.client.Dispatch('CpTrade.CpTdUtil')
    acc = g_objCpTrade.AccountNumber[0]
    accFlag = g_objCpTrade.GoodsList(acc, 1)

    objRq = win32com.client.Dispatch("CpTrade.CpTd6033")
    objRq.SetInputValue(0, acc)  # 계좌번호
    objRq.SetInputValue(1, accFlag[0])  # 상품구분 - 주식 상품 중 첫번째
    objRq.SetInputValue(2, 50)  # 요청 건수(최대 50)
    # dicflag1 = {ord(' '): '현금',
    #             ord('Y'): '융자',
    #             ord('D'): '대주',
    #             ord('B'): '담보',
    #             ord('M'): '매입담보',
    #             ord('P'): '플러스론',
    #             ord('I'): '자기융자',
    #             }

    while True:
        objRq.BlockRequest()
        # 통신 및 통신 에러 처리
        rqStatus = objRq.GetDibStatus()
        rqRet = objRq.GetDibMsg1()
        print("통신상태", rqStatus, rqRet)
        if rqStatus != 0:
            return False

        cnt = objRq.GetHeaderValue(7)
        print(cnt)

        prevalue = objRq.GetHeaderValue(9)

        for i in range(cnt):
            item = {}
            code = objRq.GetDataValue(12, i)  # 종목코드
            item['종목코드'] = code
            item['종목명'] = objRq.GetDataValue(0, i)  # 종목명
            # item['현금신용'] = dicflag1[objRq.GetDataValue(1, i)]  # 신용구분
            # print(code, '현금신용', item['현금신용'])
            # item['대출일'] = objRq.GetDataValue(2, i)  # 대출일
            item['잔고수량'] = objRq.GetDataValue(7, i)  # 체결잔고수량
            item['수익률'] = round(objRq.GetDataValue(11, i), 1)  # 수익률
            # item['매도가능'] = objRq.GetDataValue(15, i)
            item['장부가'] = round(objRq.GetDataValue(17, i))  # 체결장부단가
            item['장부가_천'] = format(item['장부가'],',')
            # item['손익단가'] = objRq.GetDataValue(18, i)  # 손익단가
            item['평가금액'] = objRq.GetDataValue(9, i)  # 평가금액(천원미만은 절사 됨)
            item['평가금액_천'] = format(item['평가금액'], ',')

            # item['평가손익'] = objRq.GetDataValue(11, i)  # 평가손익(천원미만은 절사 됨)
            # 매입금액 = 장부가 * 잔고수량
            item['매입금액'] = round(item['장부가'] * item['잔고수량'])
            item['매입금액_천'] = format(item['매입금액'], ',')

            item['예수금'] = prevalue

            item['현재가'] = 0
            item['대비'] = 0
            # item['거래량'] = 0

            # 잔고 추가
            #                key = (code, item['현금신용'],item['대출일'] )
            key = code
            # caller.jangoData[key] = item
            total_bal[key] = item

            # if len(caller.jangoData) >= 200:  # 최대 200 종목만,
            if len(total_bal) >= 200:  # 최대 200 종목만,
                break

        # if len(caller.jangoData) >= 200:
        if len(total_bal) >= 200:
            break
        if (objRq.Continue == False):
            break
    print("보유종목 개수 : ", len(total_bal))
    print("total bal ", total_bal)

    return total_bal


def cal_date(size, unit):
    result = []
    gap = 0

    if unit == 'D':
        gap = 1
    elif unit == 'W':
        gap = 7
    elif unit == 'M':
        gap = 30

    calculated = datetime.datetime.now().date()

    n = int(size)

    for i in range(0, n):
        calculated = calculated + datetime.timedelta(days=-gap)
        if unit == 'D':
            while calculated.weekday() == 5 or calculated.weekday() == 6:
                calculated = calculated + datetime.timedelta(days=-1)
        result.append(calculated)

    return result


def get_ohlcv_info(code, type, inputnum):
    print("get_ohlcv_info started..")
    objCpCybos = win32com.client.Dispatch("CpUtil.CpCybos")
    bConnect = objCpCybos.IsConnect
    if (bConnect == 0):
        print("PLUS가 정상적으로 연결되지 않음. ")
        exit()

    num = int(inputnum)
    # 차트 객체 구하기
    objStockChart = win32com.client.Dispatch("CpSysDib.StockChart")

    objStockChart.SetInputValue(0, code)  # 종목 코드 - 삼성전자
    objStockChart.SetInputValue(1, ord('2'))  # 개수로 조회
    objStockChart.SetInputValue(4, num)  # 최근 100일 치
    objStockChart.SetInputValue(5, [0, 2, 3, 4, 5, 8])  # 날짜,시가,고가,저가,종가,거래량
    objStockChart.SetInputValue(6, ord(type))  # '차트 주가 - 일간 차트 요청 'D'일'W'주'M'월'm'분'T'틱

    objStockChart.SetInputValue(9, ord('1'))  # 수정주가 사용
    objStockChart.BlockRequest()

    l = objStockChart.GetHeaderValue(3)

    print("objStockChart.GetHeaderValue(3)", objStockChart.GetHeaderValue(3))
    info = {}
    day_info = []
    open_info = []
    high_info = []
    low_info = []
    close_info = []
    vol_info = []

    for i in range(l):
        day = objStockChart.GetDataValue(0, i)
        open = objStockChart.GetDataValue(1, i)
        high = objStockChart.GetDataValue(2, i)
        low = objStockChart.GetDataValue(3, i)
        close = objStockChart.GetDataValue(4, i)
        vol = objStockChart.GetDataValue(5, i)
        # print(day, open, high, low, close, vol)

        day_info.append(day)
        open_info.append(open)
        high_info.append(high)
        low_info.append(low)
        close_info.append(close)
        vol_info.append(vol)

    # date_info = cal_date(num,type)

    date_info = cal_date(l, type)

    # print(len(open_info))
    # print(len(day_info))
    #
    # print(len(high_info))
    # print(len(low_info))
    # print(len(close_info))
    # print(len(vol_info))
    # print(len(date_info))

    day_info.reverse()
    open_info.reverse()
    high_info.reverse()
    low_info.reverse()
    close_info.reverse()
    vol_info.reverse()
    date_info.reverse()


    info['day'] = day_info
    info['open'] = open_info
    info['high'] = high_info
    info['low'] = low_info
    info['close'] = close_info
    info['vol'] = vol_info
    info['date'] = date_info

    df_data = df(info)


    df_data['MA5'] = df_data['close'].rolling(window=5).mean()
    df_data['MA10'] = df_data['close'].rolling(window=10).mean()
    df_data['MA20'] = df_data['close'].rolling(window=20).mean()
    df_data['MA60'] = df_data['close'].rolling(window=60).mean()

    df_data['positive'] = (df_data.vol - df_data.vol.shift() > 0)

    print("get_ohlcv_info ended..")
    return df_data


def get_code_list():
    stocklist = {}
    market = []
    code = []
    secondCode = []
    name = []

    KOSPI = "Kospi"
    KOSDAQ = "Kosdaq"

    for p in range(1, 3):  # kospi 1, kosdaq 2
        print('p', p)

        instCpCodeMgr = win32com.client.Dispatch("CpUtil.CpCodeMgr")
        codeList = instCpCodeMgr.GetStockListByMarket(p)

        for i, c in enumerate(codeList):
            sc = instCpCodeMgr.GetStockSectionKind(c)
            n = instCpCodeMgr.CodeToName(c)
            if (p == 1):
                market.append(KOSPI)
            elif (p == 2):
                market.append(KOSDAQ)
            code.append(c)
            secondCode.append(sc)
            name.append(n)

    stocklist['market'] = market
    stocklist['code'] = code
    stocklist['secondCode'] = secondCode
    stocklist['name'] = name

    df_stocklist = df(stocklist)

    # print(df_stocklist)
    return df_stocklist


def requestStgList():
    data8537 = {}
    idlist = []
    namelist = []

    objRq = None
    objRq = win32com.client.Dispatch("CpSysDib.CssStgList")

    # 예제 전략에서 전략 리스트를 가져옵니다.
    objRq.SetInputValue(0, ord('0'))  # '0' : 예제전략, '1': 나의전략
    objRq.BlockRequest()

    # 통신 및 통신 에러 처리
    rqStatus = objRq.GetDibStatus()
    if rqStatus != 0:
        rqRet = objRq.GetDibMsg1()
        print("통신상태", rqStatus, rqRet)
        return False

    cnt = objRq.GetHeaderValue(0)  # 0 - (long) 전략 목록 수
    flag = objRq.GetHeaderValue(1)  # 1 - (char) 요청구분
    print('종목검색 전략수:', cnt)

    for i in range(cnt):
        # item = {}
        # item['전략명'] = objRq.GetDataValue(0, i)
        # item['ID'] = objRq.GetDataValue(1, i)
        # item['전략등록일시'] = objRq.GetDataValue(2, i)
        # item['작성자필명'] = objRq.GetDataValue(3, i)
        # item['평균종목수'] = objRq.GetDataValue(4, i)
        # item['평균승률'] = objRq.GetDataValue(5, i)
        # item['평균수익'] = objRq.GetDataValue(6, i)
        # data8537[item['전략명']] = item
        # print(data8537)
        namelist.append(objRq.GetDataValue(0, i))
        idlist.append( objRq.GetDataValue(1, i))

    data8537['전략명'] = namelist
    data8537['ID'] = idlist

    df_data8537 = df(data8537)
    print('requestStgList end')
    print(df_data8537)
    return df_data8537

# '전략명': '그물망 바닥 탈피', 'ID': 'Ea2D32b6S4a6iI/wJN1jWg'
# requestStgID(Ea2D32b6S4a6iI/wJN1jWg)
def requestStgID(id):
    print('requestStgID started..')
    dataStg = []
    objRq = None
    objRq = win32com.client.Dispatch("CpSysDib.CssStgFind")
    objRq.SetInputValue(0, id)  # 전략 id 요청
    objRq.BlockRequest()
    # 통신 및 통신 에러 처리
    rqStatus = objRq.GetDibStatus()
    if rqStatus != 0:
        rqRet = objRq.GetDibMsg1()
        print("통신상태", rqStatus, rqRet)
        return False

    cnt = objRq.GetHeaderValue(0)  # 0 - (long) 검색된 결과 종목 수
    totcnt = objRq.GetHeaderValue(1)  # 1 - (long) 총 검색 종목 수
    stime = objRq.GetHeaderValue(2)  # 2 - (string) 검색시간
    print('검색된 종목수:', cnt, '전체종목수:', totcnt, '검색시간:', stime)

    for i in range(cnt):
        item = {}
        item['code'] = objRq.GetDataValue(0, i)
        item['종목명'] = g_objCodeMgr.CodeToName(item['code'])
        dataStg.append(item)

    return dataStg


if __name__ == "__main__":

    print(get_code_list())