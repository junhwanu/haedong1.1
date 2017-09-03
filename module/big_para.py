# -*- coding: utf-8 -*-
import contract, subject, log, calc, time, my_util
import define as d
import log_result as res
import datetime

def is_it_OK(subject_code, current_price):
    profit_tick = 10
    loss_tick = 10
    mesu_medo_type = ''
    contract_cnt = 2
    index = calc.data[subject_code]['idx']
    false = {'신규주문':False}

    if calc.data[subject_code]['idx'] < 300:
        return false

    state = subject.info[subject_code]['상태']
    if state == '매수중' or state == '매도중': return false

    elif state == '매매완료':
        if subject.info[subject_code]['flow'] == '하향' and subject.info[subject_code]['sar'] < current_price:
            subject.info[subject_code]['상태'] = '매수가능'
        elif subject.info[subject_code]['flow'] == '상향' and subject.info[subject_code]['sar'] > current_price:
            subject.info[subject_code]['상태'] = '매도가능'
    elif state == '매수가능' or state == '매도가능':
        if state == '매수가능' and my_util.is_sorted(subject_code) == '상승세':
                res.info('종목(' + subject_code + ') 현재 상승세이므로 매수 시도.')
                mesu_medo_type = '신규매수'
                profit_tick = subject.info[subject_code]['익절틱']
                loss_tick = subject.info[subject_code]['손절틱']
                contract_cnt = 2
        elif state == '매도가능' and my_util.is_sorted(subject_code) == '하락세':
                res.info('종목(' + subject_code + ') 현재 하락세이므로 매도 시도.')
                mesu_medo_type = '신규매도'
                profit_tick = subject.info[subject_code]['익절틱']
                loss_tick = subject.info[subject_code]['손절틱']
                contract_cnt = 2
        else:
            subject.info[subject_code]['상태'] = '매매완료' 
            return false
    else: return false
    
    order_contents = {'신규주문':True, '매도수구분':mesu_medo_type, '익절틱':profit_tick, '손절틱':loss_tick, '수량':contract_cnt}
    '''
    res.info('##### 주문 예정 #####')
    res.info(order_contents)
    chart.draw(subject_code)
    input()
    '''
    
    return order_contents

def is_it_sell(subject_code, current_price):
    index = calc.data[subject_code]['idx']
    if contract.get_contract_count(subject_code) > 0:
        # 계약 보유중
        if contract.list[subject_code]['매도수구분'] == '신규매수':
            # 매수일때
            if current_price <= contract.list[subject_code]['손절가']:
                res.info("손절가가 되어 " + str(contract.list[subject_code]['계약타입'][contract.SAFE] + contract.list[subject_code]['계약타입'][contract.DRIBBLE]) + "개 청산 요청.")
                return {'신규주문':True, '매도수구분':'신규매도', '수량':contract.list[subject_code]['계약타입'][contract.SAFE] + contract.list[subject_code]['계약타입'][contract.DRIBBLE]}
            elif calc.data[subject_code]['플로우'][-1] == '상향' and subject.info[subject_code]['sar'] > current_price:
                res.info("하향 반전되어 " + str(contract.list[subject_code]['계약타입'][contract.SAFE] + contract.list[subject_code]['계약타입'][contract.DRIBBLE]) + "개 청산 요청.")
                return {'신규주문':True, '매도수구분':'신규매도', '수량':contract.list[subject_code]['계약타입'][contract.SAFE] + contract.list[subject_code]['계약타입'][contract.DRIBBLE]}
            elif current_price > contract.list[subject_code]['익절가']:
                contract.list[subject_code]['익절가'] = current_price + subject.info[subject_code]['익절틱'] * subject.info[subject_code]['단위']
                contract.list[subject_code]['손절가'] = current_price - subject.info[subject_code]['익절틱'] * subject.info[subject_code]['단위']
        elif contract.list[subject_code]['매도수구분'] == '신규매도':
            # 매도일때
            if current_price >= contract.list[subject_code]['손절가']:
                res.info("손절가가 되어 " + str(contract.list[subject_code]['계약타입'][contract.SAFE] + contract.list[subject_code]['계약타입'][contract.DRIBBLE]) + "개 청산 요청.")
                return {'신규주문':True, '매도수구분':'신규매수', '수량':contract.list[subject_code]['계약타입'][contract.SAFE] + contract.list[subject_code]['계약타입'][contract.DRIBBLE]}
            elif calc.data[subject_code]['플로우'][-1] == '하향' and subject.info[subject_code]['sar'] < current_price:
                res.info("상향 반전되어 " + str(contract.list[subject_code]['계약타입'][contract.SAFE] + contract.list[subject_code]['계약타입'][contract.DRIBBLE]) + "개 청산 요청.")
                return {'신규주문':True, '매도수구분':'신규매수', '수량':contract.list[subject_code]['계약타입'][contract.SAFE] + contract.list[subject_code]['계약타입'][contract.DRIBBLE]}
            elif current_price < contract.list[subject_code]['익절가']:
                contract.list[subject_code]['익절가'] = current_price - subject.info[subject_code]['익절틱'] * subject.info[subject_code]['단위']
                contract.list[subject_code]['손절가'] = current_price + subject.info[subject_code]['익절틱'] * subject.info[subject_code]['단위']
    return {'신규주문':False}

def get_time(add_min):
    # 현재 시간 정수형으로 return
    current_hour = time.localtime().tm_hour
    current_min = time.localtime().tm_min
    if current_min + add_min >= 60:
        current_hour += 1
        current_min -= 60

    current_time = current_hour*100 + current_min

    return current_time
