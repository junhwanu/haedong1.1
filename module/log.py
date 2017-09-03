# -*- coding: utf-8 -*-
import shutil, time, sys, os
import logging
import define as d

logger = None

def init(path):
    global logger

    path = path + '/logs/'
    now = time.localtime()
    today = "%04d%02d%02d" % (now.tm_year, now.tm_mon, now.tm_mday)

    log_file = path + "/" +today+"_log.txt"

    if not os.path.exists(path):
        os.makedirs(path)

    if os.path.isfile(log_file) == False:
        file = open(log_file, 'w')
        file.close()
            
    logger = logging.getLogger('mylogger')
    fomatter = logging.Formatter('[%(levelname)s:%(lineno)s] %(asctime)s > %(message)s')

    fileHandler = logging.FileHandler(log_file, encoding='utf-8')
    streamHandler = logging.StreamHandler()

    fileHandler.setFormatter(fomatter)
    streamHandler.setFormatter(fomatter)

    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)
    logger.setLevel(logging.INFO)

def info(log_msg):
    logger.info(log_msg)

def debug(log_msg):
    logger.debug(log_msg)
    
def warning(log_msg):
    logger.warning(log_msg)

def error(log_msg):
    logger.error(log_msg)

def critical(log_msg):
    logger.critical(log_msg)
