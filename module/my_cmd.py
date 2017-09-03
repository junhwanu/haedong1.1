# -*- coding: utf-8 -*-
import threading
import sys, os
import subject, contract, log, kiwoom


class proc(threading.Thread):
    def run(self):
        while True:
            my_cmd = input()
            print(my_cmd)

            if my_cmd == 'help':
                pass
                # 메뉴 번호 안내
            elif my_cmd == '1':
                rtn = kiwoom.get_instance().send_order('신규매도', '0101', kiwoom.get_instance().account, 1, 'CLG17', 1, '0', '0', '1', '')
                log.debug("주문 rtn : " + str(rtn))
                pass
            elif my_cmd == '2':
                rtn = kiwoom.get_instance().send_order('신규매수', '0101', kiwoom.get_instance().account, 2, 'CLG17', 1, '0', '0', '1', '')
                log.debug("주문 rtn : " + str(rtn))
                # 그래프 확인, 종목정보로 구분
                pass

    def print_help(self):
        print("################# 명령어 #################")
        print("1. 보유 계약 정보")
        print("2. 그래프 확인")

    def print_contract_list(self):
        list = contract.get_order_number_list()

        print("############# 보유 계약 정보 #############")
        for order_number in list:
            print(contract.list[order_number])

        print("##########################################")


cmd = proc()
def init():
    cmd.start()

def get_instance():
    return cmd