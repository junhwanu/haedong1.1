# -*- coding: utf-8 -*-
import contract, subject, log, calc, time
import log_result as res

def is_it_OK(subject_code, current_price):
    profit_tick = 0
    loss_tick = 0
    mesu_medo_type = ''
    contract_cnt = 2
    
    return {'신규주문':False}
    # 매매중 또는 매매시도중, 청산시도중 일 때 구매 불가
    if subject.info[subject_code]['상태'] != '중립대기' and subject.info[subject_code]['상태'] != '매매선터치':
        return {'신규주문':False}

    # 마감시간 임박 구매 불가
    if get_time(30) >= int(subject.info[subject_code]['마감시간']) and get_time(0) < int(subject.info[subject_code]['마감시간']):
        log.debug('마감시간 임박으로 구매 불가')
        return {'신규주문':False}

    # 최소연속틱 미달로 구매 불가
    if calc.get_line_range(subject_code) < subject.info[subject_code]['최소연속틱']:
        log.debug('최소연속틱 미달로 구매 불가. 현재 연속틱 : ' + str(calc.get_line_range(subject_code)))
        return {'신규주문':False}

    # 상한선 또는 하한선 터치 시 고, 저점 찾기
    if calc.data[subject_code]['추세'][-1] == '하락세' and calc.data[subject_code]['고가'][-1] >= calc.data[subject_code]['볼린저밴드']['상한선'][-1] and calc.data[subject_code]['고저점검색완료'] == False:
        calc.find_high_low_point(subject_code)
        calc.data[subject_code]['고저점검색완료'] = True
    elif calc.data[subject_code]['추세'][-1] == '상승세' and calc.data[subject_code]['저가'][-1] <= calc.data[subject_code]['볼린저밴드']['하한선'][-1]:
        calc.find_high_low_point(subject_code)
        calc.data[subject_code]['고저점검색완료'] = True

    if calc.data[subject_code]['추세'][-1] == '하락세' and current_price <= calc.data[subject_code]['볼린저밴드']['중심선'][-1]:
        calc.data[subject_code]['고저점검색완료'] = False
    elif calc.data[subject_code]['추세'][-1] == '상승세' and current_price >= calc.data[subject_code]['볼린저밴드']['중심선'][-1]:
        calc.data[subject_code]['고저점검색완료'] = False

    # 상승세 일 때,
    if calc.data[subject_code]['추세'][-1] == '상승세':
        '''
        if current_price < calc.data[subject_code]['이동평균선'][120][-1]:
            return {'신규주문':False}
        '''

        # 하한선 터치 시 매매선터치로 상태 변경
        if current_price <= calc.data[subject_code]['볼린저밴드']['하한선'][-1]:
            if subject.info[subject_code]['상태'] != '매매선터치':
                log.debug('종목[' + subject_code + '] 상태 변경, ' + subject.info[subject_code]['상태'] + ' -> 매매선터치.')
                subject.info[subject_code]['상태'] = '매매선터치'
            return {'신규주문':False}

        # 현재가와 중심선의 차이가 5틱 이하일 땐 구매 불가
        if calc.data[subject_code]['볼린저밴드']['중심선'][-1] - current_price <= 0 * subject.info[subject_code]['단위']:
            if subject.info[subject_code]['상태'] != '중립대기':
                log.debug('종목[' + subject_code + '] 상태 변경, ' + subject.info[subject_code]['상태'] + ' -> 중립대기.')
                subject.info[subject_code]['상태'] = '중립대기'
            return {'신규주문':False}

        # 매매선터치일 때, 8틱 이상 이탈하면 중립대기로 변경
        if subject.info[subject_code]['상태'] == '매매선터치' and current_price - calc.data[subject_code]['볼린저밴드']['하한선'][-1] > 7 * subject.info[subject_code]['단위']:
            
            return {'신규주문':False}

        # 저점 고점이 없으면 구매 불가
        if len(calc.data[subject_code]['저가그룹']) < 2 or len(calc.data[subject_code]['고가그룹']) < 1:
            log.debug('종목[' + subject_code + '] 고점, 저점을 찾을 수 없으므로 구매 불가.')
            return {'신규주문':False}
        
        # 현재 저점이 이전 저점보다 낮으면 구매 불가
        if calc.data[subject_code]['저가그룹'][-1][1] <= calc.data[subject_code]['저가그룹'][-2][1]:
            log.debug('종목[' + subject_code + '] 현재 저점이 이전 저점보다 낮으므로 구매 불가.')
            return {'신규주문':False}
        
        # 직전 저점과 고점의 차가 20틱 이하일 경우 구매 불가
        if calc.data[subject_code]['고가그룹'][-1][1] - calc.data[subject_code]['저가그룹'][-1][1] <= 15 * subject.info[subject_code]['단위']:
            log.debug('종목[' + subject_code + '] 직전 저점과 직전 고점의 차가 20틱 이하이므로 구매 불가.')
            return {'신규주문':False}
        
        # 직전 고점이 상한선을 터치 안하면 구매 불가
        if calc.data[subject_code]['고가그룹'][-1][2] == False:
            log.debug('종목[' + subject_code + '] 직전 고점이 상한선을 터치하지 않아 구매 불가.')
            return {'신규주문':False}
        '''
        # 파라 매도세면 안사
        if subject.info[subject_code]['flow'] == '상향' or (subject.info[subject_code]['flow'] == '하향' and current_price >= subject.info[subject_code]['sar']):
            pass
        else:
            log.debug('종목[' + subject_code + '] 파라 하향세로 구매 불가.')
            return {'신규주문':False}
        '''

        # 익절가 10틱안넘으면 안먹어 개새기들아
        profit_tick = abs(calc.data[subject_code]['볼린저밴드']['중심선'][-1] - calc.data[subject_code]['볼린저밴드']['하한선'][-1]) / subject.info[subject_code]['단위']
        if profit_tick > 15: profit_tick = 15
        if profit_tick < 10:
            log.debug('종목[' + subject_code + '] 익절틱이 10틱 보다 작아 구매 불가.')
            return {'신규주문':False}

        # 손절가 = 15틱
        loss_tick = 15

        # 신규매수
        mesu_medo_type = '신규매수'

    # 하락세 일 때,
    if calc.data[subject_code]['추세'][-1] == '하락세':
        '''
        if current_price > calc.data[subject_code]['이동평균선'][120][-1]:
            return {'신규주문':False}
        '''

        # 상한선 터치 시 매매선터치로 상태 변경
        if current_price >= calc.data[subject_code]['볼린저밴드']['상한선'][-1]:
            if subject.info[subject_code]['상태'] != '매매선터치':
                log.debug('종목[' + subject_code + '] 상태 변경, ' + subject.info[subject_code]['상태'] + ' -> 매매선터치.')
                subject.info[subject_code]['상태'] = '매매선터치'
            return {'신규주문':False}

        # 현재가와 중심선의 차이가 5틱 이하일 땐 구매 불가
        if current_price - calc.data[subject_code]['볼린저밴드']['중심선'][-1] <= 0 * subject.info[subject_code]['단위']:
            log.debug('종목[' + subject_code + '] current_price - calc.data[subject_code][\'볼린저밴드\'][\'중심선\'][-1] = ' + str(current_price - calc.data[subject_code]['볼린저밴드']['중심선'][-1]))
            if subject.info[subject_code]['상태'] != '중립대기':
                log.debug('종목[' + subject_code + '] 상태 변경, ' + subject.info[subject_code]['상태'] + ' -> 중립대기.')
                subject.info[subject_code]['상태'] = '중립대기'
            return {'신규주문':False}

        
        if subject.info[subject_code]['상태'] == '매매선터치' and calc.data[subject_code]['볼린저밴드']['상한선'][-1] - current_price > 7 * subject.info[subject_code]['단위']:
            return {'신규주문':False}

        log.debug('종목[' + subject_code + '] 고점 : ' + str(calc.data[subject_code]['고가그룹']) + ' / 저점 : ' + str(calc.data[subject_code]['저가그룹']))
        if len(calc.data[subject_code]['저가그룹']) < 2 or len(calc.data[subject_code]['고가그룹']) < 1:
            log.debug('종목[' + subject_code + '] 고점, 저점을 찾을 수 없으므로 구매 불가.')
            return {'신규주문':False}
        
        # 현재 고점이 이전 고점보다 높으면 구매 불가
        if calc.data[subject_code]['고가그룹'][-1][1] >= calc.data[subject_code]['고가그룹'][-2][1]:
            log.debug('종목[' + subject_code + '] 현재 고점이 이전 고점보다 높으므로 구매 불가.')
            return {'신규주문':False}
        
        # 직전 저점과 고점의 차가 20틱 이하일 경우 구매 불가
        if calc.data[subject_code]['고가그룹'][-1][1] - calc.data[subject_code]['저가그룹'][-1][1] <= 15 * subject.info[subject_code]['단위']:
            log.debug('종목[' + subject_code + '] 직전 저점과 직전 고점의 차가 20틱 이하이므로 구매 불가.')
            return {'신규주문':False}
        
        # 직전 저점이 하한선을 터치 안하면 구매 불가
        if calc.data[subject_code]['저가그룹'][-1][2] == False:
            log.debug('종목[' + subject_code + '] 직전 저점이 하한선을 터치하지 않아 구매 불가.')
            return {'신규주문':False}
        '''
        # 파라 매수세면 안사
        if subject.info[subject_code]['flow'] == '하향' or (subject.info[subject_code]['flow'] == '상향' and current_price < subject.info[subject_code]['sar']):
            pass
        else:
            log.debug('종목[' + subject_code + '] 파라 상향세로 구매 불가.')
            return {'신규주문':False}
        '''
        # 익절가 10틱안넘으면 안먹어 개새기들아
        profit_tick = abs(calc.data[subject_code]['볼린저밴드']['중심선'][-1] - calc.data[subject_code]['볼린저밴드']['상한선'][-1]) / subject.info[subject_code]['단위']
        if profit_tick > 15: profit_tick = 15
        if profit_tick < 10:
            log.debug('종목[' + subject_code + '] 익절틱이 10틱 보다 작아 구매 불가.')
            return {'신규주문':False}

        # 손절가 = 15틱
        loss_tick = 15

        # 신규매수
        mesu_medo_type = '신규매도'

    if subject.info[subject_code]['상태'] != '매매선터치': 
        return {'신규주문':False}

    profit_tick = round(profit_tick, 0)
    order_contents = {'신규주문':True, '매도수구분':mesu_medo_type, '익절틱':profit_tick, '손절틱':loss_tick, '수량':contract_cnt}
    return order_contents

def is_it_sell(subject_code, current_price):
    if contract.get_contract_count(subject_code) > 0:
        # 계약 보유중
        if contract.list[subject_code]['매도수구분'] == '신규매수':
            # 매수일때
            if current_price >= contract.list[subject_code]['익절가']: 
                if contract.list[subject_code]['계약타입'][contract.DRIBBLE] > 0:
                    # 드리블 수량이 남아있다면
                    if get_time(30) >= int(subject.info[subject_code]['마감시간']) and get_time(0) < int(subject.info[subject_code]['마감시간']):
                        log.info('마감시간 임박으로 드리블 불가. 모두 청산.')
                        return {'신규주문':True, '매도수구분':'신규매도', '수량':contract.list[subject_code]['계약타입'][contract.SAFE] + contract.list[subject_code]['계약타입'][contract.DRIBBLE]}
                    else:
                        log.info("드리블 목표 달성으로 익절가 수정.")
                        contract.list[subject_code]['익절가'] = current_price + ( subject.info[subject_code]['단위'] )
                        contract.list[subject_code]['손절가'] = current_price - ( (subject.info[subject_code]['주문내용']['손절틱'] - 5) * subject.info[subject_code]['단위'] )

                # 목표달성 청산
                if contract.list[subject_code]['계약타입'][contract.SAFE] > 0:
                    log.info("목표달성 청산으로 드리블 수량 제외하고 " + str(contract.list[subject_code]['계약타입'][contract.SAFE]) + "개 청산 요청.")
                    return {'신규주문':True, '매도수구분':'신규매도', '수량':contract.list[subject_code]['계약타입'][contract.SAFE]}
                
            elif current_price <= contract.list[subject_code]['손절가']: 
                # 손절 청산
                log.info("손절가가 되어 " + str(contract.list[subject_code]['계약타입'][contract.SAFE] + contract.list[subject_code]['계약타입'][contract.DRIBBLE]) + "개 청산 요청.")
                return {'신규주문':True, '매도수구분':'신규매도', '수량':contract.list[subject_code]['계약타입'][contract.SAFE] + contract.list[subject_code]['계약타입'][contract.DRIBBLE]}
        
        elif contract.list[subject_code]['매도수구분'] == '신규매도':
            # 매도일때
            if current_price <= contract.list[subject_code]['익절가']: 
                if contract.list[subject_code]['계약타입'][contract.DRIBBLE] > 0:
                    # 드리블 수량이 남아있다면
                    if get_time(30) >= int(subject.info[subject_code]['마감시간']) and get_time(0) < int(subject.info[subject_code]['마감시간']):
                        log.info('마감시간 임박으로 드리블 불가. 모두 청산.')
                        return {'신규주문':True, '매도수구분':'신규매수', '수량':contract.list[subject_code]['계약타입'][contract.SAFE] + contract.list[subject_code]['계약타입'][contract.DRIBBLE]}
                    else:
                        log.info("드리블 목표 달성으로 익절가 수정.")
                        contract.list[subject_code]['익절가'] = current_price - ( subject.info[subject_code]['단위'] )
                        contract.list[subject_code]['손절가'] = current_price + ( (subject.info[subject_code]['주문내용']['손절틱'] - 5) * subject.info[subject_code]['단위'] )
                    
                # 목표달성 청산
                if contract.list[subject_code]['계약타입'][contract.SAFE] > 0:
                    log.info("목표달성 청산으로 드리블 수량 제외하고 " + str(contract.list[subject_code]['계약타입'][contract.SAFE]) + "개 청산 요청.")
                    return {'신규주문':True, '매도수구분':'신규매수', '수량':contract.list[subject_code]['계약타입'][contract.SAFE]}
                
            elif current_price >= contract.list[subject_code]['손절가']: 
                # 손절청산
                log.info("손절가가 되어 " + str(contract.list[subject_code]['계약타입'][contract.SAFE] + contract.list[subject_code]['계약타입'][contract.DRIBBLE]) + "개 청산 요청.")
                return {'신규주문':True, '매도수구분':'신규매수', '수량':contract.list[subject_code]['계약타입'][contract.SAFE] + contract.list[subject_code]['계약타입'][contract.DRIBBLE]}

    return {'신규주문':False}

def find_current_lowest_value(subject_code):
    min_value = 99999
    min_idx = 0
    for idx in range(calc.data[subject_code]['idx'],0,-1):
        if calc.data[subject_code]['볼린저밴드']['캔들위치'] != '하단':
            break
        if min_value > calc.data[subject_code]['저가'][idx]:
            min_value = calc.data[subject_code]['저가'][idx]
            min_idx = idx
    return min_value

def find_current_highest_value(subject_code):
    max_value = -99999
    max_idx = 0
    for idx in range(calc.data[subject_code]['idx'],0,-1):
        if calc.data[subject_code]['볼린저밴드']['캔들위치'] != '상단':
            break
        if max_value < calc.data[subject_code]['저가'][idx]:
            max_value = calc.data[subject_code]['저가'][idx]
            max_idx = idx
    return max_value

def get_time(add_min):
    # 현재 시간 정수형으로 return
    current_hour = time.localtime().tm_hour
    current_min = time.localtime().tm_min
    if current_min + add_min >= 60:
        current_hour += 1
        current_min -= 60

    current_time = current_hour*100 + current_min

    return current_time