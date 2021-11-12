# -*- coding:utf-8 -*-
'''
interface between UI and Module
'''
import pandas as pd

import creonAPI

'''
로그인 담당 class
'''


class access():
    # 필요 데이터 준비
    def __init__(self):
        self.creon = []
        self.newsy = []
        self.con_flag = 0

    # 대신증권 로그인 데이터 추출
    def get_data_creon(self, id, pw, cert):
        self.creon = [id, pw, cert]
        return True

    # 대신증권 api 접속
    def login_creon(self):
        print("def login_creon(self):")
        creonAPI.login(self.creon)
        return True

    # 대신증권 접속 여부 확인
    def check_con(self):
        self.con_flag = creonAPI.check_con()
        return self.con_flag

    def disconnect(self):
        print("def disconnect(self):")
        creonAPI.disconnect()
        # return True

# class autoLogin():
#
#     def __init__(self):
#         self.creon = []
#         self.newsy = []
#         self.con_flag = 0
#
#     # 대신증권 로그인 데이터 추출
#     def get_data_creon(self, id, pw, cert):
#         self.creon = [id, pw, cert]
#         return True
#
#     # 대신증권 api 접속
#     def login_creon(self):
#         print("def login_creon(self):")
#         creonAPI.login(self.creon)
#         return True
#
#     # 대신증권 접속 여부 확인
#     def check_con(self):
#         self.con_flag = creonAPI.check_con()
#         return self.con_flag
#
#     def disconnect(self):
#         print("def disconnect(self):")
#         creonAPI.disconnect()
#         # return True

# 계좌 보유종목 감시 Class
class MarketEye():
    def __init__(self):
        self.acc_num = 0
        self.acc_list = pd.DataFrame()

    def get_acc_num(self):
        self.acc_num = creonAPI.get_user_info(0, 0)
        return self.acc_num


# 금일 매수종목 관리 Class
class Buy_list():
    def __init__(self):
        return 0


# 금일 매도종목 관리 Class
class Sell_list():
    def __init__(self):
        return 0


# 잔고조회
class Account_list():
    def __init__(self):
        self.balance = {}

    def get_account_list(self):
        self.balance = {}

        self.balance = creonAPI.get_account_balance()

        self.codeList = []
        for k, d in self.balance.items():
            print(k, d)
            self.codeList.append(k)

        cur_list = creonAPI.curprice_Request(self.codeList)

        print("curlist : ", cur_list)
        # print(cur_list['A000225']['현재가'])
        for k, d in cur_list.items():
            print(k)
            print(type(k))
            print(str.format(k))
            self.balance[k]["현재가"] = round(cur_list[k]["현재가"], 0)
            curprice = cur_list[k]["현재가"]
            diffprice = cur_list[k]["대비"]
            self.balance[k]["대비"] = round((curprice - (curprice - diffprice)) / (curprice - diffprice) * 100, 1)

        for k, d in self.balance.items():
            print(k, d)

        return self.balance


# ohlcv 정보가져오기
class OHLCV_list():
    def __init__(self):
        self.ohlcv = pd.DataFrame()

    def get_ohlcv_list(self, code, type, num):
        self.ohlcv = pd.DataFrame()
        self.ohlcv = creonAPI.get_ohlcv_info(code, type, num)
        return self.ohlcv


class Code_list():
    def __init__(self):
        self.codelist = pd.DataFrame()

    def get_code_list(self):
        self.codelist = creonAPI.get_code_list()
        return self.codelist


class Stg_list():
    def __init__(self):
        pass

    def get_stg_list(self):
        self.stg_list = creonAPI.requestStgList()
        print('get_stg_list end')
        return self.stg_list

    def get_stg_list_by_id(self, id):
        self.getstglist = creonAPI.requestStgID(id)
        return self.getstglist


if __name__ == "__main__":
    av = access()
    print(av.check_con())
    ma = MarketEye()
    print(ma.get_acc_num())
