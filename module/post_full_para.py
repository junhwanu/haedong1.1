# -*- coding: utf-8 -*-
import contract, subject, log, calc, time, my_util
import log_result as res
import define as d

previous_profit = 0
temp_index = 0

def is_it_OK(subject_code, current_price):
    #log.info("[post_full_para] Here is post_full_para is_it_OK!!")

    global previous_profit
    global temp_index
    start_price = subject.info[subject_code]['시가']
    profit = 0
    profit_tick = subject.info[subject_code]['익절틱']
    sonjal_tick = subject.info[subject_code]['손절틱']
    mesu_medo_type = None
    false = {'신규주문': False}
    ma_line_is_true = True
    time_check_is_true = True
    reverse_tic = subject.info[subject_code]['반대매매틱']

    subject.info[subject_code]['체결미스'] = False

    param01 = 160
    param02 = 560
    param03 = 10
    param04 = 720
    param05 = -16  #-24
    param06 = 40
    param07 = 20
    param08 = -40
    param09 = 115 #140
    param10 = 200
    param11 = 30
    param12 = 35
    param13 = 20

    # 300캔들이 없으면 매매 안함
    if calc.data[subject_code]['idx'] < 3000:
        return false

    if subject.info[subject_code]['상태'] == '매수중' or subject.info[subject_code]['상태'] == '매도중' or \
            subject.info[subject_code]['상태'] == '청산시도중' or subject.info[subject_code]['상태'] == '매매시도중':
        log.debug('신규 주문 가능상태가 아니므로 매매 불가. 상태 : ' + subject.info[subject_code]['상태'])
        return false

    if subject.info[subject_code]['flow'] == '상향':
        if current_price < subject.info[subject_code]['sar']:
            return false

        elif calc.data[subject_code]['플로우'][-2] == '하향':
            return false

        for i in range(-1, -len(calc.data[subject_code]['플로우'])-1, -1):
            if calc.data[subject_code]['플로우'][i] == '하향':
                passed_candle_count = i
                break
            if i < - 20: return false

        mesu_medo_type = '신규매수'

        if calc.data[subject_code]['이전반전시SAR값'][-1]  + 10 * subject.info[subject_code]['단위'] < current_price:
            log.info("[post_full_para] 반전값 보다 10틱 이상 올라 신규 매수 포기")
            return false

    elif subject.info[subject_code]['flow'] == '하향':
        if current_price > subject.info[subject_code]['sar']:
            return false

        elif calc.data[subject_code]['플로우'][-2] == '상향':
            return false

        for i in range(-1, -len(calc.data[subject_code]['플로우'])-1, -1):
            if calc.data[subject_code]['플로우'][i] == '상향':
                passed_candle_count = i
                break
            if i < - 20: return false

        mesu_medo_type = '신규매도'

        if calc.data[subject_code]['이전반전시SAR값'][-1] - 10 * subject.info[subject_code]['단위'] > current_price:
            log.info("[post_full_para] 반전값 보다 10틱 이상 떨어져 신규 매도 포기")
            return false

    else:
        return false

    profit = subject.info[subject_code]['수익리스트'][-1]

    if len(subject.info[subject_code]['맞틀리스트']) < 5:
        return false

    if subject.info[subject_code]['반대매매'] == True:
        subject.info[subject_code]['반대매매'] = False
        log.info("[post_full_para] 반대대대 False로 변경.")

    if calc.data[subject_code]['SAR반전시간'][-1] >= calc.data[subject_code]['체결시간'][-1]:  # 반전 후 SAR로 갱신되었다면
        return false

## 여기까지 함

    if mesu_medo_type == '신규매도':
        if my_util.is_sorted_previous(subject_code, passed_candle_count) != '하락세':
            ma_line_is_true = False
    elif mesu_medo_type == '신규매수':
        if my_util.is_sorted_previous(subject_code, passed_candle_count) != '상승세':
            ma_line_is_true = False

    #log.info("[post_full_para] flow_candle_count_list :%s" % calc.flow_candle_count_list[-1])

    if calc.flow_candle_count_list[-1] <= param11:
        log.info("[post_full_para] 지난 캔들이 %s개 미만으로 진입 포기" % param11)
        return false

    elif calc.flow_candle_count_list[-1] <= param09:
        ma_line_is_true = True
        log.info("[post_full_para] 지난 캔들이 140개 이하로 진입")
        pass

    elif subject.info[subject_code]['맞틀리스트'][-1] == '틀' and subject.info[subject_code]['수익리스트'][-1] < param08:
        time_check_is_true = False
        log.info("[post_full_para] 큰 틀 다음으로 매매 진입합니다.")
        pass

    elif subject.info[subject_code]['수익리스트'][-1] > param06:
        log.info("[post_full_para] 지난 플로우 수익이 %s틱 이상으로 진입 포기" % param06)
        return false

    elif subject.info[subject_code]['맞틀리스트'][-3:] == ['틀', '맞', '틀']:
        if calc.flow_candle_count_list[-1] <= param01:
            log.info("[post_full_para] 틀맞틀 로 매매 진입합니다.")
        else:
            log.info("[post_full_para] 틀맞틀일때 지난 플로우 캔들 수가 %s(현재 %s) 이상으로 매매 안합니다" % (param01, calc.flow_candle_count_list[-1]))
            return false

    elif subject.info[subject_code]['맞틀리스트'][-2] == '맞' and subject.info[subject_code]['맞틀리스트'][-1] == '틀':
        log.info("[post_full_para] 맞틀 로 매매 포기")
        return false

    elif subject.info[subject_code]['맞틀리스트'][-5:] == ['틀', '틀', '틀', '틀', '틀']:
        log.info("[post_full_para] 틀틀틀틀틀 다음으로 매매 진입합니다.")
        pass

    elif subject.info[subject_code]['맞틀리스트'][-5:] == ['맞', '틀', '틀', '틀', '틀']:
        if subject.info[subject_code]['수익리스트'][-2] < param05:
            log.info("[post_full_para] 맞틀틀틀틀일때 조건이 맞지 않아 진입 안합니다.")
            return false
        else:
            log.info("[post_full_para] 맞틀틀틀틀 다음으로 매매 진입합니다.")
            pass

    elif subject.info[subject_code]['맞틀리스트'][-4:] == ['틀', '맞', '맞', '맞']:
        if subject.info[subject_code]['수익리스트'][-1] > param12:
            log.info("[post_full_para] 틀틀틀맞 일때 이전 플로우 수익이 %s틱 이상으로 매매 진입 안합니다." % param12)
            return false
        else:
            log.info("[post_full_para] 틀틀틀맞 다음으로 매매 진입합니다.")
            pass

    elif subject.info[subject_code]['맞틀리스트'][-4:] == ['맞', '틀', '맞', '맞']:
        if subject.info[subject_code]['수익리스트'][-2] > param13:
            log.info("[post_full_para] 맞틀맞맞 일때 이전 플로우 수익이 %s틱 이상으로 매매 진입 안합니다." % param13)
            return false
        else:
            log.info("[post_full_para] 맞틀맞맞 다음으로 매매 진입합니다.")
            pass

    elif subject.info[subject_code]['맞틀리스트'][-4:] == ['맞', '틀', '틀', '맞']:
        if subject.info[subject_code]['수익리스트'][-1] > param03:
            log.info("[post_full_para] 맞틀틀맞 일때 이전 플로우 수익이 %s틱 이상으로 매매 진입 안합니다." % param03)
            return false
        else:
            log.info("[post_full_para] 맞틀틀맞 다음으로 매매 진입합니다.")
            pass

    elif subject.info[subject_code]['맞틀리스트'][-4:] == ['틀', '틀', '틀', '맞']:
        if subject.info[subject_code]['수익리스트'][-1] > param07:
            log.info("[post_full_para] 틀틀틀맞 일때 이전 플로우 수익이 %s틱 이상으로 매매 진입 안합니다." % param07)
            return false
        else:
            log.info("[post_full_para] 틀틀틀맞 다음으로 매매 진입합니다.")
            pass

    elif subject.info[subject_code]['맞틀리스트'][-4:] == ['틀', '틀', '맞', '맞']:
        if calc.flow_candle_count_list[-2] > param02 and calc.flow_candle_count_list[-1] < param04:
            log.info("[post_full_para] 틀틀맞맞 일때 조건이 맞지 않아 매매 안합니다.")
            return false
        else:
            log.info("[post_full_para] 틀틀맞맞 다음으로 매매 진입합니다.")

    elif subject.info[subject_code]['맞틀리스트'][-4:] == ['맞', '맞', '틀', '틀']:
        #if subject.info[subject_code]['수익리스트'][-4] < subject.info[subject_code]['수익리스트'][-3]:
        if calc.flow_candle_count_list[-2] > param10:
            log.info("[post_full_para] 맞맞틀틀일때 조건이 맞지 않아 진입 안합니다.")
            return false
        else:
            log.info("[post_full_para] 맞맞틀틀 다음으로 매매 진입합니다.")
            pass

    elif subject.info[subject_code]['맞틀리스트'][-4:] == ['맞', '틀', '틀', '틀']:
        if subject.info[subject_code]['수익리스트'][-2] < param05:
            log.info("[post_full_para] 맞틀틀틀일때 조건이 맞지 않아 진입 안합니다.")
            return false
        else:
            log.info("[post_full_para] 맞틀틀틀 다음으로 매매 진입합니다.")
            pass

    else:
        log.info("[post_full_para] 맞틀 조건이 맞지 않아 매매 포기합니다.")
        return false


    if ma_line_is_true == False: return false

    current_time = int(str(calc.data[subject_code]['체결시간'][passed_candle_count+1])[8:12])

    if current_time <= int(subject.info[subject_code]['시작시간']) and current_time >= int(subject.info[subject_code]['마감시간']):
        log.info("[post_full_para] 장 시작 시간, 마감 시간 정각에 매매하지 않습니다. 매매금지")
        return false

    if subject_code[:3] == "GCZ" or subject_code[:3] == "GCQ":
        if current_time > 2100 and current_time < 2230 and subject.info[subject_code]['반대매매'] == False and time_check_is_true == True:
            log.info("[post_full_para] 21:00~22:30 시 사이라 매매 포기 합니다.")
            return false
    else:
        if current_time > 2200 and current_time < 2330 and subject.info[subject_code]['반대매매'] == False and time_check_is_true == True:
            log.info("[post_full_para] 22:00~23:30 시 사이라 매매 포기 합니다.")
            return false

    if subject.info[subject_code]['반대매매'] == True:
        subject.info[subject_code]['반대매매'] = False
        return false

    if d.get_mode() == d.REAL:  # 실제 투자 할때
        possible_contract_cnt = int(contract.my_deposit / subject.info[subject_code]['위탁증거금'])
        log.info("[post_full_para] possible_contract_cnt %s개 입니다." % possible_contract_cnt)
        contract_cnt = int(contract.my_deposit / 1.2 / subject.info[subject_code]['위탁증거금'])
        log.info("[post_full_para] contract_cnt %s개 입니다." % contract_cnt)
        if contract.recent_trade_cnt == possible_contract_cnt:
            contract_cnt = possible_contract_cnt
        log.info("[post_full_para] 매매 예정 수량은 %s개 입니다." % contract_cnt)
        if contract_cnt == 0:
            contract_cnt = 1
        #
        contract_cnt = 1

        if subject.info[subject_code]['신규매매수량'] != contract_cnt:
            subject.info[subject_code]['신규매매수량'] = contract_cnt
            log.info("[post_full_para] subject.info[subject_code]['신규매매수량'] 조정 :%s" % contract_cnt)

        log.info("[post_full_para] 최종 매매 수량은 %s개 입니다." % contract_cnt)

    else:
        contract_cnt = 2  # 테스트 돌릴때
        subject.info[subject_code]['신규매매수량'] = contract_cnt

    # heejun add `17.8.16
    number_of_current_contract = int(contract.get_contract_count(subject_code))
    if number_of_current_contract > 0 and subject.info[subject_code]['반대매매'] == False:
        return false  # 계약을 가지고 있으면서 반대매매가 아니면 추가매매 금지

    if subject.info[subject_code][
        '반대매매'] == True and number_of_current_contract > 0:  # 만약 1계약이 1차 청산되고 1계약만 드리블 중 반전되었다면 나머지 한계약만 추가 리버스파라 매매 진입
        contract_cnt = contract_cnt - number_of_current_contract
        log.debug("반대매매 True 로 계약수 조정, 계약수: %s개" % contract_cnt)
    ######################

    log.debug("종목코드(" + subject_code + ") 신규 매매 계약 수 " + str(contract_cnt))

    ######
    # contract_cnt = 0
    if contract_cnt == 0: return false

    order_contents = {'신규주문': True, '매도수구분': mesu_medo_type, '익절틱': profit_tick, '손절틱': sonjal_tick, '수량': contract_cnt}
    subject.info[subject_code]['주문내용'] = order_contents
    log.debug('!!!!!! post_para.is_it_OK() : 모든 구매조건 통과.')
    log.debug(order_contents)


    return order_contents


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

    return int(current_time)