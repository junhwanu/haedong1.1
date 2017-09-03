# -*- coding: utf-8 -*-
import log_result as res
import subject, calc
import math

def init(subject_code):
    if calc.data[subject_code]['현재가'][0] < calc.data[subject_code]['현재가'][1]:
        subject.info[subject_code]['flow'] = '상향'
        subject.info[subject_code]['ep'] = max(calc.data[subject_code]['고가'][0], calc.data[subject_code]['고가'][1])
        subject.info[subject_code]['sar'] = min(calc.data[subject_code]['저가'][0], calc.data[subject_code]['저가'][1])
    else:
        subject.info[subject_code]['flow'] = '하향'
        subject.info[subject_code]['ep'] = min(calc.data[subject_code]['저가'][0], calc.data[subject_code]['저가'][1])
        subject.info[subject_code]['sar'] = max(calc.data[subject_code]['고가'][0], calc.data[subject_code]['고가'][1])

def calculate(subject_code):
    init_af = subject.info[subject_code]['init_af']
    af = subject.info[subject_code]['af']
    max_af = subject.info[subject_code]['maxaf']
        
    '''
    # Difference of High and Low
    differences = []
    for idx in range(0, len(list['현재가'])):
        differences.append(list['고가'][idx] - list['저가'][idx])
    
    # STDEV of differences
    stDev = self.standard_deviation(list)
    sarArr = [None] * len(list['현재가'])

    # Find first non-NA value
    beg = 1;
    for idx in range(0, len(list['현재가'])):
        if list['고가'][idx] == 0 or list['저가'][idx] == 0:
            sarArr[idx] = 0
            beg += 1
        else:
            break
    '''        
    # Initialize values needed by the routine
    sig0 = subject.info[subject_code]['flow']
    sig1 = subject.info[subject_code]['flow']
    ep = subject.info[subject_code]['ep']
    prev_sar = subject.info[subject_code]['sar']
    
    # Local extreme
    lmin = min(calc.data[subject_code]['저가'][-2], calc.data[subject_code]['저가'][-1])
    lmax = max(calc.data[subject_code]['고가'][-2], calc.data[subject_code]['고가'][-1])

    #res.info('시가: ' + str(list['시가'][-1]) + ' 고가: ' + str(list['고가'][-1]) + ' 저가: ' + str(list['저가'][-1]) + ' 현재가: ' + str(list['현재가'][-1]))
    # Create signal and extreme price vectors
    if sig1 == '상향':
        # Previous buy signal
        new_sar = prev_sar + (ep - prev_sar) * af;

        if calc.data[subject_code]['저가'][-1] >= new_sar:
            sig0 = '상향'
        else:
            sig0 = '하향'    # New signal
            res.info('상향->하향 반전, list[저가][-1] = ' + str(calc.data[subject_code]['저가'][-1]) + ', sarArr[-1] = ' + str(new_sar))
            res.info('체결시간(' + str(calc.data[subject_code]['체결시간'][-1])[-6:-4] + ':' + str(calc.data[subject_code]['체결시간'][-1])[-4:-2] + ':' + str(calc.data[subject_code]['체결시간'][-1])[-2:] + ')')
        subject.info[subject_code]['ep'] = max(lmax, ep)  # New extreme price
        
    else:
        # Previous sell signal
        new_sar = prev_sar + (ep - prev_sar) * af;
        if calc.data[subject_code]['고가'][-1] < new_sar:
            sig0 = '하향'
        else:
            sig0 = '상향'   # New signal
            res.info('하향->상향 반전, list[고가][-1] = ' + str(calc.data[subject_code]['고가'][-1]) + ', sarArr[-1] = ' + str(new_sar))
            res.info('체결시간(' + str(calc.data[subject_code]['체결시간'][-1])[-6:-4] + ':' + str(calc.data[subject_code]['체결시간'][-1])[-4:-2] + ':' + str(calc.data[subject_code]['체결시간'][-1])[-2:] + ')')
        subject.info[subject_code]['ep'] = min(lmin, ep)  # New extreme price

    # Calculate acceleration factor (af) and stop-and-reverse (sar) vector
            
    # No signal change
    if sig0 == sig1:
        # Initial calculations 
        new_sar = prev_sar + (ep - prev_sar) * af;
        
        # Current buy signal 
        if sig0 == '상향':
            if subject.info[subject_code]['ep'] > ep:
                subject.info[subject_code]['af'] = min(max_af, af + init_af)

            if new_sar > lmin:
                new_sar = lmin  # Determine sar value
                    
        # Current sell signal
        else:
            if subject.info[subject_code]['ep'] < ep:
                subject.info[subject_code]['af'] = min(max_af, af + init_af)
                    
            if new_sar <= lmax:
                new_sar = lmax  # Determine sar value
            
    else: # New signal
        subject.info[subject_code]['af'] = subject.info[subject_code]['init_af']   # reset acceleration factor */
        subject.info[subject_code]['flow'] = sig0
        '''
        if sig0 == '상향':
            subject.info[subject_code]['ep'] = lmax
            new_sar = lmin
        else:
            subject.info[subject_code]['ep'] = lmin
            new_sar = lmax
        '''
        new_sar = subject.info[subject_code]['ep']  # set sar value
    
    res.info('캔들(' + str(calc.data[subject_code]['체결시간'][-1]) + '), SAR = ' + str(new_sar))
    #subject.info[subject_code]['sar'] = round(new_sar, subject.info[subject_code]['자릿수'])
    subject.info[subject_code]['sar'] = new_sar

def standard_deviation(self, list):
    M = 0.0
    S = 0.0
    k = 1
    for idx in range(len(list['현재가'])):
        value = list['현재가'][idx]
        tmpM = M
        M += (value - tmpM) / k
        S += (value - tmpM) * (value - M)
        k += 1

    return math.sqrt(S / (k-2))
