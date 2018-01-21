# -*- coding: utf-8 -*-
import contract, subject, log, calc, time, my_util
import log_result as res
import define as d
import db

previous_profit = 0
temp_index = 0


def is_it_OK(subject_code, current_price):
    #살까 말까 판단!!
    #order_contents여기서 신규 주문이 True면 레알 사고팔고 false면 안삼~!
    false = {'신규주문': False}
    #안살꺼면
    #return false
    profit_tick = subject.info[subject_code]['익절틱']
    sonjal_tick = subject.info[subject_code]['손절틱']
    mesu_medo_type = None
    contract_cnt=2

    # print(calc.data_day)
    # 레알 사는거면 mesu_medo_type가 신규매수 or 신규매도 여야지만 됨!
    order_contents = {'신규주문': True, '매도수구분': mesu_medo_type, '익절틱': profit_tick, '손절틱': sonjal_tick, '수량': contract_cnt}
    #아직 이건없듬!
    log.info(subject.info[subject_code]['현재캔들'])
    subject.info[subject_code]['주문내용'] = order_contents
    log.info('para.is_it_OK() : 모든 구매조건 통과.')
    log.info(order_contents)
    return order_contents



def is_it_sell(subject_code, current_price):
    #팔지말지 판단 살때랑 똑같음~! return {'신규주문': False}이거면 안팜!
    '''팔때는 return {'신규주문': True, '매도수구분': '신규매도',
                            '수량': contract.list[subject_code]['계약타입'][contract.SAFE] +
                                  contract.list[subject_code]['계약타입'][contract.DRIBBLE]}
        위처럼 하면 100프로 다파는거!
        ※참고~! contract.SAFE 가 1차 청산때 파는거고 contract.DRIBBLE]이 2차 청산때 파는거~!
    '''

    return {'신규주문': False}


def get_time(add_min, subject_code):
    # 현재 시간 정수형으로 return
    if d.get_mode() == d.REAL:  # 실제투자
        current_hour = time.localtime().tm_hour
        current_min = time.localtime().tm_min
        current_min += add_min
        if current_min >= 60:
            current_hour += 1
            current_min -= 60

        current_time = current_hour * 100 + current_min

    elif d.get_mode() == d.TEST:  # 테스트
        current_hour = int(str(calc.data[subject_code]['체결시간'][-1])[8:10])
        current_min = int(str(calc.data[subject_code]['체결시간'][-1])[10:12])
        current_min += add_min
        if current_min >= 60:
            current_hour += 1
            current_min -= 60

        current_time = current_hour * 100 + current_min

        current_time = int(str(calc.data[subject_code]['체결시간'][-1])[8:12])

    return current_time
