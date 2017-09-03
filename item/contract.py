# -*- coding: utf-8 -*-
import subject, log

list = {}

SAFE = '목표달성청산'
DRIBBLE = '드리블'
ALL = '전체'

my_deposit = 0
recent_trade_cnt = 0

def add_contract(order_info, order_contents): # 계약타입(목표달성 청산 또는 달성 후 드리블)
    """
    신규계약을 관리리스트에 추가한다.
      
    :param subject_code: 종목코드
    :param chegyul_current_price: 체결가
    :param goal_current_price: 목표가
    :param sonjul_prcie: 손절가
    :param contract_type: 계약타입(contract.SAFE | contract.DRIBBLE)
    
    dic = {} 
    dic['주문번호'] = order_info['주문번호']  
    dic['원주문번호'] = order_info['원주문번호'] 
    dic['주문유형'] = order_info['주문유형'] 
    dic['종목코드'] = order_info['종목코드']   
    dic['매도수구분'] = order_info['매도수구분']       
    dic['체결표시가격'] = order_info['체결표시가격'] 
    dic['신규수량'] = order_info['신규수량']     
    dic['청산수량'] = order_info['청산수량']     
    dic['체결수량'] = order_info['체결수량']  
    """
    
    subject_code = order_info['종목코드']
    if subject_code in list:
        log.info("%s 종목은 이미 %s계약 보유 중 입니다" % (subject_code, list[subject_code]['계약타입'][SAFE] + list[subject_code]['계약타입'][DRIBBLE]))
        
        safe_num = 0
        dribble_num = 0
        
        if subject.info[subject_code]['상태'] == '매매시도중' or subject.info[subject_code]['상태'] == '매수중' or subject.info[subject_code]['상태'] == '매도중':
            if list[subject_code]['계약타입'][SAFE] > list[subject_code]['계약타입'][DRIBBLE]:
                safe_num = int(int(order_info['신규수량'])/2)
                dribble_num = int(order_info['신규수량']) - safe_num
            else:
                dribble_num = int(int(order_info['신규수량'])/2)
                safe_num = int(order_info['신규수량']) - dribble_num

            #list[subject_code]['계약타입'][SAFE] += safe_num
            list[subject_code]['계약타입'][DRIBBLE] += dribble_num
            list[subject_code]['계약타입'][DRIBBLE] += safe_num
            
            log.info('종목코드 : ' + subject_code + ', 목표달성청산수량 ' + str(safe_num) + '개, 드리블수량 ' + str(dribble_num) + '개 추가.')
            log.info('현재 보유 계약 수량, 종목코드 : ' + subject_code + ', 목표달성청산수량 ' + str(list[subject_code]['계약타입'][SAFE]) + '개, 드리블수량 ' + str(list[subject_code]['계약타입'][DRIBBLE]) + '개 보유')
        
        else:
            log.error("%s 종목 매매가 꼬였습니다. 무엇인가 잘못되었습니다. 방금 매수한 종목 바로 청산합니다.")
            list[subject_code]['계약타입'][DRIBBLE] += int(order_info['신규수량'])
            subject.info[subject_code]['이상신호'] = True
            return False
        
        return True


    else:
        log.info("신규 계약 추가")
        subject.info[subject_code]['반전시현재가'] = float(order_info['체결표시가격'])
        list[subject_code] = {}
        
        safe_num = int(int(order_info['신규수량'])/2)
        dribble_num = int(order_info['신규수량']) - safe_num
        
        list[subject_code]['계약타입'] = {}
        list[subject_code]['계약타입'][SAFE] = 0
        list[subject_code]['계약타입'][DRIBBLE] = safe_num + dribble_num
        list[subject_code]['체결가'] = float(order_info['체결표시가격'])
        list[subject_code]['매도수구분'] = order_contents['매도수구분']

        if order_contents['매도수구분'] == '신규매도':
            list[subject_code]['익절가'] = list[subject_code]['체결가'] - order_contents['익절틱'] * subject.info[subject_code]['단위']
            list[subject_code]['손절가'] = list[subject_code]['체결가'] + order_contents['손절틱'] * subject.info[subject_code]['단위']
        elif order_contents['매도수구분'] == '신규매수':
            list[subject_code]['익절가'] = list[subject_code]['체결가'] + order_contents['익절틱'] * subject.info[subject_code]['단위']
            list[subject_code]['손절가'] = list[subject_code]['체결가'] - order_contents['손절틱'] * subject.info[subject_code]['단위']
        list[subject_code]['보유수량'] = int(order_info['신규수량'])
        log.info('종목코드 : ' + subject_code + ', 목표달성청산수량 ' + str(safe_num) + '개, 드리블수량 ' + str(dribble_num) + '개 추가.')
        log.info('현재 보유 계약 수량, 종목코드 : ' + subject_code + ', 목표달성청산수량 ' + str(list[subject_code]['계약타입'][SAFE]) + '개, 드리블수량 ' + str(list[subject_code]['계약타입'][DRIBBLE]) + '개 보유')
        log.info(list[subject_code])
        
    return True
    
def remove_contract(order_info):
    subject_code = order_info['종목코드']
    remove_cnt = int(order_info['청산수량'])
    
    if subject_code in list:
        if list[subject_code]['계약타입'][SAFE] >= remove_cnt:
            log.info("%s 종목 보유 중인 SAFE Type 계약 수 변경, 계약수 %d -> %d" % (subject_code,list[subject_code]['계약타입'][SAFE],
                                                                      list[subject_code]['계약타입'][SAFE]-remove_cnt))
            list[subject_code]['계약타입'][SAFE] -= remove_cnt
        
        else:
            remove_cnt -= list[subject_code]['계약타입'][SAFE]
            list[subject_code]['계약타입'][SAFE] = 0
            list[subject_code]['계약타입'][DRIBBLE] -= remove_cnt

            if list[subject_code]['계약타입'][DRIBBLE] == 0:
                del list[subject_code]
                log.info(subject_code + " 종목 모든 계약 청산 합니다.")
                subject.info[subject_code]['반전시현재가'] = 0

        return True
        
    else:
        log.error("%s 종목은 가지고 있는 계약이 없습니다." % subject_code)
        return False

def get_contract_count(subject_code):
    if subject_code in list:
        count = list[subject_code]['계약타입'][SAFE] + list[subject_code]['계약타입'][DRIBBLE]
        return count
    else:
        return 0
    
def delete_contract(subject_code):
    if subject_code in list:
        del list[subject_code]
        
def get_commission(account):
    if account == "5105855972":
        return 12
    elif account == "5107243872":
        return 12
    elif account == "51115392":
        return 12

    return 15