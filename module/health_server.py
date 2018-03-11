# -*- coding: utf8 -*-

# socket 과 select 모듈 임포트
import socketserver
import threading
import time
import sys

HEALTH_PORT = 56789
BUFF_SIZE = 1024


class ClientHandler(socketserver.BaseRequestHandler):

    def handle(self):
        sock = self.request
        recv_buff = sock.recv(BUFF_SIZE)
        recv_message = str(recv_buff, encoding="utf-8")

        # Echo
        sock.send(recv_buff)
        print("Echo(" + recv_message + ") from Health checker(" + self.client_address[0] + ")", end = "\r")
        time.sleep(1)
        sock.close()


class HealthConnectManager(threading.Thread):
    server = None

    def __init__(self):
        super(HealthConnectManager, self).__init__()
        threading.Thread.__init__(self)
        self.bind_ip = ''
        self.bind_port = HEALTH_PORT
        self.server = None

    def run(self):

        try:
            self.server = socketserver.TCPServer((self.bind_ip, self.bind_port), ClientHandler)
            print("Start health connection thr! Waiting client from port #" + str(self.bind_port))
            poll_interval = 1
            self.server.serve_forever(poll_interval)


        except Exception as err:
            print("Exception ({0})".format(err))
            sys.exit(-1)

    def get_name(self):
        return str(self.__class__.__name__)

    def print_status(self):
        print(self.__getattribute__())

    def server_close(self):
        if self.server is not None:
            self.server.shutdown()
            #sys.exit()

if __name__ == '__main__':
    # Example code
    server_thr = HealthConnectManager()

    # Single thread mode --> 다음 함수에서 Blocking 됨
    server_thr.run()

    # Multi thread mode --> Main thread 와 동시에 동작
    # server_thr.start()

    while True:
        print("Main thread is alive!")
        time.sleep(60)
