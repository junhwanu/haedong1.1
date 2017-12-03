# -*- coding: utf-8 -*-
import contract, subject, log, calc, time, my_util
import log_result as res
import define as d


def is_it_OK(subject_code, current_price):
    data = calc.data_day[subject_code]
    false = {'신규주문': False}
    min_prev_flow_length = 5
    define_ma = [3, 10]
    remain_ratio = 0.5
    sonjul_tick = 200

    # 현재가를 금일봉 시가로 넣어서 이평선 계산에 추가
    data[-1]['시가'] = current_price

    # 이동평균선 계산
    calc_ma(subject_code, define_ma)

    # 플로우 계산
    calc_flow(subject_code)

    # 플로우 반전 확인
    if data[-1]['연속플로우'] > 1:
        return false

    # 매도수구분 확인
    if data[-1]['플로우'] == '상향': mesu_medo_type = '신규매수'
    else: mesu_medo_type = '신규매도'

    # 이전 플로우 연속일 계산
    prev_flow_length = 0

    # 이전 플로우 연속일 확인
    if prev_flow_length < min_prev_flow_length:
        return false

    # 매매 계약 수
    contract_cnt = int(contract.my_deposit / (subject.info[subject_code]['위탁증거금'] * (1 + remain_ratio)))

    # 매매
    order_contents = {'신규주문': True, '매도수구분': mesu_medo_type, '익절틱': 9999, '손절틱': sonjul_tick, '수량': contract_cnt}

    return order_contents


def is_it_sell(subject_code, current_price):
    return {'신규주문': False}

def calc_ma(subject_code, define_ma):
    data = calc.data_day[subject_code]

    for i in range(0, len(data)):
        for ma_value in define_ma:
            if ma_value < i:
                if '이동평균선' not in data[i].keys():
                    data[i]['이동평균선'] = []

                sum = 0
                for j in range(i - ma_value + 1, i + 1):
                    sum = sum + data[i]['시가']

                data[i]['이동평균선'].append(sum / ma_value)


def calc_flow(subject_code):
    data = calc.data_day[subject_code]

    for i in range(0, len(data)):
        if len(data[i]['이동평균선']) > 1:
            if data[i]['이동평균선'][0] > data[i]['이동평균선'][1]:
                data[i]['플로우'] = '상향'
            elif data[i]['이동평균선'][0] < data[i]['이동평균선'][1]:
                data[i]['플로우'] = '하향'
            else:
                data[i]['플로우'] = data[i-1]['플로우']

            if data[i]['플로우'] == data[i-1]['플로우']:
                data[i]['연속플로우'] = data[i-1]['연속플로우'] + 1
            else:
                data[i]['연속플로우'] = 1

        else:
            data[i]['플로우'] = '모름'