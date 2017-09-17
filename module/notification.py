# -*- coding: utf-8 -*-
import telepot

TOKEN = '339704326:AAEXoMPlPLsuA5uMqdCUF-Wq5QMyKqNsgYo'

def sendMessage(msg, account):
    id_list = []
    if account == None:
        id_list.append(285446312) # ����
        id_list.append(330172669) # ����
        id_list.append(377943640) # ����
    elif account == '5107243872' or account == '7003919272':
        id_list.append(330172669) # ����
    elif account == '5105855972':
        id_list.append(285446312) # ����
    elif account =='5111539272':
        id_list.append(377943640) # ����

    if len(id_list) == 0: return

    bot = telepot.Bot(TOKEN)

    for id in id_list:
        bot.sendMessage(id, msg)
        
        
if __name__ == "__main__":
    sendMessage("테스트","5107243872")