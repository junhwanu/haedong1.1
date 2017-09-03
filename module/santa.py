# -*- coding: utf-8 -*-
import contract, subject, log, calc, time

def is_it_OK(subject_code, current_price):
    '''
    이거 살까?
    '''
    
    # 마감시간 임박 구매 불가
    if get_time(30) >= int(subject.info[subject_code]['마감시간']) and get_time(0) < int(subject.info[subject_code]['마감시간']):
        log.debug('마감시간 임박으로 구매 불가')
        return {'신규주문':False}
   
    # 이평선 정렬확인
    #if calc.data[subject_code]['정배열연속틱'] < subject.info[subject_code]['최소연속틱']:
    if calc.get_line_range(subject_code) < subject.info[subject_code]['최소연속틱']:
        return {'신규주문':False}
    #log.debug('정배열연속틱 : ' + str(calc.data[subject_code]['정배열연속틱']) + ' >= 최소연속틱 : ' + str(subject.info[subject_code]['최소연속틱']) + ' 구매조건 통과.')
    log.debug('추세시작부터 연속틱 : ' + str(calc.get_line_range(subject_code)) + ' >= 최소연속틱 : ' + str(subject.info[subject_code]['최소연속틱']) + ' 구매조건 통과.')

    # 일목균형표 확인
    if calc.data[subject_code]['추세'][ calc.data[subject_code]['idx'] ] == '상승세':
        if calc.data[subject_code]['일목균형표']['선행스팬1'][ calc.data[subject_code]['idx'] ] > current_price and calc.data[subject_code]['일목균형표']['선행스팬2'][ calc.data[subject_code]['idx'] ] > current_price:
            return {'신규주문':False}
        log.debug('현재가가 일목균형표 구름대보다 위에 있는 구매조건 통과.')    
    elif calc.data[subject_code]['추세'][ calc.data[subject_code]['idx'] ] == '하락세':
        if calc.data[subject_code]['일목균형표']['선행스팬1'][ calc.data[subject_code]['idx'] ] < current_price and calc.data[subject_code]['일목균형표']['선행스팬2'][ calc.data[subject_code]['idx'] ] < current_price:
            return {'신규주문':False}
        log.debug('현재가가 일목균형표 구름대보다 아래에 있는 구매조건 통과.')

    
    # 추세선 터치여부 확인
    
    '''
    if subject.info[subject_code]['상태'] == '매매구간진입':
        log.debug('현재가가 매매구간진입 상태로 구매조건 통과.')
    '''
    if subject.info[subject_code]['상태'] == '매매구간진입' and subject.info[subject_code]['매매구간누적캔들'] >= 1:
        log.debug('현재가가 매매구간진입 상태이며, 매매구간누적캔들 ' + str(subject.info[subject_code]['매매구간누적캔들']) + '개로 구매조건 통과.')
    else: 
        log.debug('현재상태 : ' + subject.info[subject_code]['상태'] + ', 매매구간누적캔들 : ' + str(subject.info[subject_code]['매매구간누적캔들']) + '로 구매조건 미달.')
        return {'신규주문':False}

    # 매매선과 5틱 이내일때만 구매
    min_tick = 2
    if abs(current_price - calc.data[subject_code]['매매선'][-1]) > min_tick * subject.info[subject_code]['단위']:
        log.debug('현재가 : ' + str(current_price) + ', 매매선가 : ' + str(calc.data[subject_code]['매매선'][-1]) + ' ' + str(min_tick) + '틱 이상 차이로 구매 안함.')
        return {'신규주문':False}
    log.debug('매매선과 현재가가 '  + str(min_tick) + '틱 이내로 구매조건 통과.')

    # 추세선 기울기가 너무 작은지 확인
    if calc.data[subject_code]['추세'][ calc.data[subject_code]['idx'] ] == '상승세':
        if calc.data[subject_code]['추세선기울기'] < 0.002:
            log.debug('추세선 기울기가 ' + str(calc.data[subject_code]['추세선기울기']) + '로 너무 작아 매매 불가.')
            return {'신규주문':False}
        else:
            log.debug('추세선 기울기 : ' + str(calc.data[subject_code]['추세선기울기']) + '로 구매조건 통과.')
    elif calc.data[subject_code]['추세'][ calc.data[subject_code]['idx'] ] == '하락세':
        if calc.data[subject_code]['추세선기울기'] > -0.002:
            log.debug('추세선 기울기가 ' + str(calc.data[subject_code]['추세선기울기']) + '로 너무 작아 매매 불가.')
            return {'신규주문':False}
        else:
            log.debug('추세선 기울기 : ' + str(calc.data[subject_code]['추세선기울기']) + '로 구매조건 통과.')

    # 모든 조건 충족 시 현재 보유 계약 상태 확인해서 리턴
    
    # 초기에 계좌 잔고 저장해서, 몇개 살 수 있는지 확인해서 리턴
    contract_cnt = 2

    # 매도수구분 설정
    mesu_medo_type = None
    if calc.data[subject_code]['추세'][ calc.data[subject_code]['idx'] ] == '상승세':
        mesu_medo_type = '신규매수'
    elif calc.data[subject_code]['추세'][ calc.data[subject_code]['idx'] ] == '하락세':
        mesu_medo_type = '신규매도'

    profit_tick = int(abs(calc.data[subject_code]['추세선기울기'] * 5000))
    if profit_tick > 10: profit_tick = 10

    order_contents = {'신규주문':True, '매도수구분':mesu_medo_type, '익절틱':profit_tick, '손절틱':profit_tick, '수량':contract_cnt}
    log.debug('santa.is_it_OK() : 모든 구매조건 통과.')
    log.debug(order_contents)
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
                        contract.list[subject_code]['익절가'] = current_price + ( subject.info[subject_code]['주문내용']['익절틱'] * subject.info[subject_code]['단위'] )
                        contract.list[subject_code]['손절가'] = current_price - ( (subject.info[subject_code]['주문내용']['손절틱'] - 1) * subject.info[subject_code]['단위'] ) # 수수료 때문에 1틱 뺌

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
                        contract.list[subject_code]['익절가'] = current_price - ( subject.info[subject_code]['주문내용']['익절틱'] * subject.info[subject_code]['단위'] )
                        contract.list[subject_code]['손절가'] = current_price + ( (subject.info[subject_code]['주문내용']['손절틱'] - 1) * subject.info[subject_code]['단위'] ) # 수수료 때문에 1틱 뺌
                    
                # 목표달성 청산
                if contract.list[subject_code]['계약타입'][contract.SAFE] > 0:
                    log.info("목표달성 청산으로 드리블 수량 제외하고 " + str(contract.list[subject_code]['계약타입'][contract.SAFE]) + "개 청산 요청.")
                    return {'신규주문':True, '매도수구분':'신규매수', '수량':contract.list[subject_code]['계약타입'][contract.SAFE]}
                
            elif current_price >= contract.list[subject_code]['손절가']: 
                # 손절청산
                log.info("손절가가 되어 " + str(contract.list[subject_code]['계약타입'][contract.SAFE] + contract.list[subject_code]['계약타입'][contract.DRIBBLE]) + "개 청산 요청.")
                return {'신규주문':True, '매도수구분':'신규매수', '수량':contract.list[subject_code]['계약타입'][contract.SAFE] + contract.list[subject_code]['계약타입'][contract.DRIBBLE]}

    return {'신규주문':False}

def update_state_by_current_price(subject_code, current_price):
    if subject.info[subject_code]['상태'] == '중립대기':
        if calc.get_line_range(subject_code) >= subject.info[subject_code]['최소연속틱']:
            if calc.data[subject_code]['추세'][ calc.data[subject_code]['idx'] ] == '상승세':
                if calc.data[subject_code]['매매선'][ calc.data[subject_code]['idx'] ] >= current_price:
                    subject.info[subject_code]['상태'] = '매매선터치'
                    log.info('상태변경 : 중립대기 -> 매매선터치')
            elif calc.data[subject_code]['추세'][ calc.data[subject_code]['idx'] ] == '하락세':
                if calc.data[subject_code]['매매선'][ calc.data[subject_code]['idx'] ] <= current_price:
                    subject.info[subject_code]['상태'] = '매매선터치'
                    log.info('상태변경 : 중립대기 -> 매매선터치')
    elif subject.info[subject_code]['상태'] == '매매선터치' or subject.info[subject_code]['상태'] == '매매구간진입':
        if calc.data[subject_code]['추세'][ calc.data[subject_code]['idx'] ] == '상승세':
            if current_price - calc.data[subject_code]['매매선'][-1] > 2:
                log.info('상태변경 : ' + subject.info[subject_code]['상태'] + ' -> 중립대기')
                subject.info[subject_code]['상태'] = '중립대기'
        elif calc.data[subject_code]['추세'][ calc.data[subject_code]['idx'] ] == '하락세':
            if calc.data[subject_code]['매매선'][-1] - current_price  > 2:
                log.info('상태변경 : ' + subject.info[subject_code]['상태'] + ' -> 중립대기')
                subject.info[subject_code]['상태'] = '중립대기'

def update_state_by_current_candle(subject_code, price):
    current_price = float(price['현재가'])
    start_price = float(price['시가'])
    '''
    if subject.info[subject_code]['상태'] == '매매선터치' or subject.info[subject_code]['상태'] == '매매구간진입' :
        if calc.data[subject_code]['추세'][ calc.data[subject_code]['idx'] ] == '상승세':
            if current_price >= calc.data[subject_code]['매매선'][ calc.data[subject_code]['idx'] ]:
                log.debug('상태변경 : ' + subject.info[subject_code]['상태'] + ' -> 매매구간진입')
                subject.info[subject_code]['상태'] = '매매구간진입'
                subject.info[subject_code]['매매구간누적캔들'] += 1
                log.debug('매매구간 누적캔들 : ' + str(subject.info[subject_code]['매매구간누적캔들']))
            else:
                log.debug('상태변경 : ' + subject.info[subject_code]['상태'] + ' -> 매매선터치')
                subject.info[subject_code]['상태'] = '매매선터치'
                subject.info[subject_code]['매매구간누적캔들'] = 0
        elif calc.data[subject_code]['추세'][ calc.data[subject_code]['idx'] ] == '하락세':
            if current_price <= calc.data[subject_code]['매매선'][ calc.data[subject_code]['idx'] ]:
                log.debug('상태변경 : ' + subject.info[subject_code]['상태'] + ' -> 매매구간진입')
                subject.info[subject_code]['상태'] = '매매구간진입'
                subject.info[subject_code]['매매구간누적캔들'] += 1
                log.debug('매매구간 누적캔들 : ' + str(subject.info[subject_code]['매매구간누적캔들']))
            else:
                log.debug('상태변경 : ' + subject.info[subject_code]['상태'] + ' -> 매매선터치')
                subject.info[subject_code]['상태'] = '매매선터치'
                subject.info[subject_code]['매매구간누적캔들'] = 0
    '''
    if subject.info[subject_code]['상태'] == '매매선터치' or subject.info[subject_code]['상태'] == '매매구간진입' :
        if calc.data[subject_code]['추세'][ calc.data[subject_code]['idx'] ] == '상승세':
            if current_price >= calc.data[subject_code]['매매선'][ calc.data[subject_code]['idx'] ]:
                if start_price < calc.data[subject_code]['매매선'][ calc.data[subject_code]['idx'] ]:
                    log.debug('상태변경 : ' + subject.info[subject_code]['상태'] + ' -> 매매선터치')
                    subject.info[subject_code]['상태'] = '매매선터치'
                    subject.info[subject_code]['매매구간누적캔들'] = 0
                else:
                    log.debug('상태변경 : ' + subject.info[subject_code]['상태'] + ' -> 매매구간진입')
                    subject.info[subject_code]['상태'] = '매매구간진입'
                    subject.info[subject_code]['매매구간누적캔들'] += 1
                    log.debug('매매구간 누적캔들 : ' + str(subject.info[subject_code]['매매구간누적캔들']))
        elif calc.data[subject_code]['추세'][ calc.data[subject_code]['idx'] ] == '하락세':
            if current_price <= calc.data[subject_code]['매매선'][ calc.data[subject_code]['idx'] ]:
                if start_price > calc.data[subject_code]['매매선'][ calc.data[subject_code]['idx'] ]:
                    log.debug('상태변경 : ' + subject.info[subject_code]['상태'] + ' -> 매매선터치')
                    subject.info[subject_code]['상태'] = '매매선터치'
                    subject.info[subject_code]['매매구간누적캔들'] = 0
                else:
                    log.debug('상태변경 : ' + subject.info[subject_code]['상태'] + ' -> 매매구간진입')
                    subject.info[subject_code]['상태'] = '매매구간진입'
                    subject.info[subject_code]['매매구간누적캔들'] += 1
                    log.debug('매매구간 누적캔들 : ' + str(subject.info[subject_code]['매매구간누적캔들']))
    

def get_time(add_min):
    # 현재 시간 정수형으로 return
    current_hour = time.localtime().tm_hour
    current_min = time.localtime().tm_min
    if current_min + add_min >= 60:
        current_hour += 1
        current_min -= 60

    current_time = current_hour*100 + current_min

    return current_time