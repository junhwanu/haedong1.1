# -*- coding: utf-8 -*-
import contract, subject, log, calc, time, my_util
import log_result as res
import define as d
import db

previous_profit = 0
temp_index = 0


def is_it_OK(subject_code, current_price):
    global previous_profit
    global temp_index
    start_price = subject.info[subject_code]['시가']
    profit = 0
    profit_tick = subject.info[subject_code]['익절틱']
    sonjal_tick = subject.info[subject_code]['손절틱']
    mesu_medo_type = None
    false = {'신규주문': False}
    ma_line_is_true = True
    reverse_tic = subject.info[subject_code]['반대매매틱']

    if calc.data[subject_code]['idx'] < 300:
        return false

    if subject.info[subject_code]['상태'] == '매수중' or subject.info[subject_code]['상태'] == '매도중' or \
                    subject.info[subject_code]['상태'] == '청산시도중' or subject.info[subject_code]['상태'] == '매매시도중':
        log.debug('신규 주문 가능상태가 아니므로 매매 불가. 상태 : ' + subject.info[subject_code]['상태'])
        return false

    # log.debug("종목코드(" + subject_code + ")  현재 Flow : " + subject.info[subject_code]['flow'] + " / SAR : " + str(subject.info[subject_code]['sar']) + " / 추세 : " + my_util.is_sorted(subject_code))
    if subject.info[subject_code]['flow'] == '상향':
        if current_price < subject.info[subject_code]['sar']:
            log.debug("종목코드(" + subject_code + ") 하향 반전.")
            profit = current_price - calc.data[subject_code]['이전반전시SAR값'][-1]
            if len(calc.data[subject_code]['SAR반전시간']) > 0 and calc.data[subject_code]['SAR반전시간'][-1] == \
                    calc.data[subject_code]['체결시간'][-1]:  # 반전 후 SAR로 갱신되었다면
                profit = current_price - calc.data[subject_code]['이전반전시SAR값'][-2]

            if my_util.is_sorted(subject_code) == '하락세':
                mesu_medo_type = '신규매도'
            else:
                res.info("이동평균선이 맞지 않아 매수 포기합니다.")
                ma_line_is_true = False
                # return false

        elif calc.data[subject_code]['플로우'][-2] == '하향':
            log.debug("종목코드(" + subject_code + ") 상향 반전.")
            profit = calc.data[subject_code]['이전반전시SAR값'][-1] - current_price
            if len(calc.data[subject_code]['SAR반전시간']) > 0 and calc.data[subject_code]['SAR반전시간'][-1] == \
                    calc.data[subject_code]['체결시간'][-1]:  # 반전 후 SAR로 갱신되었다면
                profit = calc.data[subject_code]['이전반전시SAR값'][-2] - current_price

            if my_util.is_sorted(subject_code) == '상승세':
                mesu_medo_type = '신규매수'

            else:
                res.info("이동평균선이 맞지 않아 매수 포기합니다.")
                ma_line_is_true = False
                # return false
        else:
            return false

    elif subject.info[subject_code]['flow'] == '하향':
        if current_price > subject.info[subject_code]['sar']:
            log.debug("종목코드(" + subject_code + ") 상향 반전.")
            profit = calc.data[subject_code]['이전반전시SAR값'][-1] - current_price
            if len(calc.data[subject_code]['SAR반전시간']) > 0 and calc.data[subject_code]['SAR반전시간'][-1] == \
                    calc.data[subject_code]['체결시간'][-1]:  # 반전 후 SAR로 갱신되었다면
                profit = calc.data[subject_code]['이전반전시SAR값'][-2] - current_price

            if my_util.is_sorted(subject_code) == '상승세':
                mesu_medo_type = '신규매수'

            else:
                res.info("이동평균선이 맞지 않아 매수 포기합니다.")
                ma_line_is_true = False
                # return false

        elif calc.data[subject_code]['플로우'][-2] == '상향':
            log.debug("종목코드(" + subject_code + ") 하향 반전.")
            profit = current_price - calc.data[subject_code]['이전반전시SAR값'][-1]
            if len(calc.data[subject_code]['SAR반전시간']) > 0 and calc.data[subject_code]['SAR반전시간'][-1] == \
                    calc.data[subject_code]['체결시간'][-1]:  # 반전 후 SAR로 갱신되었다면
                profit = current_price - calc.data[subject_code]['이전반전시SAR값'][-2]

            if my_util.is_sorted(subject_code) == '하락세':
                mesu_medo_type = '신규매도'

            else:
                res.info("이동평균선이 맞지 않아 매수 포기합니다.")
                ma_line_is_true = False
                # return false
        else:
            return false
    else:
        return false

    profit = profit / subject.info[subject_code]['단위']

    if len(subject.info[subject_code]['맞틀리스트']) < 5:
        return false

    if subject.info[subject_code]['반대매매'] == True:
        subject.info[subject_code]['반대매매'] = False
        log.info("반대대대 False로 변경.")

    if len(calc.data[subject_code]['SAR반전시간']) > 0 and calc.data[subject_code]['SAR반전시간'][-1] == \
            calc.data[subject_code]['체결시간'][-1]:  # 반전 후 SAR로 갱신되었다면

        if subject.info[subject_code]['맞틀리스트'][-2] == '맞' and subject.info[subject_code]['맞틀리스트'][-1] == '틀':
            if subject.info[subject_code]['수익리스트'][-2] > 70:
                log.info("지지난 플로우가 70이상 수익으로 진입안합니다.")
                return false
            else:
                pass

        if subject.info[subject_code]['맞틀리스트'][-4:] == ['틀','틀', '틀', '틀']:
            log.info("틀틀틀틀 다음으로 매매 진입합니다.")
            pass

        elif subject.info[subject_code]['맞틀리스트'][-4:] == ['틀','맞', '맞', '틀']:
            log.info("틀맞맞틀 다음으로 매매 진입합니다.")
            pass

        elif subject.info[subject_code]['맞틀리스트'][-4:] == ['틀','맞', '틀', '틀']:

            log.info("틀맞틀틀 다음으로 매매 진입합니다.")
            pass

        elif subject.info[subject_code]['맞틀리스트'][-4:] == ['맞','틀', '틀', '맞']:
            if subject.info[subject_code]['수익리스트'][-1] > 10:
                log.info("이전 플로우 수익이 10틱 이상으로 매매 진입 안합니다.")
                return false
            else:
                log.info("맞틀틀맞 다음으로 매매 진입합니다.")
                pass

        elif subject.info[subject_code]['맞틀리스트'][-4:] == ['틀', '틀', '틀', '맞']:
            log.info("틀틀틀맞 다음으로 매매 진입합니다.")
            pass

        elif subject.info[subject_code]['맞틀리스트'][-4:] == ['맞', '맞', '맞', '틀']:
            log.info("맞맞맞틀 다음으로 매매 진입합니다.")
            pass

        elif subject.info[subject_code]['맞틀리스트'][-4:] == ['틀', '틀', '맞', '맞']:
            log.info("틀틀맞맞 다음으로 매매 진입합니다.")
            pass

        elif subject.info[subject_code]['맞틀리스트'][-4:] == ['맞', '맞', '틀', '틀']:
            log.info("맞맞틀틀 다음으로 매매 진입합니다.")
            pass

        elif subject.info[subject_code]['맞틀리스트'][-3:] == ['틀', '맞', '틀']:

            if subject.info[subject_code]['수익리스트'][-2] > 70:
                log.info("지지난 플로우가 70이상 수익으로 진입안합니다.")
                return false
            else:
                log.info("틀맞틀 다음으로 매매 진입합니다.")
                pass

        elif subject.info[subject_code]['맞틀리스트'][-3:] == ['맞', '틀', '맞'] and profit > reverse_tic:
            if mesu_medo_type == '신규매도':
                mesu_medo_type = '신규매수'
            elif mesu_medo_type == '신규매수':
                mesu_medo_type = '신규매도'
            log.info("[%s] 반대매매 조건이 맞아 반대 매매 진입합니다." % mesu_medo_type)
            ma_line_is_true = True
            subject.info[subject_code]['반대매매'] = True


        else:
            log.info("맞틀 조건이 맞지 않아 매매 포기합니다.")
            return false

    else:

        if subject.info[subject_code]['맞틀리스트'][-1] == '맞' and profit < 0:
            if subject.info[subject_code]['수익리스트'][-1] > 70:
                log.info("지지난 플로우가 70이상 수익으로 진입안합니다.")
                return false
            else:
                pass


        if subject.info[subject_code]['맞틀리스트'][-3:] == ['틀', '틀', '틀'] and profit < 0:
            log.info("틀틀틀틀 다음으로 매매 진입합니다.")
            pass

        elif subject.info[subject_code]['맞틀리스트'][-3:] == ['틀', '맞', '맞'] and profit < 0:
            log.info("틀맞맞틀 다음으로 매매 진입합니다.")
            pass

        elif subject.info[subject_code]['맞틀리스트'][-3:] == ['틀', '맞', '틀'] and profit < 0:
            log.info("틀맞틀틀 다음으로 매매 진입합니다.")
            pass

        elif subject.info[subject_code]['맞틀리스트'][-3:] == ['맞', '틀', '틀'] and profit > 0:
            if profit > 10:
                log.info("이전 플로우 수익이 10틱 이상으로 매매 진입 안합니다.")
                return false
            else:
                log.info("맞틀틀맞 다음으로 매매 진입합니다.")
                pass

        elif subject.info[subject_code]['맞틀리스트'][-3:] == ['틀', '틀', '틀'] and profit > 0:
            log.info("틀틀틀맞 다음으로 매매 진입합니다.")
            pass

        elif subject.info[subject_code]['맞틀리스트'][-3:] == ['맞', '맞', '맞'] and profit < 0:
            log.info("맞맞맞틀 다음으로 매매 진입합니다.")
            pass

        elif subject.info[subject_code]['맞틀리스트'][-3:] == ['틀', '틀', '맞'] and profit > 0:
            log.info("틀틀맞맞 다음으로 매매 진입합니다.")
            pass

        elif subject.info[subject_code]['맞틀리스트'][-3:] == ['맞','맞', '틀'] and profit < 0:
            log.info("맞맞틀틀 다음으로 매매 진입합니다.")
            pass

        elif subject.info[subject_code]['맞틀리스트'][-2:] == ['틀', '맞'] and profit < 0:
            if subject.info[subject_code]['수익리스트'][-1] > 70:
                log.info("지지난 플로우가 70이상 수익으로 진입안합니다.")
                return false
            else:
                log.info("틀맞틀 다음으로 매매 진입합니다.")
                pass


        elif subject.info[subject_code]['맞틀리스트'][-2:] == ['맞', '틀'] and profit > reverse_tic:
            if mesu_medo_type == '신규매도':
                mesu_medo_type = '신규매수'
            elif mesu_medo_type == '신규매수':
                mesu_medo_type = '신규매도'
            log.info("[%s] 반대매매 조건이 맞아 반대 매매 진입합니다." % mesu_medo_type)
            ma_line_is_true = True
            subject.info[subject_code]['반대매매'] = True


        else:
            log.info("맞틀 조건이 맞지 않아 매매 포기합니다.")
            return false

    if ma_line_is_true == False: return false


    #썸머타임 일때
    if get_time(0, subject_code) > 2100 and get_time(0, subject_code) < 2230 and subject.info[subject_code][
        '반대매매'] == False:
        log.info("21:00~22:30 시 사이라 매매 포기 합니다.")
        return false

    elif get_time(0, subject_code) == int(subject.info[subject_code]['시작시간']) or get_time(0, subject_code) == int(
            subject.info[subject_code]['마감시간']):
        log.info("장 시작 시간, 마감 시간 정각에 매매하지 않습니다. 매매금지")
        return false

    # contract_cnt = 2
    if d.get_mode() == d.REAL:  # 실제 투자 할때
        possible_contract_cnt = int(contract.my_deposit / subject.info[subject_code]['위탁증거금'])
        log.info("possible_contract_cnt %s개 입니다." % possible_contract_cnt)
        contract_cnt = int(contract.my_deposit / 1.2 / subject.info[subject_code]['위탁증거금'])
        log.info("contract_cnt %s개 입니다." % contract_cnt)
        if contract.recent_trade_cnt == possible_contract_cnt:
            contract_cnt = possible_contract_cnt
        log.info("매매 예정 수량은 %s개 입니다." % contract_cnt)
        if contract_cnt == 0:
            contract_cnt = 2
        #
        contract_cnt = 1

    else:
        contract_cnt = 2  # 테스트 돌릴때

    if contract_cnt > 1:
        subject.info[subject_code]['신규매매수량'] = contract_cnt
    elif contract_cnt == 1:
        subject.info[subject_code]['신규매매수량'] = 2 #1계약만 살수 있을 때 신규매매수량이 1이면 1차 청산 되어버려 2로 고정

    # heejun add `17.8.16
    number_of_current_contract = int(contract.get_contract_count(subject_code))
    if number_of_current_contract > 0 and subject.info[subject_code][
        '반대매매'] == False: return false  # 계약을 가지고 있으면서 반대매매가 아니면 추가매매 금지

    if subject.info[subject_code]['반대매매'] == True:  # 만약 1계약이 1차 청산되고 1계약만 드리블 중 반전되었다면 나머지 한계약만 추가 리버스파라 매매 진입
        contract_cnt = contract_cnt - number_of_current_contract
    ######################

    log.debug("종목코드(" + subject_code + ") 신규 매매 계약 수 " + str(contract_cnt))

    ######
    #contract_cnt = 0
    if contract_cnt == 0: return false


    order_contents = {'신규주문': True, '매도수구분': mesu_medo_type, '익절틱': profit_tick, '손절틱': sonjal_tick, '수량': contract_cnt}
    subject.info[subject_code]['주문내용'] = order_contents
    log.debug('para.is_it_OK() : 모든 구매조건 통과.')
    log.debug(order_contents)
    return order_contents



def is_it_sell(subject_code, current_price):
    index = calc.data[subject_code]['idx']

    try:
        first_chungsan = 77
        first_chungsan_dribble = 5

        second_chungsan = 200
        second_chungsan_dribble = 15

        sar_before_reverse_tic = 0

        # log.debug("종목코드(" + subject_code + ") is_it_sell() 진입.")
        # log.debug("종목코드(" + subject_code + ") 현재 Flow : " + subject.info[subject_code]['flow'] + " / SAR : " + str(subject.info[subject_code]['sar']))
        if contract.get_contract_count(subject_code) > 0:
            # 계약 보유중
            # log.debug("종목코드(" + subject_code + ") is_it_sell() / 보유 계약 : " + str(contract.get_contract_count(subject_code)))
            if contract.list[subject_code]['매도수구분'] == '신규매수':
                # 매수일때
                if calc.data[subject_code]['현재플로우최극가'] - (
                            subject.info[subject_code]['손절틱'] * subject.info[subject_code]['단위']) > current_price:
                    res.info("손절가가 되어 " + str(
                        contract.list[subject_code]['계약타입'][contract.SAFE] + contract.list[subject_code]['계약타입'][
                            contract.DRIBBLE]) + "개 청산 요청.")
                    return {'신규주문': True, '매도수구분': '신규매도',
                            '수량': contract.list[subject_code]['계약타입'][contract.SAFE] +
                                  contract.list[subject_code]['계약타입'][
                                      contract.DRIBBLE]}

                elif current_price <= float(contract.list[subject_code]['체결가']) - (subject.info[subject_code]['리버스손절틱'] * subject.info[subject_code]['단위']):
                    res.info("반대매매 리버스 손절가가 되어 " + str(contract.list[subject_code]['계약타입'][contract.SAFE] + contract.list[subject_code]['계약타입'][contract.DRIBBLE]) + "개 청산 요청.")
                    return {'신규주문': True, '매도수구분': '신규매도',
                            '수량': contract.list[subject_code]['계약타입'][contract.SAFE] +
                                  contract.list[subject_code]['계약타입'][contract.DRIBBLE]}

                elif current_price <= contract.list[subject_code]['손절가']:

                    if contract.get_contract_count(subject_code) == subject.info[subject_code]['신규매매수량']:
                        #1차 청산일 때
                        contract.list[subject_code]['손절가'] = current_price - subject.info[subject_code]['익절틱'] * \
                                                                             subject.info[subject_code]['단위']
                        contract_num = int((contract.list[subject_code]['계약타입'][contract.SAFE] +
                                            contract.list[subject_code]['계약타입'][contract.DRIBBLE]) / 2)
                        if contract_num < 1: return {'신규주문': False}
                        res.info("손절가가 되어 " + str(contract_num) + "개 청산 요청.")
                        return {'신규주문': True, '매도수구분': '신규매도', '수량': contract_num}
                    else:
                        #1차 청산 이후 청산일 때
                        res.info("손절가가 되어 " + str(contract.list[subject_code]['계약타입'][contract.SAFE] +
                                                  contract.list[subject_code]['계약타입'][
                                                      contract.DRIBBLE]) + "개 청산 요청.")
                        return {'신규주문': True, '매도수구분': '신규매도',
                                '수량': contract.list[subject_code]['계약타입'][contract.SAFE] +
                                      contract.list[subject_code]['계약타입'][contract.DRIBBLE]}
                elif calc.data[subject_code]['플로우'][-1] == '상향' and subject.info[subject_code]['sar'] > current_price:
                    if subject.info[subject_code]['반대매매'] == False:
                        res.info("하향 반전되어 " + str(
                            contract.list[subject_code]['계약타입'][contract.SAFE] + contract.list[subject_code]['계약타입'][
                                contract.DRIBBLE]) + "개 청산 요청.")
                        return {'신규주문': True, '매도수구분': '신규매도',
                                '수량': contract.list[subject_code]['계약타입'][contract.SAFE] +
                                      contract.list[subject_code]['계약타입'][contract.DRIBBLE]}

                elif calc.data[subject_code]['플로우'][-1] == '하향' and subject.info[subject_code]['sar'] < current_price:
                    if subject.info[subject_code]['반대매매'] == True:
                        res.info("상향 반전되어 " + str(contract.list[subject_code]['계약타입'][contract.SAFE] +
                                                  contract.list[subject_code]['계약타입'][
                                                      contract.DRIBBLE]) + "개 청산 요청.")
                        return {'신규주문': True, '매도수구분': '신규매도',
                                '수량': contract.list[subject_code]['계약타입'][contract.SAFE] +
                                      contract.list[subject_code]['계약타입'][contract.DRIBBLE]}
                elif current_price > contract.list[subject_code]['익절가']:
                    contract.list[subject_code]['익절가'] = current_price + subject.info[subject_code]['익절틱'] * \
                                                                         subject.info[subject_code]['단위']
                    contract.list[subject_code]['손절가'] = current_price - subject.info[subject_code]['익절틱'] * \
                                                                         subject.info[subject_code]['단위']
                    log.debug("종목코드(" + subject_code + ") 익절가 갱신.")
                elif current_price - float(contract.list[subject_code]['체결가']) >= first_chungsan * \
                        subject.info[subject_code]['단위'] and contract.get_contract_count(subject_code) == \
                        subject.info[subject_code]['신규매매수량']:
                    if contract.list[subject_code]['손절가'] < current_price - first_chungsan_dribble * \
                            subject.info[subject_code]['단위']:
                        contract.list[subject_code]['손절가'] = current_price - first_chungsan_dribble * \
                                                                             subject.info[subject_code]['단위']
                        res.info("1차 청산 드리블 중 %s" % contract.list[subject_code]['손절가'])
                elif current_price - float(contract.list[subject_code]['체결가']) >= second_chungsan * \
                        subject.info[subject_code]['단위'] and contract.get_contract_count(subject_code) == int(
                                subject.info[subject_code]['신규매매수량'] - int(subject.info[subject_code]['신규매매수량'] / 2)):
                    if contract.list[subject_code]['손절가'] < current_price - second_chungsan_dribble * \
                            subject.info[subject_code]['단위']:
                        contract.list[subject_code]['손절가'] = current_price - second_chungsan_dribble * \
                                                                             subject.info[subject_code]['단위']
                        res.info("2차 청산 드리블 중 %s" % contract.list[subject_code]['손절가'])
                        # return {'신규주문':True, '매도수구분':'신규매도', '수량':int((contract.list[subject_code]['계약타입'][contract.SAFE] + contract.list[subject_code]['계약타입'][contract.DRIBBLE]+1)/2)}
            elif contract.list[subject_code]['매도수구분'] == '신규매도':
                # 매도일때
                if calc.data[subject_code]['현재플로우최극가'] + (
                            subject.info[subject_code]['손절틱'] * subject.info[subject_code]['단위']) < current_price:
                    res.info("손절가가 되어 " + str(
                        contract.list[subject_code]['계약타입'][contract.SAFE] + contract.list[subject_code]['계약타입'][
                            contract.DRIBBLE]) + "개 청산 요청.")
                    return {'신규주문': True, '매도수구분': '신규매수',
                            '수량': contract.list[subject_code]['계약타입'][contract.SAFE] +
                                  contract.list[subject_code]['계약타입'][
                                      contract.DRIBBLE]}

                elif current_price >= float(contract.list[subject_code]['체결가']) + (subject.info[subject_code]['리버스손절틱'] * subject.info[subject_code]['단위']):
                    res.info("반대매매 리버스 손절가가 되어 " + str(contract.list[subject_code]['계약타입'][contract.SAFE] + contract.list[subject_code]['계약타입'][contract.DRIBBLE]) + "개 청산 요청.")
                    return {'신규주문': True, '매도수구분': '신규매수',
                            '수량': contract.list[subject_code]['계약타입'][contract.SAFE] +
                                  contract.list[subject_code]['계약타입'][contract.DRIBBLE]}



                elif current_price >= contract.list[subject_code]['손절가']:

                    if contract.get_contract_count(subject_code) == subject.info[subject_code]['신규매매수량']:
                        #1차 청산일 때
                        contract.list[subject_code]['손절가'] = current_price + subject.info[subject_code]['익절틱'] * \
                                                                             subject.info[subject_code]['단위']
                        contract_num = int((contract.list[subject_code]['계약타입'][contract.SAFE] +
                                            contract.list[subject_code]['계약타입'][contract.DRIBBLE]) / 2)
                        if contract_num < 1: return {'신규주문': False}
                        res.info("손절가가 되어 " + str(contract_num) + "개 청산 요청.")
                        return {'신규주문': True, '매도수구분': '신규매수', '수량': contract_num}
                    else:
                        #1차 청산 이후 청산 일 때
                        res.info("손절가가 되어 " + str(contract.list[subject_code]['계약타입'][contract.SAFE] +
                                                  contract.list[subject_code]['계약타입'][
                                                      contract.DRIBBLE]) + "개 청산 요청.")
                        return {'신규주문': True, '매도수구분': '신규매수',
                                '수량': contract.list[subject_code]['계약타입'][contract.SAFE] +
                                      contract.list[subject_code]['계약타입'][contract.DRIBBLE]}

                elif calc.data[subject_code]['플로우'][-1] == '하향' and subject.info[subject_code]['sar'] < current_price:
                    if subject.info[subject_code]['반대매매'] == False:
                        res.info("상향 반전되어 " + str(
                            contract.list[subject_code]['계약타입'][contract.SAFE] + contract.list[subject_code]['계약타입'][
                                contract.DRIBBLE]) + "개 청산 요청.")
                        return {'신규주문': True, '매도수구분': '신규매수',
                                '수량': contract.list[subject_code]['계약타입'][contract.SAFE] +
                                      contract.list[subject_code]['계약타입'][contract.DRIBBLE]}
                elif calc.data[subject_code]['플로우'][-1] == '상향' and subject.info[subject_code]['sar'] > current_price:
                    if subject.info[subject_code]['반대매매'] == True:
                        res.info("하향 반전되어 " + str(
                            contract.list[subject_code]['계약타입'][contract.SAFE] + contract.list[subject_code]['계약타입'][
                                contract.DRIBBLE]) + "개 청산 요청.")
                        return {'신규주문': True, '매도수구분': '신규매수',
                                '수량': contract.list[subject_code]['계약타입'][contract.SAFE] +
                                      contract.list[subject_code]['계약타입'][contract.DRIBBLE]}
                elif current_price < contract.list[subject_code]['익절가']:
                    contract.list[subject_code]['익절가'] = current_price - subject.info[subject_code]['익절틱'] * \
                                                                         subject.info[subject_code]['단위']
                    contract.list[subject_code]['손절가'] = current_price + subject.info[subject_code]['익절틱'] * \
                                                                         subject.info[subject_code]['단위']
                    log.debug("종목코드(" + subject_code + ") 익절가 갱신.")
                elif (float(contract.list[subject_code]['체결가']) - current_price) >= first_chungsan * \
                        subject.info[subject_code]['단위'] and contract.get_contract_count(subject_code) == \
                        subject.info[subject_code]['신규매매수량']:  # int(contract.get_contract_count(subject_code) / 2) > 0:
                    if contract.list[subject_code]['손절가'] > current_price + first_chungsan_dribble * \
                            subject.info[subject_code]['단위']:
                        contract.list[subject_code]['손절가'] = current_price + first_chungsan_dribble * \
                                                                             subject.info[subject_code]['단위']
                        res.info("1차 청산 드리블 중 %s" % contract.list[subject_code]['손절가'])
                elif (float(contract.list[subject_code]['체결가']) - current_price) >= second_chungsan * \
                        subject.info[subject_code]['단위'] and contract.get_contract_count(subject_code) == int(
                                subject.info[subject_code]['신규매매수량'] - int(subject.info[subject_code]['신규매매수량'] / 2)):
                    if contract.list[subject_code]['손절가'] > current_price + second_chungsan_dribble * \
                            subject.info[subject_code]['단위']:
                        contract.list[subject_code]['손절가'] = current_price + second_chungsan_dribble * \
                                                                             subject.info[subject_code]['단위']
                        res.info("2차 청산 드리블 중 %s" % contract.list[subject_code]['손절가'])
                        # return {'신규주문':True, '매도수구분':'신규매수', '수량':int((contract.list[subject_code]['계약타입'][contract.SAFE] + contract.list[subject_code]['계약타입'][contract.DRIBBLE]+1)/2)}

    except Exception as err:
        log.error(err)

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
