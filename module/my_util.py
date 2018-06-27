# -*- coding: utf-8 -*-
import subject, calc
import datetime, time
import define as d


def get_date_string_from_date_int(date):
    date = str(date)
    return date[4:6] + '-' + date[6:8] + ' ' + date[8:10] + ':' + date[10:12]


def get_start_index_of_trend(subject_code):
    start_index = calc.data[subject_code]['idx'] - calc.data[subject_code]['정배열연속틱'] + 1

    if start_index <= 0:
        return 0

    past_trend = calc.data[subject_code]['추세'][start_index - 1]
    current_trend = calc.data[subject_code]['추세'][-1]

    max = 0.0
    min = 99999.99
    point = start_index
    for idx in range(start_index - 1, 0, -1):
        if calc.data[subject_code]['추세'][idx] == None or calc.data[subject_code]['추세'][idx] != past_trend:
            break

        if current_trend == '상승세':
            if calc.data[subject_code]['현재가'][idx] < min:
                min = calc.data[subject_code]['현재가'][idx]
                point = idx
        elif current_trend == '하락세':
            if calc.data[subject_code]['현재가'][idx] > max:
                max = calc.data[subject_code]['현재가'][idx]
                point = idx

    return point


def chanege_past_trend(subject_code):
    start_index = calc.data[subject_code]['idx'] - calc.data[subject_code]['정배열연속틱'] + 1

    for idx in range(start_index - 1, 0, -1):
        if calc.data[subject_code]['추세'][idx] == None or calc.data[subject_code]['추세'][idx] == \
                calc.data[subject_code]['추세'][-1]:
            break
        calc.data[subject_code]['추세'][idx] = calc.data[subject_code]['추세'][-1]


def get_trend_continuous_tick_count(subject_code):
    return calc.data[subject_code]['idx'] - get_start_index_of_trend(subject_code) + 1


def get_trend_range(subject_code):
    current_index = calc.data[subject_code]['idx']
    rt = 9999999
    rt_idx = current_index
    if calc.data[subject_code]['플로우'][current_index] == '하향': rt = -9999999

    cnt = 0
    for idx in range(current_index, 0, -1):
        if calc.data[subject_code]['플로우'][current_index] != calc.data[subject_code]['플로우'][idx]:
            current_idx = idx
            break
        cnt += 1

    for idx in range(current_index, 0, -1):
        cnt += 1
        if calc.data[subject_code]['플로우'][current_index] == '하향':
            if (calc.data[subject_code]['플로우'][idx] == '상향') or idx == 0: break
            if rt < calc.data[subject_code]['저가'][idx]:
                rt = calc.data[subject_code]['저가'][idx]
                rt_idx = idx
        elif calc.data[subject_code]['플로우'][current_index] == '상향':
            if (calc.data[subject_code]['플로우'][idx] == '하향') or idx == 0: break
            if rt > calc.data[subject_code]['고가'][idx]:
                rt = calc.data[subject_code]['고가'][idx]
                rt_idx = idx
    return calc.data[subject_code]['idx'] - rt_idx + 1


def get_time(add_min):
    # 현재 시간 정수형으로 return
    current_hour = time.localtime().tm_hour
    current_min = time.localtime().tm_min
    current_min += add_min
    if current_min >= 60:
        current_hour += 1
        current_min -= 60

    current_time = current_hour * 100 + current_min

    return current_time


def is_end_time(add_min, subject_code):
    if d.get_mode() is d.REAL:
        if get_time(0) < int(subject.info[subject_code]['마감시간']) and get_time(add_min) >= int(
                subject.info[subject_code]['마감시간']):
            return True
    elif d.get_mode() is d.TEST:
        _time = str(calc.data[subject_code]['체결시간'][-1])
        current_hour = int(_time[-6:-4])
        current_min = int(_time[-4:-2])
        after_hour = current_hour
        after_min = current_min + add_min
        if after_min >= 60:
            after_hour += 1
            after_min -= 60

        current = current_hour * 100 + current_min
        after = after_hour * 100 + after_min

        if current < int(subject.info[subject_code]['마감시간']) and after >= int(subject.info[subject_code]['마감시간']):
            return True

    return False


def is_holiday(subject_code):
    if d.get_mode() is d.REAL:
        weekno = datetime.datetime.today().weekday()
        if weekno < 5:
            return False
        else:
            current_time = get_time(0)
            if current_time >= 0 and current_time <= 700:
                weekno -= 1

            if weekno < 5: return False

        return True
    elif d.get_mode() is d.TEST:
        _time = str(calc.data[subject_code]['체결시간'][-1])
        today = datetime.date(int(_time[:4]), int(_time[4:6]), int(_time[6:8]))
        weekno = datetime.datetime.weekday(today)
        if weekno < 5:
            return False
        else:
            current_time = get_time(0)
            if current_time >= 0 and current_time <= 700:
                weekno -= 1

            if weekno < 5: return False

        return True
    return False


def is_trade_time(subject_code):
    if d.get_mode() is d.TEST: return True
    if d.get_mode() is d.TEST and calc.data[subject_code]['idx'] < 10:
        return True
    if is_end_time(3, subject_code) is False or is_holiday(subject_code) is False:
        return True
    return False


def is_sorted(subject_code):
    org_lst = []
    for days in subject.info[subject_code]['이동평균선']:
        org_lst.append(calc.data[subject_code]['이동평균선'][days][-1])

    sort_lst = org_lst[:]
    sort_lst.sort()
    reverse_lst = sort_lst[:]
    reverse_lst.reverse()

    if sort_lst == org_lst:
        return '하락세'
    elif reverse_lst == org_lst:
        return '상승세'
    else:
        return '모름'


def is_sorted_previous(subject_code, passed_candle_count=-2):
    org_lst = []
    for days in subject.info[subject_code]['이동평균선']:
        org_lst.append(calc.data[subject_code]['이동평균선'][days][passed_candle_count])

    sort_lst = org_lst[:]
    sort_lst.sort()
    reverse_lst = sort_lst[:]
    reverse_lst.reverse()

    if sort_lst == org_lst:
        return '하락세'
    elif reverse_lst == org_lst:
        return '상승세'
    else:
        return '모름'


def get_today_date():
    today = datetime.date.today()
    year = str(today.year)
    month = str(today.month)
    if len(month) == 1: month = '0' + month

    day = str(today.day)
    if len(day) == 1: day = '0' + day

    return year + month + day