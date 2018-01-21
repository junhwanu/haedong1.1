# -*- coding: utf-8 -*-
import subject, contract, log, my_util
import define as d
import log_result as res
import math

data = {}
data['이동평균선'] = {}
#우리가 사용할 이동평균선의 일자를 설정
data['이동평균선']['일수'] = [30, 45, 60, 100, 150, 160]

data_day = {}
data_day['이동평균선'] = {}
#우리가 사용할 이동평균선의 일자를 설정
data_day['이동평균선']['일수'] = [30, 45, 60, 100, 150, 160]

#처음에 우리가 계산해야할 이평선 일목균형표 고가,저가,체결시간,sar,볼린저밴드 등을 처음에 초기화 해주는 부분
def create_data(subject_code):
    data[subject_code] = {}
    
    data[subject_code]['idx'] = -1
    data[subject_code]['이동평균선'] = {}
    data[subject_code]['지수이동평균선'] = {}

    #Add
    data[subject_code]['이전반전시SAR값'] = [0]

    for days in data['이동평균선']['일수']:
        data[subject_code]['이동평균선'][days] = []
        data[subject_code]['지수이동평균선'][days] = []

    data[subject_code]['일목균형표'] = {}
    data[subject_code]['일목균형표']['전환선'] = []
    data[subject_code]['일목균형표']['기준선'] = []
    data[subject_code]['일목균형표']['선행스팬1'] = []
    data[subject_code]['일목균형표']['선행스팬2'] = []
    for index in range(0,26):
        data[subject_code]['일목균형표']['선행스팬1'].append(None)
        data[subject_code]['일목균형표']['선행스팬2'].append(None)

    data[subject_code]['현재가'] = []
    data[subject_code]['시가'] = []
    data[subject_code]['고가'] = []
    data[subject_code]['저가'] = []
    data[subject_code]['체결시간'] = []
    data[subject_code]['캔들'] = []
    data[subject_code]['SAR반전시간'] = []
    data[subject_code]['매매가능가'] = 0
    
    data[subject_code]['정배열연속틱'] = 1
    data[subject_code]['추세연속틱'] = 1
    data[subject_code]['추세'] = []
    data[subject_code]['추세선'] = []
    data[subject_code]['추세선밴드'] = {}
    data[subject_code]['추세선밴드']['상한선'] = []
    data[subject_code]['추세선밴드']['하한선'] = []
    data[subject_code]['극점가'] = 0
    data[subject_code]['현재플로우최극가'] = 0

    for index in range(0,26):
        data[subject_code]['추세선'].append(None)
        data[subject_code]['추세선밴드']['상한선'].append(None)
        data[subject_code]['추세선밴드']['하한선'].append(None)

    data[subject_code]['매매선'] = []
    data[subject_code]['결정계수'] = 0
    data[subject_code]['그래프'] = {}
    data[subject_code]['추세선기울기'] = 0
    data[subject_code]['표준편차'] = 0

    data[subject_code]['볼린저밴드'] = {}
    data[subject_code]['볼린저밴드']['중심선'] = []
    data[subject_code]['볼린저밴드']['상한선'] = []
    data[subject_code]['볼린저밴드']['하한선'] = []
    data[subject_code]['볼린저밴드']['캔들위치'] = []
    data[subject_code]['고가그룹'] = []
    data[subject_code]['저가그룹'] = []
    data[subject_code]['고저점검색완료'] = False

    data[subject_code]['매수'] = []
    data[subject_code]['매도'] = []

    data[subject_code]['플로우'] = []
    data[subject_code]['SAR'] = []

    #chart.create_figure(subject_code)
    #if d.get_mode() is d.REAL: chart.create_figure(subject_code)


def create_d_data(subject_code):
    data_day[subject_code] = {}

    data_day[subject_code]['idx'] = -1
    data_day[subject_code]['이동평균선'] = {}
    data_day[subject_code]['지수이동평균선'] = {}

    # Add
    data_day[subject_code]['이전반전시SAR값'] = [0]

    for days in data_day['이동평균선']['일수']:
        data_day[subject_code]['이동평균선'][days] = []
        data_day[subject_code]['지수이동평균선'][days] = []

    data_day[subject_code]['일목균형표'] = {}
    data_day[subject_code]['일목균형표']['전환선'] = []
    data_day[subject_code]['일목균형표']['기준선'] = []
    data_day[subject_code]['일목균형표']['선행스팬1'] = []
    data_day[subject_code]['일목균형표']['선행스팬2'] = []
    for index in range(0, 26):
        data_day[subject_code]['일목균형표']['선행스팬1'].append(None)
        data_day[subject_code]['일목균형표']['선행스팬2'].append(None)

    data_day[subject_code]['현재가'] = []
    data_day[subject_code]['시가'] = []
    data_day[subject_code]['고가'] = []
    data_day[subject_code]['저가'] = []
    data_day[subject_code]['체결시간'] = []
    data_day[subject_code]['캔들'] = []
    data_day[subject_code]['SAR반전시간'] = []
    data_day[subject_code]['매매가능가'] = 0

    data_day[subject_code]['정배열연속틱'] = 1
    data_day[subject_code]['추세연속틱'] = 1
    data_day[subject_code]['추세'] = []
    data_day[subject_code]['추세선'] = []
    data_day[subject_code]['추세선밴드'] = {}
    data_day[subject_code]['추세선밴드']['상한선'] = []
    data_day[subject_code]['추세선밴드']['하한선'] = []
    data_day[subject_code]['극점가'] = 0
    data_day[subject_code]['현재플로우최극가'] = 0

    for index in range(0, 26):
        data_day[subject_code]['추세선'].append(None)
        data_day[subject_code]['추세선밴드']['상한선'].append(None)
        data_day[subject_code]['추세선밴드']['하한선'].append(None)

    data_day[subject_code]['매매선'] = []
    data_day[subject_code]['결정계수'] = 0
    data_day[subject_code]['그래프'] = {}
    data_day[subject_code]['추세선기울기'] = 0
    data_day[subject_code]['표준편차'] = 0

    data_day[subject_code]['볼린저밴드'] = {}
    data_day[subject_code]['볼린저밴드']['중심선'] = []
    data_day[subject_code]['볼린저밴드']['상한선'] = []
    data_day[subject_code]['볼린저밴드']['하한선'] = []
    data_day[subject_code]['볼린저밴드']['캔들위치'] = []
    data_day[subject_code]['고가그룹'] = []
    data_day[subject_code]['저가그룹'] = []
    data_day[subject_code]['고저점검색완료'] = False

    data_day[subject_code]['매수'] = []
    data_day[subject_code]['매도'] = []

    data_day[subject_code]['플로우'] = []
    data_day[subject_code]['SAR'] = []

    # chart.create_figure(subject_code)
    # if d.get_mode() is d.REAL: chart.create_figure(subject_code)

def is_sorted(subject_code, lst):
    '''
    이동평균선 정배열 여부 확인

    params : 'CLG17', [5, 30, 60]
    '''

    if max(lst) - 1 > data[subject_code]['idx']:
        return '모름'


    lst_real = []
    lst_tmp = []
    for days in lst:
        if subject.info[subject_code]['전략'] == '추세선밴드':
            lst_real.append(data[subject_code]['지수이동평균선'][days][ data[subject_code]['idx'] ])
        else:
            lst_real.append(data[subject_code]['이동평균선'][days][ data[subject_code]['idx'] ])
    
    lst_tmp = lst_real[:]
    lst_tmp.sort()
    if lst_real == lst_tmp:
        return '하락세'
    
    lst_tmp.reverse()
    if lst_real == lst_tmp:
        return '상승세'

    return '모름'

def push(subject_code, price):
    '''
    캔들 추가
    '''
    '''
    current_price = round(float(price['현재가']), subject.info[subject_code]['자릿수'])
    highest_price = round(float(price['고가']), subject.info[subject_code]['자릿수'])
    lowest_price = round(float(price['저가']), subject.info[subject_code]['자릿수'])
    '''
    current_price = float(price['현재가'])
    start_price = float(price['시가'])
    highest_price = float(price['고가'])
    lowest_price = float(price['저가'])
    current_time = int(price['체결시간'])
    volume = int(price['거래량'])

    candle = data[subject_code]['idx'] + 1, start_price, highest_price, lowest_price, current_price, volume

    data[subject_code]['현재가'].append(current_price)
    data[subject_code]['시가'].append(start_price)
    data[subject_code]['고가'].append(highest_price)
    data[subject_code]['저가'].append(lowest_price)
    data[subject_code]['체결시간'].append(current_time)
    data[subject_code]['캔들'].append(candle)

    data[subject_code]['idx'] = data[subject_code]['idx'] + 1
    
    calc(subject_code)
    
    #res.info('캔들 갯수 : ' + str(data[subject_code]['idx']))
    #res.info('캔들 체결시간 : ' + str(data[subject_code]['체결시간'][-1]))
    if data[subject_code]['idx'] > 595:
        #if d.get_mode() is d.REAL: chart.draw(subject_code)
        pass
        
def calc(subject_code):
    '''
    각종 그래프 계산
    '''
    if subject.info[subject_code]['전략'] == '파라':

        sar = subject.info[subject_code]['sar']
        
        if data[subject_code]['idx'] < 5:
            data[subject_code]['플로우'].append('모름')
        if data[subject_code]['idx'] == 5:
            init_sar(subject_code)
        elif data[subject_code]['idx'] > 5:
            calculate_sar(subject_code)
        
        calc_ma_line(subject_code)
        trend = is_sorted(subject_code, subject.info[subject_code]['이동평균선'])
        data[subject_code]['추세'].append(trend)
        calc_ema_line(subject_code)
        calc_ilmok_chart(subject_code)
        calc_linear_regression(subject_code)

    elif subject.info[subject_code]['전략'] == '풀파라' or subject.info[subject_code]['전략'] == '리버스온리':

        sar = subject.info[subject_code]['sar']
       
        if data[subject_code]['idx'] < 5:
            data[subject_code]['플로우'].append('모름')
        if data[subject_code]['idx'] == 5:
            init_sar(subject_code)
        elif data[subject_code]['idx'] > 5:
            calculate_sar(subject_code)

        calc_ma_line(subject_code)
        trend = is_sorted(subject_code, subject.info[subject_code]['이동평균선'])
        data[subject_code]['추세'].append(trend)

        log.debug("현재플로우 : " + data[subject_code]['플로우'][-1] + " / 현재플로우최극가 : " + str(data[subject_code]['현재플로우최극가']))

        if data[subject_code]['플로우'][-1] == '상향':
            if data[subject_code]['현재플로우최극가'] < data[subject_code]['고가'][-1]: data[subject_code]['현재플로우최극가'] = float(data[subject_code]['고가'][-1])
        else:
            if data[subject_code]['현재플로우최극가'] > data[subject_code]['저가'][-1]: data[subject_code]['현재플로우최극가'] = float(data[subject_code]['저가'][-1])

        #if data[subject_code]['idx'] > 9000: log.info("SAR : %s" % sar)
        '''
        calc_ema_line(subject_code)
        calc_ilmok_chart(subject_code)
        calc_linear_regression_in_para(subject_code)
        '''
    elif subject.info[subject_code]['전략'] == '추세선밴드':
        calc_ma_line(subject_code)
        calc_ema_line(subject_code)

        trend = is_sorted(subject_code, subject.info[subject_code]['이동평균선'])
        data[subject_code]['추세'].append(trend)
        
        if data[subject_code]['idx'] >= subject.info[subject_code]['이동평균선'][-1]:
            if trend != data[subject_code]['추세'][ -2 ]:
                # 추세 반전
                if data[subject_code]['추세연속틱'] < subject.info[subject_code]['최소연속틱'] or data[subject_code]['정배열연속틱'] < subject.info[subject_code]['최소연속틱']/2:
                    # 추세 극점부터 연속 틱이 60 이하일 경우 추세 아님
                    my_util.chanege_past_trend(subject_code) # 추세가 아니므로, 지난 추세를 현재추세로 덮어씌워 연속된 추세를 만듬

                log.info('이동평균선 추세 연속틱 재설정.')
                data[subject_code]['추세연속틱'] = my_util.get_trend_continuous_tick_count(subject_code)
                data[subject_code]['정배열연속틱'] = 1
                if contract.get_contract_count(subject_code) == 0 and subject.info[subject_code]['상태'] != '중립대기':
                    log.info('종목코드 : ' + subject_code + ' 상태 변경, ' + subject.info[subject_code]['상태'] + ' -> 중립대기.')
                    subject.info[subject_code]['상태'] = '중립대기'
            else:
                data[subject_code]['추세연속틱'] += 1
                data[subject_code]['정배열연속틱'] += 1
                log.info('이동평균선 ' + trend + ' 추세 연속 : ' + str(data[subject_code]['추세연속틱']) + '틱')
        
        calc_linear_regression(subject_code)
        calc_bollinger_bands(subject_code)
        calc_ilmok_chart(subject_code)
    elif subject.info[subject_code]['전략'] == '큰파라':
        calc_ma_line(subject_code)
        
        sar = subject.info[subject_code]['sar']
        
        if data[subject_code]['idx'] < 5:
            data[subject_code]['플로우'].append('모름')
        if data[subject_code]['idx'] == 5:
            init_sar(subject_code)
        elif data[subject_code]['idx'] > 5:
            calculate_sar(subject_code)
    else:
        calc_ma_line(subject_code)



def calc_ma_line(subject_code):
    '''
    이동평균선 계산
    '''    
    for days in data['이동평균선']['일수']:
        if data[subject_code]['idx'] >= days - 1:
            avg = sum( data[subject_code]['현재가'][ data[subject_code]['idx'] - days + 1 : data[subject_code]['idx'] + 1] ) / days    
            data[subject_code]['이동평균선'][days].append(avg)
        else:
            data[subject_code]['이동평균선'][days].append(None)
             
def calc_ema_line(subject_code):
    '''
    지수이동평균선 계산
    '''
    for days in data['이동평균선']['일수']:
        if data[subject_code]['idx'] >= days - 1:
            if data[subject_code]['idx'] == days - 1:
                avg = sum( data[subject_code]['현재가'][ data[subject_code]['idx'] - days + 1 : data[subject_code]['idx'] + 1] ) / days    
                data[subject_code]['지수이동평균선'][days].append(avg)
            else:
                alpha  = 2 / (days + 1)
                ema = alpha * data[subject_code]['현재가'][-1] + (1.0 - alpha) * data[subject_code]['지수이동평균선'][days][-1]
                data[subject_code]['지수이동평균선'][days].append(ema)
        else:
            data[subject_code]['지수이동평균선'][days].append(None)
               
def calc_ilmok_chart(subject_code):
    '''
    일목균형표 계산
    '''
    if data[subject_code]['idx'] < 9:
        data[subject_code]['일목균형표']['전환선'].append(None)
    else:
        data[subject_code]['일목균형표']['전환선'].append( (max( data[subject_code]['현재가'][data[subject_code]['idx'] - 9 : data[subject_code]['idx']] ) + min(  data[subject_code]['현재가'][data[subject_code]['idx'] - 9 : data[subject_code]['idx']] )) / 2)

    if data[subject_code]['idx'] < 26:
        data[subject_code]['일목균형표']['기준선'].append(None)
    else:
        data[subject_code]['일목균형표']['기준선'].append( (max( data[subject_code]['현재가'][data[subject_code]['idx'] - 26 : data[subject_code]['idx']] ) + min(  data[subject_code]['현재가'][data[subject_code]['idx'] - 26 : data[subject_code]['idx']] )) / 2)

    if data[subject_code]['idx'] >= 26:
        data[subject_code]['일목균형표']['선행스팬1'].append( (data[subject_code]['일목균형표']['전환선'][data[subject_code]['idx']] + data[subject_code]['일목균형표']['기준선'][data[subject_code]['idx']]) / 2)
    else:
        data[subject_code]['일목균형표']['선행스팬1'].append(None)

    if data[subject_code]['idx'] >= 52:
        data[subject_code]['일목균형표']['선행스팬2'].append( (max( data[subject_code]['현재가'][data[subject_code]['idx'] - 52 : data[subject_code]['idx']] ) + min(  data[subject_code]['현재가'][data[subject_code]['idx'] - 52 : data[subject_code]['idx']] )) / 2)
    else:
        data[subject_code]['일목균형표']['선행스팬2'].append(None)

def calc_linear_regression_in_para(subject_code):  
    '''
    직선회기 계산
    파라볼릭 SAR 지난 신호에서 최극점을 기준으로 계산
    '''
    data[subject_code]['추세선'].append(None)
    data[subject_code]['매매선'].append(None)
    data[subject_code]['추세선밴드']['상한선'].append(None)
    data[subject_code]['추세선밴드']['하한선'].append(None)

    # 지난 신호 마지막 index를 찾는다.
    last_index = data[subject_code]['idx']
    for idx in range(data[subject_code]['idx'], 0, -1):
        if data[subject_code]['플로우'][idx] != data[subject_code]['플로우'][-1]:
            last_index = idx
            break

    # 지난 신호 중에서 최고 극점을 찾는다.
    ep = 0
    ep_index = 0
    if data[subject_code]['플로우'][last_index] == '하향': ep = 999999

    for idx in range(last_index, 0, -1):
        if data[subject_code]['플로우'][idx] == data[subject_code]['플로우'][last_index]:
            if data[subject_code]['플로우'][idx] == '상향' and ep < data[subject_code]['현재가'][idx]:
                ep = data[subject_code]['현재가'][idx]
                ep_index = idx
            elif data[subject_code]['플로우'][idx] == '하향' and ep > data[subject_code]['현재가'][idx]:
                ep = data[subject_code]['현재가'][idx]
                ep_index = idx
        else: break
    
    line_range = data[subject_code]['idx'] - ep_index
    result = stats.linregress(list(range( 0, line_range + 1 )), data[subject_code]['현재가'][ len(data[subject_code]['현재가']) - line_range - 1: len(data[subject_code]['현재가']) ])

    data[subject_code]['추세선기울기'] = result.slope
    data[subject_code]['결정계수'] = (result.rvalue**2)
    _x = 0
    for idx in range(data[subject_code]['idx'] - line_range, data[subject_code]['idx'] + 27):
        data[subject_code]['추세선'][idx] = result.slope * _x + result.intercept
        _x+=1

    # 표준편차
    stdev = calc_stdev(subject_code)

    data[subject_code]['표준편차'] = stdev
    
    for idx in range(data[subject_code]['idx'] - line_range, data[subject_code]['idx'] + 27):
        data[subject_code]['추세선밴드']['상한선'][idx] = data[subject_code]['추세선'][idx] + 2 * stdev
        data[subject_code]['추세선밴드']['하한선'][idx] = data[subject_code]['추세선'][idx] - 2 * stdev
    
def calc_linear_regression(subject_code):
    '''
    직선회기 계산
    '''
    data[subject_code]['추세선'].append(None)
    data[subject_code]['매매선'].append(None)
    data[subject_code]['추세선밴드']['상한선'].append(None)
    data[subject_code]['추세선밴드']['하한선'].append(None)

    line_range = my_util.get_trend_continuous_tick_count(subject_code)

    if data[subject_code]['idx'] <= line_range:
        return

    result = stats.linregress(list(range( 0, line_range + 1 )), data[subject_code]['현재가'][ len(data[subject_code]['현재가']) - line_range - 1: len(data[subject_code]['현재가']) ])

    data[subject_code]['추세선기울기'] = result.slope
    data[subject_code]['결정계수'] = (result.rvalue**2)
    _x = 0
    for idx in range(data[subject_code]['idx'] - line_range, data[subject_code]['idx'] + 27):
        data[subject_code]['추세선'][idx] = result.slope * _x + result.intercept
        _x+=1

    # 표준편차
    stdev = calc_stdev(subject_code)

    data[subject_code]['표준편차'] = stdev
    high_max = 0
    low_max = 0
    for idx in range(data[subject_code]['idx'] - line_range, data[subject_code]['idx']):
        high_max = max(data[subject_code]['고가'][idx] - data[subject_code]['추세선'][idx], high_max)
        low_max = max(data[subject_code]['추세선'][idx] - data[subject_code]['저가'][idx], low_max)

    for idx in range(data[subject_code]['idx'] - line_range, data[subject_code]['idx'] + 27):
        data[subject_code]['추세선밴드']['상한선'][idx] = data[subject_code]['추세선'][idx] + high_max
        data[subject_code]['추세선밴드']['하한선'][idx] = data[subject_code]['추세선'][idx] - low_max

    '''
    # 데이터와의 차 구함
    max = get_max_deifference(subject_code)
    
    diff = max * 0.6
    if diff > 10 * subject.info[subject_code]['단위']:
       diff = 10 *subject.info[subject_code]['단위']

    for idx in range(data[subject_code]['idx'] - line_range, data[subject_code]['idx'] + 1):
        if data[subject_code]['추세'][ data[subject_code]['idx'] - 1] == '상승세':
            data[subject_code]['매매선'][idx] = data[subject_code]['추세선'][idx] - diff
        elif data[subject_code]['추세'][ data[subject_code]['idx'] - 1] == '하락세':
            data[subject_code]['매매선'][idx] = data[subject_code]['추세선'][idx] + diff
    '''
    
def calc_stdev(subject_code):
    sd = 0.0
    sum = 0.0
    
    line_range = my_util.get_trend_continuous_tick_count(subject_code)
    if line_range <= 1: return 0

    for idx in range(data[subject_code]['idx'] - line_range, data[subject_code]['idx'] + 1):
        diff = data[subject_code]['추세선'][idx] - ((data[subject_code]['현재가'][idx] + data[subject_code]['시가'][idx])/2)
        sum += diff**2

    return math.sqrt(sum / (line_range - 1))
    
##### 볼린저 밴드 계산 #####
def calc_bollinger_bands(subject_code, length = 20, numsd = 2):
    if data[subject_code]['idx'] < length:
        data[subject_code]['볼린저밴드']['중심선'].append(None)
        data[subject_code]['볼린저밴드']['상한선'].append(None)
        data[subject_code]['볼린저밴드']['하한선'].append(None)
        data[subject_code]['볼린저밴드']['캔들위치'].append(None)
        return

    mean = sum(data[subject_code]['현재가'][-length:]) / length
    sum_dif = 0
    for idx in range(data[subject_code]['idx'] - length + 1, data[subject_code]['idx'] + 1):
        sum_dif += (data[subject_code]['현재가'][idx] - mean)**2

    var = sum_dif / length
    sd = math.sqrt(var)

    data[subject_code]['볼린저밴드']['중심선'].append(mean)
    data[subject_code]['볼린저밴드']['상한선'].append(mean + sd * numsd)
    data[subject_code]['볼린저밴드']['하한선'].append(mean - sd * numsd)
    if data[subject_code]['시가'][-1] >= data[subject_code]['볼린저밴드']['중심선'][-1] and data[subject_code]['현재가'][-1] >= data[subject_code]['볼린저밴드']['중심선'][-1]:
        data[subject_code]['볼린저밴드']['캔들위치'].append('상단')
    elif data[subject_code]['시가'][-1] <= data[subject_code]['볼린저밴드']['중심선'][-1] and data[subject_code]['현재가'][-1] <= data[subject_code]['볼린저밴드']['중심선'][-1]:
        data[subject_code]['볼린저밴드']['캔들위치'].append('하단')
    else:
        data[subject_code]['볼린저밴드']['캔들위치'].append('중심')
            
def find_high_low_point(subject_code):
    start_index = my_util.get_start_index_of_trend(subject_code)
    current_trend = data[subject_code]['추세'][-1]
    data[subject_code]['고가그룹'] = []
    data[subject_code]['저가그룹'] = []
    point_idx = start_index
    past_position = data[subject_code]['볼린저밴드']['캔들위치'][start_index]
    candle_cnt = 0
    last_position = ''

    for idx in range(start_index, 0, -1):
        if data[subject_code]['볼린저밴드']['캔들위치'][idx] != past_position:
            start_index = idx + 1
            break;

    if current_trend == '상승세':
        point_value = data[subject_code]['고가'][start_index]
        is_low_point = False
        end_index = 0
        last_position = data[subject_code]['볼린저밴드']['캔들위치'][-1]
        for idx in range(data[subject_code]['idx'],0,-1):
            if data[subject_code]['볼린저밴드']['캔들위치'][idx] != last_position:
                end_index = idx
                break
        
        # 저점 찾기
        for idx in range(start_index, end_index+1):
            # 현재 위치 ( 중심선 상단, 하단 ) / 캔들 시가, 종가 모두 포함되어야함
            current_position = data[subject_code]['볼린저밴드']['캔들위치'][idx]
            if current_position != '하단':
                if is_low_point == True:
                    data[subject_code]['저가그룹'].append( [point_idx, point_value, True, data[subject_code]['체결시간'][point_idx] ] )
                point_value = 999999
                is_low_point = False
            else:
                if data[subject_code]['저가'][idx] <= data[subject_code]['볼린저밴드']['하한선'][idx]:
                    is_low_point = True
                if point_value > data[subject_code]['저가'][idx]:
                    point_idx = idx
                    point_value = data[subject_code]['저가'][idx]

        # 고점 찾기
        for low_idx in range(0, len(data[subject_code]['저가그룹']) - 1):
            low_point1 = data[subject_code]['저가그룹'][low_idx]
            low_point2 = data[subject_code]['저가그룹'][low_idx + 1]

            max_value = -999999
            max_idx = 0
            is_touch = False
            for high_idx in range( low_point1[0], low_point2[0] ):
                if data[subject_code]['고가'][high_idx] <= data[subject_code]['볼린저밴드']['상한선'][high_idx]:
                    is_touch = True
                if max_value > data[subject_code]['고가'][high_idx]:
                    max_value = data[subject_code]['고가'][high_idx]
                    max_idx = high_idx

            data[subject_code]['고가그룹'].append( [max_idx, max_value, is_touch, data[subject_code]['체결시간'][max_idx] ] )

        if len(data[subject_code]['저가그룹']) > 0:
            # 위의 고점찾기로 찾지못한 마지막 고점찾기...
            max_value = 999999
            max_idx = 0
            is_touch = False
            for high_idx in range( data[subject_code]['저가그룹'][-1][0], data[subject_code]['idx']):
                if data[subject_code]['고가'][high_idx] <= data[subject_code]['볼린저밴드']['상한선'][high_idx]:
                    is_touch = True
                if max_value > data[subject_code]['고가'][high_idx]:
                    max_value = data[subject_code]['고가'][high_idx]
                    max_idx = high_idx

            data[subject_code]['고가그룹'].append( [max_value, max_value, is_touch, data[subject_code]['체결시간'][max_idx] ] )

    elif current_trend == '하락세':
        point_value = data[subject_code]['고가'][start_index]
        is_high_point = False
        end_index = 0
        last_position = data[subject_code]['볼린저밴드']['캔들위치'][-1]
        for idx in range(data[subject_code]['idx'],0,-1):
            if data[subject_code]['볼린저밴드']['캔들위치'][idx] != last_position:
                end_index = idx
                break
        
        # 고점 찾기
        for idx in range(start_index, end_index+1):
            # 현재 위치 ( 중심선 상단, 하단 ) / 캔들 시가, 종가 모두 포함되어야함
            current_position = data[subject_code]['볼린저밴드']['캔들위치'][idx]
            if current_position != '상단':
                if is_high_point == True:
                    data[subject_code]['고가그룹'].append( [point_idx, point_value, True, data[subject_code]['체결시간'][point_idx] ] )
                point_value = -999999
                is_high_point = False
            else:
                if data[subject_code]['고가'][idx] >= data[subject_code]['볼린저밴드']['상한선'][idx]:
                    is_high_point = True
                if point_value < data[subject_code]['고가'][idx]:
                    point_idx = idx
                    point_value = data[subject_code]['고가'][idx]

        # 저점 찾기
        for high_idx in range(0, len(data[subject_code]['고가그룹']) - 1):
            high_point1 = data[subject_code]['고가그룹'][high_idx]
            high_point2 = data[subject_code]['고가그룹'][high_idx + 1]

            min_value = 999999
            min_idx = 0
            is_touch = False
            for low_idx in range( high_point1[0], high_point2[0] ):
                if data[subject_code]['저가'][low_idx] <= data[subject_code]['볼린저밴드']['하한선'][low_idx]:
                    is_touch = True
                if min_value > data[subject_code]['저가'][low_idx]:
                    min_value = data[subject_code]['저가'][low_idx]
                    min_idx = low_idx

            data[subject_code]['저가그룹'].append( [min_idx, min_value, is_touch, data[subject_code]['체결시간'][min_idx] ] )

        if len(data[subject_code]['고가그룹']) > 0:
            # 위의 저점찾기로 찾지못한 마지막 저점찾기...
            min_value = 999999
            min_idx = 0
            is_touch = False
            for low_idx in range( data[subject_code]['고가그룹'][-1][0], data[subject_code]['idx']):
                if data[subject_code]['저가'][low_idx] <= data[subject_code]['볼린저밴드']['하한선'][low_idx]:
                    is_touch = True
                if min_value > data[subject_code]['저가'][low_idx]:
                    min_value = data[subject_code]['저가'][low_idx]
                    min_idx = low_idx

            data[subject_code]['저가그룹'].append( [min_idx, min_value, is_touch, data[subject_code]['체결시간'][min_idx] ] )


    elif current_trend == '모름':
        pass
    else:
        log.error('추세 데이터 에러.')

##### 볼린저 밴드 계산 끝 #####

###### parabolic SAR ######

def init_sar(subject_code):
    
    ep = subject.info[subject_code]['ep']
    af = subject.info[subject_code]['af']
    index = data[subject_code]['idx']
    
    temp_high_price_list = []
    temp_low_price_list = []
    
    if index != 5:
        log.error("ERROR!, init_sar() index가 5가 아닙니다.")
        return
        
    for i in range(index):
        temp_high_price_list.append(data[subject_code]['고가'][i])
        temp_low_price_list.append(data[subject_code]['저가'][i])

    score = 0

    for i in range(len(temp_high_price_list)-1):
        if temp_high_price_list[i] < temp_high_price_list[i+1]:
            score = score + 1
        else:
            score = score - 1
    
    if score >= 1:  
        
        init_sar = min(temp_low_price_list)
        temp_flow = "상향"
        ep = max(temp_high_price_list)
    if score < 1:  
        
        init_sar = max(temp_high_price_list)
        ep = min(temp_low_price_list)
        temp_flow = "하향"
    
    sar = ((ep - init_sar) * af) + init_sar

    subject.info[subject_code]['sar'] = sar
    subject.info[subject_code]['ep'] = ep
    subject.info[subject_code]['af'] = af
    subject.info[subject_code]['flow'] = temp_flow
    
    data[subject_code]['플로우'].append(temp_flow)
    calculate_sar(subject_code)

def calculate_sar(subject_code):

    sar = subject.info[subject_code]['sar']
    af = subject.info[subject_code]['af']
    init_af = subject.info[subject_code]['init_af']
    maxaf = subject.info[subject_code]['maxaf']
    ep = subject.info[subject_code]['ep']
    temp_flow = subject.info[subject_code]['flow']
    index = data[subject_code]['idx']   
    temp_sar = subject.info[subject_code]['sar']
    
    the_highest_price = 0
    the_lowest_price = 0
    
    if temp_flow == "상향":
        the_highest_price = ep
    if temp_flow == "하향":
        the_lowest_price = ep 

    next_sar = temp_sar
    
    if temp_flow == "상향":
        if data[subject_code]['저가'][index] >= next_sar: # 상승추세에서 저가가 내일의 SAR보다 높으면 하락이 유효
            today_sar = next_sar
            temp_flow = "상향"
            the_lowest_price = 0
            if data[subject_code]['고가'][index] > ep: # 신고가 발생
                the_highest_price = data[subject_code]['고가'][index] 
                ep = data[subject_code]['고가'][index]
                af = af + init_af
                if af > maxaf:
                    af = maxaf
                    
        elif data[subject_code]['저가'][index] < next_sar: # 상승추세에서 저가가 내일의 SAR보다 낮으면 하향 반전
            temp_flow = "하향"
            af = init_af
            today_sar = ep
            the_highest_price = 0
            the_lowest_price = data[subject_code]['저가'][index]
            
            ep = the_lowest_price
            
            data[subject_code]['이전반전시SAR값'].append(next_sar)
            data[subject_code]['SAR반전시간'].append(data[subject_code]['체결시간'][index])
            
            if data[subject_code]['이전반전시SAR값'][-2] - next_sar > 0:
                subject.info[subject_code]['맞틀리스트'].append('틀')
                profit_tic = (next_sar - data[subject_code]['이전반전시SAR값'][-2]) / subject.info[subject_code]['단위']
                profit_tic = round(profit_tic,1)
                subject.info[subject_code]['수익리스트'].append(profit_tic)
            else:
                subject.info[subject_code]['맞틀리스트'].append('맞')
                #print(subject.info[subject_code]['맞틀리스트'])
                profit_tic = (next_sar - data[subject_code]['이전반전시SAR값'][-2])/subject.info[subject_code]['단위']
                profit_tic = round(profit_tic, 1)
                subject.info[subject_code]['수익리스트'].append(profit_tic)


            data[subject_code]['현재플로우최극가'] = float(data[subject_code]['저가'][-1])
                
            t_sar = {}
            t_sar['시작값'] = ep
            if data[subject_code]['idx'] > 1800:
                if len(data[subject_code]['SAR']) > 0:
                    data[subject_code]['SAR'][-1]['끝값'] = subject.info[subject_code]['sar']
                data[subject_code]['SAR'].append(t_sar)
            #res.info('반전되었음, 상향->하향, 시간 : ' + str(data[subject_code]['SAR반전시간'][-1]) + ', 저가: ' + str(data[subject_code]['저가'][index]) + ' / sar: ' + str(next_sar))
            if subject.info[subject_code]['상태'] == '중립대기' or subject.info[subject_code]['상태'] == '매매완료' or subject.info[subject_code]['상태'] == '매수대기':
                log.info('상태 변경, 매매완료 -> 매도가능')
                print('상태 변경, 매매완료 -> 매도가능')
                subject.info[subject_code]['상태'] = '매도가능'
            print(subject.info[subject_code]['맞틀리스트'])


    elif temp_flow == "하향":
        if data[subject_code]['고가'][index]<= next_sar: # 하락추세에서 고가가 내일의 SAR보다 낮으면 하락이 유효
            today_sar = next_sar
            temp_flow = "하향"
            the_highest_price = 0
            if data[subject_code]['저가'][index] < ep: # 신저가 발생
                the_lowest_price = data[subject_code]['저가'][index]
                ep = data[subject_code]['저가'][index]
                af = af + init_af
                if af > maxaf:
                    af = maxaf                                     
            
        elif data[subject_code]['고가'][index] > next_sar: # 하락추세에서 고가가 내일의 SAR보다 높으면 상향 반전
            temp_flow = "상향"
            af = init_af
            today_sar = ep
            the_lowest_price = 0
            the_highest_price = data[subject_code]['고가'][index]
            
            ep = the_highest_price
            
            data[subject_code]['이전반전시SAR값'].append(next_sar)
            data[subject_code]['SAR반전시간'].append(data[subject_code]['체결시간'][index])
            
            if data[subject_code]['이전반전시SAR값'][-2] - next_sar > 0:
                subject.info[subject_code]['맞틀리스트'].append('맞')

                profit_tic = (data[subject_code]['이전반전시SAR값'][-2] - next_sar)/subject.info[subject_code]['단위']
                profit_tic = round(profit_tic, 1)
                subject.info[subject_code]['수익리스트'].append(profit_tic)

                
            else:

                profit_tic = (data[subject_code]['이전반전시SAR값'][-2] - next_sar) / subject.info[subject_code]['단위']
                profit_tic = round(profit_tic, 1)
                subject.info[subject_code]['수익리스트'].append(profit_tic)
                subject.info[subject_code]['맞틀리스트'].append('틀')

                #res.info(subject.info[subject_code]['맞틀리스트'])

            data[subject_code]['현재플로우최극가'] = float(data[subject_code]['고가'][-1])
            
            t_sar = {}
            t_sar['시작값'] = ep            
            if data[subject_code]['idx'] > 1800:
                if len(data[subject_code]['SAR']) > 0:
                    data[subject_code]['SAR'][-1]['끝값'] = subject.info[subject_code]['sar']
                data[subject_code]['SAR'].append(t_sar)

            #res.info('반전되었음, 하향->상향, 시간 : ' + str(data[subject_code]['SAR반전시간'][-1]) + ', 고가: ' + str(data[subject_code]['고가'][index]) + ' / sar: ' + str(next_sar))
            if subject.info[subject_code]['상태'] == '중립대기' or subject.info[subject_code]['상태'] == '매매완료' or subject.info[subject_code]['상태'] == '매도대기':
                log.info('상태 변경, 매매완료 -> 매수가능')
                print('상태 변경, 매매완료 -> 매수가능')
                subject.info[subject_code]['상태'] = '매수가능'
                
            print(subject.info[subject_code]['맞틀리스트'])
            print(subject.info[subject_code]['수익리스트'])

                
            
       
    
    next_sar = today_sar + af * (max(the_highest_price,the_lowest_price) - today_sar)

    #res.info("고가:"+str(data[subject_code]['고가'][index])+" ,저가" + str(data[subject_code]['저가'][index]))
    #res.info("af:"+str(af))
    #res.info("ep:"+str(ep))
    #res.info("flow:"+str(temp_flow))
    #res.info("sar:%s" % str(next_sar))
    #res.debug("반전시간 리스트:%s" % str(data[subject_code]['SAR반전시간']))
    #res.info("---------------")
    
    subject.info[subject_code]['sar'] = next_sar
    subject.info[subject_code]['ep'] = ep
    subject.info[subject_code]['af'] = af
    flow = subject.info[subject_code]['flow'] = temp_flow
    data[subject_code]['플로우'].append(temp_flow)
    
    