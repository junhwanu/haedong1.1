# -*- coding: utf-8 -*-
import contract, subject, log, calc, time, my_util
import log_result as res
import define as d
import db

def is_it_OK(subject_code, current_price):
    profit_tick = 20
    sonjal_tick = 10
    contract_cnt = 2
    mesu_medo_type = None
    min_y_prime = 0.2

    false = {'신규주문': False}

    # 300캔들이 없으면 매매 안함
    if calc.data[subject_code]['idx'] < 251:
        return false

    if subject.info[subject_code]['최근매매인덱스'] > calc.data[subject_code]['idx'] - 300:
        return false

    if subject.info[subject_code]['상태'] == '매수중' or subject.info[subject_code]['상태'] == '매도중' or \
                    subject.info[subject_code]['상태'] == '청산시도중' or subject.info[subject_code]['상태'] == '매매시도중':
        log.debug('신규 주문 가능상태가 아니므로 매매 불가. 상태 : ' + subject.info[subject_code]['상태'])
        return false

    dx = 150
    dy = (calc.data[subject_code]['이동평균선'][100][-1] - calc.data[subject_code]['이동평균선'][100][-dx]) / subject.info[subject_code]['단위']

    if dy > 0: mesu_medo_type = '신규매수'
    else: mesu_medo_type = '신규매도'

    y_prime = abs(dy) / dx;

    if not (y_prime > min_y_prime and ((mesu_medo_type == '신규매수' and calc.data[subject_code]['이동평균선'][100][-1] > calc.data[subject_code]['이동평균선'][100][-(int(dx/2))] > calc.data[subject_code]['이동평균선'][100][-dx]) or (mesu_medo_type == '신규매도' and calc.data[subject_code]['이동평균선'][100][-1] < calc.data[subject_code]['이동평균선'][100][-(int(dx/2))] < calc.data[subject_code]['이동평균선'][100][-dx]))):
        '''
        기울기 50틱 / 150캔들 이하면 매매 안함
        구간 중간에 기울기가 나란히 정렬되어 있지 않으면 매매 안함
        '''
        return false

    if not ((calc.data[subject_code]['이동평균선'][30][-1] - subject.info[subject_code]['단위']) <= current_price <= (calc.data[subject_code]['이동평균선'][30][-1] + subject.info[subject_code]['단위'])):
        '''
        현재가가 30MA +- 1틱 이내로 진입했을 시 매매하기 때문에 그게 아니라면 매매 안함
        '''
        return false

    if (mesu_medo_type == '신규매수' and calc.data[subject_code]['이동평균선'][30][-1] < calc.data[subject_code]['이동평균선'][100][-1]) or (mesu_medo_type == '신규매도' and calc.data[subject_code]['이동평균선'][30][-1] > calc.data[subject_code]['이동평균선'][100][-1]):
        '''
        30, 100MA가 매도수구분과 정렬되지 않을 경우 매매 안함
        '''
        return false

    order_contents = {'신규주문': True, '매도수구분': mesu_medo_type, '익절틱': profit_tick, '손절틱': sonjal_tick, '수량': contract_cnt}
    subject.info[subject_code]['주문내용'] = order_contents
    log.debug('ma30100.is_it_OK() : 모든 구매조건 통과.')
    log.debug(order_contents)
    return order_contents



def is_it_sell(subject_code, current_price):
    index = calc.data[subject_code]['idx']
    sell_contents = None
    
    try:
        if contract.get_contract_count(subject_code) > 0:
            # 계약 보유중
            if contract.list[subject_code]['매도수구분'] == '신규매수':
                if current_price - subject.info[subject_code]['손절틱'] * subject.info[subject_code]['단위'] > contract.list[subject_code]['손절가']:
                    contract.list[subject_code]['손절가'] = current_price - subject.info[subject_code]['손절틱'] * subject.info[subject_code]['단위']

                if current_price <= contract.list[subject_code]['손절가']:
                    log.info("매수간 손절가가 되어 청산 요청. (현재가 : %s, 체결가 : %s, 익절가 : %s, 손절가 : %s)" % (current_price, contract.list[subject_code]['체결가'], contract.list[subject_code]['익절가'], contract.list[subject_code]['손절가']))
                    sell_contents = {'신규주문': True, '매도수구분': '신규매도', '수량': contract.get_contract_count(subject_code)}

                elif current_price >= contract.list[subject_code]['익절가']:
                    log.info("현재가가 익절가가 되어 1차 청산 요청. (현재가 : %s, 체결가 : %s, 익절가 : %s, 손절가 : %s)" % (current_price, contract.list[subject_code]['체결가'], contract.list[subject_code]['익절가'], contract.list[subject_code]['손절가']))
                    contract.list[subject_code]['익절가'] = 9999
                    sell_contents = {'신규주문': True, '매도수구분': '신규매도', '수량': int(contract.get_contract_count(subject_code)/2)}

                elif current_price <= calc.data[subject_code]['이동평균선'][100][-1] and contract.list[subject_code]['체결가'] < calc.data[subject_code]['이동평균선'][100][-1]:
                    log.info("현재가가 100MA에 닿아 청산 요청. (현재가 : %s, 체결가 : %s, 익절가 : %s, 손절가 : %s)" % (current_price, contract.list[subject_code]['체결가'], contract.list[subject_code]['익절가'], contract.list[subject_code]['손절가']))
                    sell_contents = {'신규주문': True, '매도수구분': '신규매도', '수량': contract.get_contract_count(subject_code)}

            elif contract.list[subject_code]['매도수구분'] == '신규매도':
                if current_price + subject.info[subject_code]['손절틱'] * subject.info[subject_code]['단위'] < contract.list[subject_code]['손절가']:
                    contract.list[subject_code]['손절가'] = current_price + subject.info[subject_code]['손절틱'] * subject.info[subject_code]['단위']

                if current_price >= contract.list[subject_code]['손절가']:
                    log.info("매도간 손절가가 되어 청산 요청. (현재가 : %s, 체결가 : %s, 익절가 : %s, 손절가 : %s)" % (current_price, contract.list[subject_code]['체결가'], contract.list[subject_code]['익절가'], contract.list[subject_code]['손절가']))
                    sell_contents = {'신규주문': True, '매도수구분': '신규매수', '수량': contract.get_contract_count(subject_code)}

                elif current_price <= contract.list[subject_code]['익절가']:
                    log.info("현재가가 익절가가 되어 1차 청산 요청. (현재가 : %s, 체결가 : %s, 익절가 : %s, 손절가 : %s)" % (current_price, contract.list[subject_code]['체결가'], contract.list[subject_code]['익절가'], contract.list[subject_code]['손절가']))
                    contract.list[subject_code]['익절가'] = -9999
                    sell_contents = {'신규주문': True, '매도수구분': '신규매수', '수량': int(contract.get_contract_count(subject_code)/2)}

                elif current_price >= calc.data[subject_code]['이동평균선'][100][-1] and contract.list[subject_code]['체결가'] > calc.data[subject_code]['이동평균선'][100][-1]:
                    log.info("현재가가 100MA에 닿아 청산 요청. (현재가 : %s, 체결가 : %s, 익절가 : %s, 손절가 : %s)" % (current_price, contract.list[subject_code]['체결가'], contract.list[subject_code]['익절가'], contract.list[subject_code]['손절가']))
                    sell_contents = {'신규주문': True, '매도수구분': '신규매수', '수량': contract.get_contract_count(subject_code)}

    except Exception as err:
        log.error(err)

    if sell_contents is not None:
        subject.info[subject_code]['최근매매인덱스'] = index
        return sell_contents
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
        '''
        current_hour = int(str(calc.data[subject_code]['체결시간'][-1])[8:10])
        current_min = int(str(calc.data[subject_code]['체결시간'][-1])[10:12])
        current_min += add_min
        if current_min >= 60:
            current_hour += 1
            current_min -= 60

        current_time = current_hour * 100 + current_min
        '''
        current_time = int(str(calc.data[subject_code]['체결시간'][-1])[8:12])

    return current_time
