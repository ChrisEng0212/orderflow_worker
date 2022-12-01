import os
from celery import Celery
from celery.utils.log import get_task_logger
from time import sleep
import math
from pybit import inverse_perpetual

app = Celery('tasks', broker=os.getenv("CELERY_BROKER_URL"))
logger = get_task_logger(__name__)


@app.task
def add(x, y):
    logger.info(f'Adding {x} + {y}')
    return x + y

def handle_trade_message(msg):
    print(msg['data'])

def handle_info_message(msg):
    print(msg['data'])

@app.task
def bbws():

    openWhile =  'true'
    ws_inverseP = inverse_perpetual.WebSocket(
        test=False,
        ping_interval=30,  # the default is 30
        ping_timeout=10,  # the default is 10
        domain="bybit"  # the default is "bybit"
    )

    ws_inverseP.trade_stream(
        handle_trade_message, "BTCUSD"
    )

    ws_inverseP.instrument_info_stream(
        handle_info_message, "BTCUSD"
    )
    while openWhile == 'true':
        sleep(1)

    return True




