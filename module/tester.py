# -*- coding: utf-8 -*-
import kiwoom, log, contract, subject, calc, time, pymysql, subject
import log_result as res

curs = None
conn = None
kw = None
recent_price = {}

def init():
    global kw
    #지금은 의미 없음~! 월물별로 테스트하기 때문에~!
    print('테스트 시작일을 입력하세요. (ex. 20170129)')

    start_date = input()
    #end_date = get_yesterday()
    end_date = '20171002'
    #end_date = str(int(start_date) + 1)
    print('종목코드를 입력하세요. (ex. CL)')
    subject_code = input()
    
    #subject.info[str(subject_code)] = subject.info["GC"]
    #print(subject.info[subject_code])
    kw = kiwoom.api(2)

    connect(subject_code)

    not_exist_table_count = 0
    #지금은 필요없음 왜냐하면 월물별로 테스트 하기 때문에 여러 날짜를 가져올 필요가 없이 월물 1번만 가져와서 테스트하면됨~!nyny
    for date in range( int(start_date), int(end_date) ):
        tick_cnt = 0
        candle_cnt = 0
        #table_name = subject_code  +'_'+ str(date)
        table_name = subject_code
        if exist_table(table_name, subject_code) == False:
            log.info('테이블이 없음.')
            if date % 100 <= 31: not_exist_table_count+=1
            if not_exist_table_count > 10: break
            continue
        else: not_exist_table_count = 0

        print(str(date) + '테스트 시작.')
        log.info('table_name : ' + table_name)
        
        # subject_code, data 날짜에 맞는 테이블을 불러온다.
        candle = {'현재가':0, '거래량':0, '체결시간':0, '시가':0, '고가':0, '저가':999999999, '영업일자':0}
        data = read_tick(table_name)
        print('데이터개수 : ' + str(len(data)))

        time.sleep(2)
        for idx in range(len(data)):
            _tick = {}
            tick = data[idx] # 한 tick 읽어 온다.
            
            if tick != None: # tick 정보가 있으면
                candle['현재가'] = float(tick[1])
                candle['거래량'] += int(tick[2])
                #candle['체결시간'] = tick[0]
                candle['체결시간'] = tick[0].strftime('%Y%m%d%H%M%S')
                candle['영업일자'] = tick[3]
                
                if tick_cnt == 0:
                    candle['시가'] = float(tick[1])
                if candle['고가'] < float(tick[1]):
                    candle['고가'] = float(tick[1])
                if candle['저가'] > float(tick[1]):
                    candle['저가'] = float(tick[1])

                recent_price[subject_code] = float(tick[1])
                _tick = setTick(tick)
                
                tick_cnt += 1
                if candle_cnt > 10:
                    kw.OnReceiveRealData(subject_code, '해외선물시세', _tick)
                    pass
                if tick_cnt == subject.info[subject_code]['시간단위']:
                    tick_cnt = 0
                    candle_cnt += 1
                    #res.info(str(candle))
                    kw.OnReceiveTrData(subject.info[subject_code]['화면번호'], '해외선물옵션틱그래프조회', None, None, None, candle) 
                    candle = {'현재가':0, '거래량':0, '체결시간':0, '시가':0, '고가':0, '저가':999999999, '영업일자':0}  
                    #input()
            else:
                print(str(date) + ' 테스트 종료.')
                break 
        break
    disconnect()

def setTick(tick):
    return {'현재가':float(tick[1]), '체결시간':tick[0], '거래량':tick[2], '시가':float(tick[1]), '고가':float(tick[1]), '저가':float(tick[1]), '영업일자':tick[3]}

def send_order(contract_type, subject_code, contract_cnt, order_type):
    order_info = {}
    if contract_type == '신규매수':
        order_info['주문번호'] = 0        # 주문번호 
        order_info['원주문번호'] = 0       # 원주문번호
        order_info['주문유형'] = 1         # 주문유형(1 : 시장가, 2 : 지정가, 3 : STOP)
        order_info['종목코드'] = subject_code             # 종목코드
        order_info['매도수구분'] = 2      # 매도수구분(1 : 매도, 2 : 매수)
        #print("recnet_price[subject_code]:%s" % recent_price[subject_code])
        order_info['체결표시가격'] = str(round(recent_price[subject_code] + subject.info[subject_code]['단위'], subject.info[subject_code]['자릿수']))        # 체결표시가격
        if contract.get_contract_count(subject_code) > 0:
            order_info['신규수량'] = 0       # 신규수량
            order_info['청산수량'] = contract_cnt
            order_info['체결수량'] = contract_cnt
        else:
            order_info['신규수량'] = contract_cnt       # 신규수량
            order_info['청산수량'] = 0
            order_info['체결수량'] = contract_cnt
    elif contract_type == '신규매도':
        order_info['주문번호'] = 0        # 주문번호 
        order_info['원주문번호'] = 0       # 원주문번호
        order_info['주문유형'] = 1         # 주문유형(1 : 시장가, 2 : 지정가, 3 : STOP)
        order_info['종목코드'] = subject_code             # 종목코드
        order_info['매도수구분'] = 1       # 매도수구분(1 : 매도, 2 : 매수)
        #print("recnet_price[subject_code]:%s" % recent_price[subject_code])
        order_info['체결표시가격'] = str(round(recent_price[subject_code] - subject.info[subject_code]['단위'], subject.info[subject_code]['자릿수']))        # 체결표시가격
        if contract.get_contract_count(subject_code) > 0:
            order_info['신규수량'] = 0       # 신규수량
            order_info['청산수량'] = contract_cnt
            order_info['체결수량'] = contract_cnt
        else:
            order_info['신규수량'] = contract_cnt       # 신규수량
            order_info['청산수량'] = 0
            order_info['체결수량'] = contract_cnt

    kw.OnReceiveChejanData('1', None, None, order_info)
        
    return 0

def get_yesterday():
    return time.localtime().tm_year * 10000 + time.localtime().tm_mon * 100 + time.localtime().tm_mday

def connect(subject_code):
    global curs
    global conn
    if subject_code == 'GCJ17' or subject_code == 'GCM17' or subject_code == 'GCQ17':
        conn = pymysql.connect(host='211.253.10.91', user='root', password='goehddl', db='haedong', charset='utf8')
    else:
        conn = pymysql.connect(host='211.253.10.91', user='root', password='goehddl', db='haedong4', charset='utf8')
    curs = conn.cursor()

def disconnect():
    conn.close()

def read_tick(table_name):
    #conn = pymysql.connect(host='211.253.28.132', user='root', password='goehddl', db='test_db1', charset='utf8')
    #curs = conn.cursor()
    
    global curs
    global conn
    query = "select date, price, volume, working_day from %s"%table_name
    #query = "select date, now_price, volume, working_day from %s"%table_name
    curs.execute(query)
    conn.commit()   
    
#    rows = curs.fetchone()
    row =curs.fetchall()
    
    return row

def exist_table(table_name, subject_code):
    global curs
    global conn
    temp = []
    #conn = pymysql.connect(host='211.253.28.132', user='root', password='goehddl', db='test_db1', charset='utf8')
    #curs = conn.cursor()
    if subject_code == 'GCJ17' or subject_code == 'GCM17' or subject_code == 'GCQ17':
        query = "show tables in haedong like '%s'"%table_name
    else:
        query = "show tables in haedong4 like '%s'" % table_name
    curs.execute(query)
    conn.commit()
    
    temp = curs.fetchone()

    if temp != None and temp[0] == table_name:
        return True
    else: return False
