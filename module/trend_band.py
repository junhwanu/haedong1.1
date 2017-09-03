# -*- coding: utf-8 -*-
import contract, subject, log, calc, time
import log_result as res

def is_it_OK(subject_code, current_price, adjusted_price, highest_price, lowest_price):
    profit_tick = 10
    loss_tick = 10
    mesu_medo_type = ''
    contract_cnt = 2
    index = calc.data[subject_code]['idx']

    # 마감시간 임박 구매 불가
    if get_time(30) >= int(subject.info[subject_code]['마감시간']) and get_time(0) < int(subject.info[subject_code]['마감시간']):
        log.debug('마감시간 임박으로 구매 불가')
        return {'신규주문':False}

    # 최소연속틱 미달로 구매 불가
    if calc.data[subject_code]['추세연속틱'] < subject.info[subject_code]['최소연속틱'] or calc.data[subject_code]['정배열연속틱'] < subject.info[subject_code]['최소연속틱']/2:
        log.debug('최소연속틱 미달로 구매 불가. 현재 연속틱 : ' + str(calc.data[subject_code]['추세연속틱']))
        return {'신규주문':False}

    if subject.info[subject_code]['상태'] == '중립대기':
        if calc.data[subject_code]['추세'][-1] == '상승세':
            if current_price <= calc.data[subject_code]['추세선밴드']['하한선'][index] and adjusted_price <= calc.data[subject_code]['추세선밴드']['하한선'][index]:
                log.info('종목코드(' + subject_code + ') 상태 변경, ' + subject.info[subject_code]['상태'] + ' -> 매매선터치.')
                subject.info[subject_code]['상태'] = '매매선터치'
                calc.data[subject_code]['극점가'] = adjusted_price
        else:
            if current_price >= calc.data[subject_code]['추세선밴드']['상한선'][index] and adjusted_price >= calc.data[subject_code]['추세선밴드']['상한선'][index]:
                log.info('종목코드(' + subject_code + ') 상태 변경, ' + subject.info[subject_code]['상태'] + ' -> 매매선터치.')
                subject.info[subject_code]['상태'] = '매매선터치'
                calc.data[subject_code]['극점가'] = adjusted_price
        return {'신규주문':False}

    if calc.data[subject_code]['추세'][-1] == '모름':
        return {'신규주문':False}

    elif subject.info[subject_code]['상태'] == '매매선터치':
        # 추세선과 매매선 폭이 너무 좁으면 매매 불가
        if calc.data[subject_code]['추세선밴드']['상한선'][-1] - calc.data[subject_code]['추세선밴드']['하한선'][-1] <= 20 * subject.info[subject_code]['단위']:
            log.debug('추세선밴드 폭이 ' + str(calc.data[subject_code]['추세선밴드']['상한선'][-1] - calc.data[subject_code]['추세선밴드']['하한선'][-1]) + '이므로 매매 불가.')
            return {'신규주문':False}
        
        if calc.data[subject_code]['추세'][-1] == '상승세':
            
            if calc.data[subject_code]['이동평균선'][240][-1] == None or calc.data[subject_code]['이동평균선'][240][-1] >= calc.data[subject_code]['이동평균선'][ subject.info[subject_code]['이동평균선'][-1] ][-1]:
                log.debug('이동평균선이 240선과 정배열되어있지 않으므로 매매 불가.')
                return {'신규주문':False}
            
            if calc.data[subject_code]['추세선기울기'] <= 0.2 * subject.info[subject_code]['단위'] or calc.data[subject_code]['추세선기울기'] >= 0.5 * subject.info[subject_code]['단위']:
                log.debug('추세선기울기 : ' + str(calc.data[subject_code]['추세선기울기']) + '로 매매 불가.')
                return {'신규주문':False}
            
            if adjusted_price <= calc.data[subject_code]['극점가']:
                calc.data[subject_code]['극점가'] = adjusted_price
            
            if abs(adjusted_price - calc.data[subject_code]['극점가']) > 25 * subject.info[subject_code]['단위']:
                subject.info[subject_code]['상태'] = '중립대기'
                return {'신규주문':False}
            
            if adjusted_price >= calc.data[subject_code]['추세선밴드']['하한선'][index] + 4 * subject.info[subject_code]['단위']:
                #if current_price <= calc.data[subject_code]['추세선밴드']['하한선'][index] + 4 * subject.info[subject_code]['단위']:
                if current_price < adjusted_price:
                    if abs(calc.data[subject_code]['극점가'] - current_price) <= 15 * subject.info[subject_code]['단위']:
                        # 볼린저밴드랑 상단에 위치해야함
                        if lowest_price - 4 * subject.info[subject_code]['단위'] >= calc.data[subject_code]['볼린저밴드']['하한선'][index] and lowest_price - 4 * subject.info[subject_code]['단위'] >= calc.data[subject_code]['추세선밴드']['하한선'][index]:
                            # 신규매수타이밍
                            mesu_medo_type = '신규매수'
                        else:
                            log.debug('현재 캔들이 볼린저밴드를 하한선을 터치하여 매매 안함.')
                            return {'신규주문':False}
                    else:
                        log.debug('극점가와 현재가의 가격차이가 크므로, 매매 안함.')
                        return {'신규주문':False}
                else:
                    log.debug('현재가가 하한선 상단에 위치하여 매매 안함.')
                    return {'신규주문':False}
            else:
                log.debug('보정가가 하한선 하단에 위치하여 매매 안함.')
                return {'신규주문':False}
        else:
            
            if calc.data[subject_code]['이동평균선'][240][-1] == None or calc.data[subject_code]['이동평균선'][240][-1] <= calc.data[subject_code]['이동평균선'][ subject.info[subject_code]['이동평균선'][-1] ][-1]:
                log.debug('이동평균선이 240선과 정배열되어있지 않으므로 매매 불가.')
                return {'신규주문':False}
            
            if calc.data[subject_code]['추세선기울기'] >= -0.2 * subject.info[subject_code]['단위'] or calc.data[subject_code]['추세선기울기'] <= -0.5 * subject.info[subject_code]['단위']:
                log.debug('추세선기울기 : ' + str(calc.data[subject_code]['추세선기울기']) + '로 매매 불가.')
                return {'신규주문':False}
            

            if adjusted_price >= calc.data[subject_code]['극점가']:
                calc.data[subject_code]['극점가'] = adjusted_price
            
            if abs(adjusted_price - calc.data[subject_code]['극점가']) > 25 * subject.info[subject_code]['단위']:
                subject.info[subject_code]['상태'] = '중립대기'
                return {'신규주문':False}
            
            if adjusted_price <= calc.data[subject_code]['추세선밴드']['상한선'][index] - 4 * subject.info[subject_code]['단위']:
                #if current_price >= calc.data[subject_code]['추세선밴드']['상한선'][index] - 4 * subject.info[subject_code]['단위']:
                if current_price > adjusted_price:
                    if abs(calc.data[subject_code]['극점가'] - current_price) <= 15 * subject.info[subject_code]['단위']:
                        # 볼린저밴드랑 하단에 위치해야함
                        if highest_price + 4 * subject.info[subject_code]['단위'] <= calc.data[subject_code]['볼린저밴드']['상한선'][index] and highest_price + 4 * subject.info[subject_code]['단위'] <= calc.data[subject_code]['추세선밴드']['상한선'][index]:
                            # 신규매수타이밍
                            mesu_medo_type = '신규매도'
                        else:
                            log.debug('현재 캔들이 볼린저밴드를 상한선을 터치하여 매매 안함.')
                            return {'신규주문':False}
                    else:
                        log.debug('극점가와 현재가의 가격차이가 크므로, 매매 안함.')
                        return {'신규주문':False}
                else:
                    log.debug('현재가가 상한선 하단에 위치하여 매매 안함.')
                    return {'신규주문':False}
            else:
                log.debug('보정가가 상한선 상단에 위치하여 매매 안함.')
                return {'신규주문':False}

    else:
        return {'신규주문':False}

    order_contents = {'신규주문':True, '매도수구분':mesu_medo_type, '익절틱':profit_tick, '손절틱':loss_tick, '수량':contract_cnt}
    return order_contents

def is_it_sell(subject_code, current_price, adjusted_price):
    if contract.get_contract_count(subject_code) > 0:
        # 계약 보유중
        if contract.list[subject_code]['매도수구분'] == '신규매수':
            # 매수일때
            if current_price >= contract.list[subject_code]['익절가'] and current_price >= calc.data[subject_code]['볼린저밴드']['중심선'][-1]: 
            #if current_price >= contract.list[subject_code]['익절가']:
                if contract.list[subject_code]['계약타입'][contract.DRIBBLE] > 0:
                    # 드리블 수량이 남아있다면
                    if get_time(30) >= int(subject.info[subject_code]['마감시간']) and get_time(0) < int(subject.info[subject_code]['마감시간']):
                        log.info('마감시간 임박으로 드리블 불가. 모두 청산.')
                        return {'신규주문':True, '매도수구분':'신규매도', '수량':contract.list[subject_code]['계약타입'][contract.SAFE] + contract.list[subject_code]['계약타입'][contract.DRIBBLE]}
                    else:
                        log.info("드리블 목표 달성으로 익절가 수정.")
                        contract.list[subject_code]['익절가'] = current_price + ( subject.info[subject_code]['단위'] )
                        contract.list[subject_code]['손절가'] = current_price - ( subject.info[subject_code]['주문내용']['익절틱'] * subject.info[subject_code]['단위'] )

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
            if current_price <= contract.list[subject_code]['익절가'] and current_price <= calc.data[subject_code]['볼린저밴드']['중심선'][-1]: 
            #if current_price <= contract.list[subject_code]['익절가']:
                if contract.list[subject_code]['계약타입'][contract.DRIBBLE] > 0:
                    # 드리블 수량이 남아있다면
                    if get_time(30) >= int(subject.info[subject_code]['마감시간']) and get_time(0) < int(subject.info[subject_code]['마감시간']):
                        log.info('마감시간 임박으로 드리블 불가. 모두 청산.')
                        return {'신규주문':True, '매도수구분':'신규매수', '수량':contract.list[subject_code]['계약타입'][contract.SAFE] + contract.list[subject_code]['계약타입'][contract.DRIBBLE]}
                    else:
                        log.info("드리블 목표 달성으로 익절가 수정.")
                        contract.list[subject_code]['익절가'] = current_price - ( subject.info[subject_code]['단위'] )
                        contract.list[subject_code]['손절가'] = current_price + ( subject.info[subject_code]['주문내용']['익절틱'] * subject.info[subject_code]['단위'] )
                    
                # 목표달성 청산
                if contract.list[subject_code]['계약타입'][contract.SAFE] > 0:
                    log.info("목표달성 청산으로 드리블 수량 제외하고 " + str(contract.list[subject_code]['계약타입'][contract.SAFE]) + "개 청산 요청.")
                    return {'신규주문':True, '매도수구분':'신규매수', '수량':contract.list[subject_code]['계약타입'][contract.SAFE]}
                
            elif current_price >= contract.list[subject_code]['손절가']: 
                # 손절청산
                log.info("손절가가 되어 " + str(contract.list[subject_code]['계약타입'][contract.SAFE] + contract.list[subject_code]['계약타입'][contract.DRIBBLE]) + "개 청산 요청.")
                return {'신규주문':True, '매도수구분':'신규매수', '수량':contract.list[subject_code]['계약타입'][contract.SAFE] + contract.list[subject_code]['계약타입'][contract.DRIBBLE]}

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