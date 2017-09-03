# -*- coding: utf-8 -*-

mode = None # 현재 모드
REAL = 1    # 실제 투자
TEST = 2    # 테스트 프로그램
DB = 3      # DB 수집

PRODUCT_CNT = 5 # ['MTL','ENG','CUR','IDX','CMD']
RECEIVED_PRODUCT_COUNT = 0 # 현재 받은 상품 정보들

def get_mode():
    return mode