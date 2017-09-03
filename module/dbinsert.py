# -*- coding: utf-8 -*-
import sys, time, os, shutil
import gmail, log, calc, santa, screen, db
import json
import dbsubject, contract
import pymysql

from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtWidgets import QApplication


class api():
    app = None
    recent_price = {}
    recent_candle_time = {}
    recent_request_candle_time = 0
    price_changed_cnt = 0
    account = ""
    cnt = 0
    data = []
    start_date = ''
    recent_date = None
    
    def __init__(self):
        super(api, self).__init__()
        self.app = QApplication(sys.argv)

        self.ocx = QAxWidget("KFOPENAPI.KFOpenAPICtrl.1")
        self.ocx.OnEventConnect[int].connect(self.OnEventConnect)
        self.ocx.OnReceiveTrData[str, str, str, str, str].connect(self.OnReceiveTrData)
        self.ocx.OnReceiveChejanData[str, int, str].connect(self.OnReceiveChejanData)
        self.ocx.OnReceiveRealData[str, str, str].connect(self.OnReceiveRealData)
        
        print("데이터를 읽어올 시작일을 입력하세요. ex)20170125")
        self.start_date = input()
        print(self.start_date)
        if self.connect() == 0:
            self.app.exec_()


    ####################################################
    # Interface Methods
    ####################################################

    def connect(self):
        """
        로그인 윈도우를 실행한다.
        로그인이 성공하거나 실패하는 경우 OnEventConnect 이벤트가 발생하고 이벤트의 인자 값으로 로그인 성공 여부를 알 수 있다.

        :return: 0 - 성공, 음수값은 실패
        """

        if self.ocx.dynamicCall("GetConnectState()") == 0:
            rtn = self.ocx.dynamicCall("CommConnect(1)")
            if rtn == 0:
                print("연결 성공")
            else:
                print("연결 실패")

            return rtn

    def get_login_info(self, sTag):
        """
        로그인한 사용자 정보를 반환한다.

        :param sTag: 사용자 정보 구분 TAG값
            “ACCOUNT_CNT” ? 전체 계좌 개수를 반환한다.
            "ACCNO" ? 전체 계좌를 반환한다. 계좌별 구분은 ‘;’이다.
            “USER_ID” - 사용자 ID를 반환한다.
            “USER_NAME” ? 사용자명을 반환한다.
            “KEY_BSECGB” ? 키보드보안 해지여부. 0:정상, 1:해지
            “FIREW_SECGB” ? 방화벽 설정 여부. 0:미설정, 1:설정, 2:해지
            Ex) openApi.GetLoginInfo(“ACCOUNT_CNT”);
        :return: TAG값에 따른 데이터 반환
        """
        return self.ocx.dynamicCall("GetLoginInfo(QString)", [sTag]).rstrip(';')
    
    #def get_dbinput_info(self):
    #    subject_code = dbsubject.info[]

    def get_dynamic_subject_info(self):
        self.get_dynamic_subject_code()
        self.get_dynamic_subject_market_time()
    
    def get_dynamic_subject_code(self):
        
        self.set_input_value("상품코드", '')
        self.comm_rq_data("상품별현재가조회", "opt10006", "", screen.S0010)
        
        '''
        lists = ['CMD','MTL','ENG','CUR','IDX']
        for list in lists:
            self.set_input_value("상품코드", list)
            self.comm_rq_data("상품별현재가조회", "opt10006", "", screen.S0010)
            time.sleep(1)
        '''
    def get_dynamic_subject_market_time(self):
        lists = ['MTL','ENG','CUR','IDX','CMD']
        for list in lists:
            self.set_input_value("품목구분", list)
            self.comm_rq_data("장운영정보조회", "opw50001", "", screen.S0011)
            time.sleep(0.5)
        

    def send_order(self, contract_type, subject_code, contract_cnt):
        
        """
        주식 주문을 서버로 전송한다.
        신규매수:self.send_order("신규매수","0101",my_account_number,1,subject_code,1,now_current_price,"","2","")
           

        신규매도:
        매수청산:
       매도청산:self.send_order("신규매수","0101",my_account_number,2,subject_code,subject_info[subject_code]['보유수량'],now_current_price,"2","")
       
 
        :param sRQName: 사용자 구분 요청 명
        :param sScreenNo: 화면번호[4]
        :param sAccNo: 계좌번호[10]
        :param nOrderType: 주문유형 (1:신규매수, 2:신규매도, 3:매수취소, 4:매도취소, 5:매수정정, 6:매 도정정)
        :param sCode: 주식종목코드
        :param nQty: 주문수량
        :param sPrice: 주문단가
        :param sStop: 스탑단가
        :param sHogaGb: 거래구분 1:시장가, 2:지정가, 3:STOP, 4:STOP LIMIT
            
            ※ 시장가, 최유리지정가, 최우선지정가, 시장가IOC, 최유리IOC, 시장가FOK, 최유리FOK, 장전시간외, 장후시간외 주문시 주문가격을 입력하지 않습니다.
            ex)
            지정가 매수 - openApi.SendOrder(“RQ_1”, “0101”, “5015123410”, 1, “000660”, 10, 48500, “00”, “”);
            시장가 매수 - openApi.SendOrder(“RQ_1”, “0101”, “5015123410”, 1, “000660”, 10, 0, “03”, “”);
            매수 정정 - openApi.SendOrder(“RQ_1”,“0101”, “5015123410”, 5, “000660”, 10, 49500, “00”, “1”);
            매수 취소 - openApi.SendOrder(“RQ_1”, “0101”, “5015123410”, 3, “000660”, 10, 0, “00”, “2”);
        :param sOrgOrderNo: 원주문번호
        :return: 에러코드 - parse_error_code
            -201     : 주문과부하 
            -300     : 주문입력값 오류
            -301     : 계좌비밀번호를 입력하십시오.
            -302     : 타인 계좌를 사용할 수 없습니다.
            -303     : 경고-주문수량 200개 초과
            -304     : 제한-주문수량 400개 초과

        """
        _contract_type = 0
        if contract_type == '신규매수':
            _contract_type = 2
        elif contract_type == '신규매도':
            _contract_type = 1
        else: return -300

        return self.ocx.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, QString, QString, QString, QString)",
                                    [contract_type, '0101', self.account, _contract_type, subject_code, contract_cnt, '0', '0', '1', ''])

    def request_tick_info(self, subject_code, tick_unit, prevNext):

        self.set_input_value("종목코드", subject_code)
        self.set_input_value("시간단위", tick_unit)
        '''
        temp = prevNext
        if prevNext != "":
            tmp_num = temp.split()[2]
            a = tmp_num[0:len(tmp_num)-6]
            tmp_num.replace(a, "")
            if int(a) <= 1756800000 and ' 09 ' in temp:
                temp = temp.replace(' 09 ', ' 00 ')
                temp = temp.replace('F0','EE')
            '''
        rtn = self.comm_rq_data("해외선물옵션틱그래프조회","opc10001", prevNext, dbsubject.info[subject_code]['화면번호'])

        if rtn != 0:
            # 에러코드별 로그
            log.error(self.parse_error_code(rtn))
            
        while rtn == -200:
            time.sleep(0.05)
            rtn = self.comm_rq_data("해외선물옵션틱그래프조회","opc10001", prevNext, dbsubject.info[subject_code]['화면번호'])
        

    def set_input_value(self, sID, sValue):
        """
        Tran 입력 값을 서버통신 전에 입력한다.

        :param sID: 아이템명
        :param sValue: 입력 값
        Ex) openApi.SetInputValue(“종목코드”, “000660”);
            openApi.SetInputValue(“계좌번호”, “5015123401”);
        """
        self.ocx.dynamicCall("SetInputValue(QString, QString)", sID, sValue)

    def comm_rq_data(self, sRQName, sTrCode, nPrevNext, sScreenNo):
        """
        Tran을 서버로 송신한다.

        :param sRQName: 사용자구분 명
        :param sTrCode: Tran명 입력
        :param nPrevNext: 0:조회, 2:연속
        :param sScreenNo: 4자리의 화면번호
        Ex) openApi.CommRqData( “RQ_1”, “OPT00001”, 0, “0101”);
        :return:
        OP_ERR_SISE_OVERFLOW – 과도한 시세조회로 인한 통신불가
        OP_ERR_RQ_STRUCT_FAIL – 입력 구조체 생성 실패
        OP_ERR_RQ_STRING_FAIL – 요청전문 작성 실패
        OP_ERR_NONE(0) – 정상처리
        """
        return self.ocx.dynamicCall("CommRqData(QString, QString, QString, QString)", sRQName, sTrCode, nPrevNext, sScreenNo)

    def quit(self):
        """ Quit the server """

        QApplication.quit()
        sys.exit()  

    ####################################################
    # Control Event Handlers
    ####################################################

    def OnReceiveTrData(self, sScrNo, sRQName, sTrCode, sRecordName, sPreNext):
        """
        Tran 수신시 이벤트
        서버통신 후 데이터를 받은 시점을 알려준다.

        :param py: 화면번호
        :param sRQName: 사용자구분 명
        :param sTrCode: Tran 명
        :param sRecordName: Record 명
        :param sPreNext: 연속조회 유무
        :param nDataLength: 1.0.0.1 버전 이후 사용하지 않음.
        :param sErrorCode: 1.0.0.1 버전 이후 사용하지 않음.
        :param sMessage: 1.0.0.1 버전 이후 사용하지 않음.
        :param sSplmMsg: 1.0.0.1 버전 이후 사용하지 않음.
        """
        
        price = {}
        now_time = time.localtime()
        today_time = "%04d%02d%02d" % (now_time.tm_year, now_time.tm_mon, now_time.tm_mday)
        
        if sRQName == "해외선물옵션틱그래프조회":
            subject_codes = list(dbsubject.info.keys())
            subject_code=subject_codes[0]
            print(subject_code)
            print(dbsubject.info[subject_code]['화면번호'])
            print(sScrNo)
            if sScrNo == dbsubject.info[subject_code]['화면번호']:                    
                # 초기 데이터 수신
                log.info('sTrCode' + sTrCode)
                log.info('sRecordName' + sRecordName)
                _data = self.ocx.dynamicCall("GetCommFullData(QString, QString, int)", sTrCode, sRecordName, 0)
                _data = _data.split()
                
                if self.recent_date == None:
                    self.recent_date = _data[6]

                if int(self.recent_date) < int(_data[6]):
                    # 입력한 날꺼까지 다 데이터를 받아오고나서 하는것!!(2주치 받을때만 사용되어짐)
                    log.info('self.recent_date' + self.recent_date)
                    log.info('영업일자 : ' + str(_data[6]))
                    self.data.reverse()
                    log.debug(self.start_date)
                    db.insert(self.data, self.start_date, subject_code)
                    time.sleep(5)
                    del dbsubject.info[subject_code]
                    del subject_codes[0]
                    self.data=[]
                    _data=[]
                    self.recent_date=None
                    if len(subject_codes)>0:
                        subject_code=subject_codes[0]
                        self.request_tick_info(subject_code,1, "")
                    else :
                        quit()

#                 print('today_time',today_time)
                if int(_data[6]) <= int (today_time):
                    self.recent_date = str(_data[6])
                    self.data.extend(_data)
                    #self.data.append(_data)
                
                log.info("recent date is " + _data[6])    
                log.info('체결시간 : int(_data[2])   ' + _data[2])
                log.info('현재가 : ' + _data[0])
                log.info('self.data.__len__()' + str(len(self.data)))
                
                if int(_data[2][:12]) < int(self.start_date + dbsubject.info[subject_code]['시작시간']):
                    # 입력한 날꺼까지 다 데이터를 받아오고나서 하는것!!
                    log.info('엽업일자입니당 : ' + str(_data[6]))
                    self.data.reverse()
                    log.debug(self.start_date)
                    db.insert(self.data, self.start_date, subject_code)
                    #time.sleep(5)
                    del dbsubject.info[subject_code]
                    del subject_codes[0]
                    self.data=[]
                    _data=[]
                    self.recent_date=None
                    if len(subject_codes)>0:
                        subject_code=subject_codes[0]
                        self.request_tick_info(subject_code,1, "")
                    else :
                        quit()

                else:
                    time.sleep(0.2)
                    self.request_tick_info(subject_code,1, sPreNext)   
            '''
            for subject_code in dbsubject.info.keys():
                if sScrNo == dbsubject.info[subject_code]['화면번호']:                    
                    # 초기 데이터 수신
                    _data = self.ocx.dynamicCall("GetCommFullData(QString, QString, int)", sTrCode, sRecordName, 0)
                    _data = _data.split()
                    
                    if self.recent_date == None:
                        self.recent_date = _data[6]

                    if int(self.recent_date) < int(_data[6]):
                        # 입력한 날꺼까지 다 데이터를 받아오고나서 하는것!!(2주치 받을때만 사용되어짐)
                        log.info('self.recent_date' + self.recent_date)
                        log.info('영업일자 : ' + str(_data[6]))
                        self.data.reverse()
                        log.debug(self.start_date)
                        db.insert(self.data, self.start_date, subject_code)
                        break
#                     print('today_time',today_time)
                    if int(_data[6]) <= int (today_time):
                        self.recent_date = str(_data[6])
                        self.data.extend(_data)
                        #self.data.append(_data)
                
                    #log.info("recent date is " + _data[6])    
                    #log.info('체결시간 : int(_data[2])   ' + _data[2])
                    #log.info('현재가 : ' + _data[0])
                    #log.info('self.data.__len__()' + str(len(self.data)))
                
                    if int(_data[2][:12]) < int(self.start_date + dbsubject.info[subject_code]['시작시간']):
                        # 입력한 날꺼까지 다 데이터를 받아오고나서 하는것!!
                        log.info('엽업일자입니당 : ' + str(_data[6]))
                        self.data.reverse()
                        log.debug(self.start_date)
                        db.insert(self.data, self.start_date, subject_code)
                        break
                    else:
                        time.sleep(0.2)
                        self.request_tick_info(subject_code,1, sPreNext)    
                '''          
                
        if sRQName == '상품별현재가조회':
            
            for i in range(68):
                
                subject_code = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRecordName, i, '종목코드n').strip() #현재가 = 틱의 종가
                if subject_code ==None:
                    break

                subject_symbol = subject_code[:2] 
                if subject_symbol in dbsubject.info.keys():
                    log.info("금일 %s의 종목코드는 %s 입니다." % (dbsubject.info[subject_symbol]["종목명"],subject_code))
                    dbsubject.info[subject_code] = dbsubject.info[subject_symbol]
                    del dbsubject.info[subject_symbol]
                    #print('초기초기 지워지워 ', dbsubject.info.keys())
                    #print(subject_code)
                    #self.request_tick_info(subject_code,1, "")
                    #self.recent_request_candle_time = time.time()
     
            #print(dbsubject.info.keys())
            subject_codes = list(dbsubject.info.keys())
            print(subject_codes)
            print(subject_codes[0])
            self.request_tick_info(subject_codes[0],1, "")        
            # 초기 데이터 요청
            #리스트로 subject_code 가져와서 이걸 1개씩 던진다!! 
            #포문안되는게 해외선물 거기서 돈다... 따라서 저기 break하면서 나올때 리스트 된거 하나씩날리는 함수만들어서 진행!
            #self.request_tick_info(subject_code,1, "")
            #self.recent_request_candle_time = time.time()
        
        if sRQName == "장운영정보조회":
            
            log.info("장운영정보조회")
            for i in range(20):
                subject_code = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRecordName, i, '파생품목코드')
                market_time1 = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRecordName, i, '장운영시간1')
                market_time2 = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRecordName, i, '장운영시간2')
                market_time3 = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRecordName, i, '장운영시간3')
                market_time4 = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRecordName, i, '장운영시간4')
                
                log.info(subject_code)
                log.info(market_time1)
                log.info(market_time2)
                log.info(market_time3)
                log.info(market_time4)
            
    def OnReceiveRealData(self, sSubjectCode, sRealType, sRealData):
        """
        실시간 시세 이벤트
        실시간데이터를 받은 시점을 알려준다.

        :param sSubjectCode: 종목코드
        :param sRealType: 리얼타입
        :param sRealData: 실시간 데이터전문
        """
        # 캔들 생기는 시점 확인해서 가격이 안바뀌어도 옥수수에 3틱으로 설정할 경우 가격변동없이 캔들이 생기는 경우가 있으니 request_tick_info 시점 확인
        
        #log.debug("OnReceiveRealData entered.")
        if sSubjectCode[:2] not in dbsubject.info.keys(): #정의 하지 않은 종목이 실시간 데이터 들어오는 경우 실시간 해제
            self.ocx.dynamicCall("DisconnectRealData(QString)", screen.S0010)
            self.ocx.dynamicCall("DisconnectRealData(QString)", screen.S0011)
            
        pass
        

    def OnReceiveChejanData(self, sGubun, nItemCnt, sFidList):
        """
        체결데이터를 받은 시점을 알려준다.

        :param sGubun: 체결구분 - 0:주문체결통보, 1:잔고통보, 3:특이신호
        :param nItemCnt: 아이템갯수
        :param sFidList: 데이터리스트 - 데이터 구분은 ‘;’ 이다.
        """
        pass

    def OnEventConnect(self, nErrCode):
        """
        통신 연결 상태 변경시 이벤트

        :param nErrCode: 에러 코드 - 0이면 로그인 성공, 음수면 실패, 에러코드 참조
        """
        print("OnEventConnect received")
        
        if nErrCode == 0:
            print("로그인 성공")
            # 계좌번호 저장
            self.account = self.get_login_info("ACCNO")
            log.info("계좌번호 : " + self.account)
            
            # 다이나믹 종목 정보 요청
            #self.get_dynamic_subject_info()
            self.get_dynamic_subject_code()

            # 초기 데이터 요청
            #self.request_tick_info('CLH17', dbsubject.info['CLH17']['시간단위'], "")
            #self.request_tick_info('GCG17', dbsubject.info['GCG17']['시간단위'], "")
            
            # 종목 정보 로그 찍기
            #log.info("참여 종목 : %s" % dbsubject.info.values())


        else:
            c_time = "%02d%02d" % (time.localtime().tm_hour, time.localtime().tm_min)

            # 로그인 실패 로그 표시 및 에러코드별 에러내용 발송
            err_msg = "에러코드별 메시지"
            log.critical(err_msg)

            if int(c_time) >= 800 or int(c_time) < 700:
                # 메일 발송
                gmail.send_email('[긴급' + str(c_time) + '] 해동이 작동 중지', '에러코드')

                # 자동이 재시작 로직 작성
                pass

            self.quit()

    ####################################################
    # Custom Methods
    ####################################################

    @staticmethod
    def parse_error_code(err_code):
        """
        Return the message of error codes

        :param err_code: Error Code
        :type err_code: str
        :return: Error Message
        """
        err_code = str(err_code)
        ht = {
            "0": "정상처리",
            "-100": "사용자정보교환에 실패하였습니다. 잠시후 다시 시작하여 주십시오.",
            "-101": "서버 접속 실패",
            "-102": "버전처리가 실패하였습니다.",
            "-200": "시세조회 과부하",
            "-201": "REQUEST_INPUT_st Failed",
            "-202": "요청 전문 작성 실패",
            "-300": "주문 입력값 오류",
            "-301": "계좌비밀번호를 입력하십시오.",
            "-302": "타인계좌는 사용할 수 없습니다.",
            "-303": "주문가격이 20억원을 초과합니다.",
            "-304": "주문가격은 50억원을 초과할 수 없습니다.",
            "-305": "주문수량이 총발행주수의 1%를 초과합니다.",
            "-306": "주문수량은 총발행주수의 3%를 초과할 수 없습니다."
        }
        return ht[err_code] + " (%s)" % err_code if err_code in ht else err_code

    def get_today_date(self):
        ret = ''
        ret += str(time.localtime().tm_year)
        if time.localtime().tm_mon < 10:
            ret += '0'
        ret += str(time.localtime().tm_mon)
        if time.localtime().tm_mday < 10:
            ret += '0'
        ret += str(time.localtime().tm_mday)

        return ret

    def get_start_time(self, subject_code):
        start_time = int(dbsubject.info[subject_code]['시작시간'])
        end_time = int(dbsubject.info[subject_code]['마감시간'])
        current_hour = time.localtime().tm_hour
        current_min = time.localtime().tm_min
        current_time = current_hour*100 + current_min
        return_time = ''
        if current_time < end_time:
            yesterday = time.localtime(time.time() - 86400)
            mon = yesterday.tm_mon
            if mon < 10:
                mon = '0' + str(mon)
            day = yesterday.tm_mday
            if day < 10:
                day = '0' + str(day)
            return_time = str(yesterday.tm_year) + str(mon) + str(day) + dbsubject.info[subject_code]['시작시간'] + '00'
        elif current_time >= start_time:
            today = time.localtime()
            mon = today.tm_mon
            if mon < 10:
                mon = '0' + str(mon)
            day = today.tm_mday
            if day < 10:
                day = '0' + str(day)
            return_time = str(today.tm_year) + str(mon) + str(day) + dbsubject.info[subject_code]['시작시간'] + '00'

        return return_time