import os
import redis
import json

try:
    import config
    REDIS_URL = config.REDIS_URL
    r = redis.from_url(REDIS_URL, ssl_cert_reqs=None, decode_responses=True)
except:
    REDIS_URL = os.getenv('CELERY_BROKER_URL')
    r = redis.from_url(REDIS_URL, decode_responses=True)


def createCandle():

    newCandle = {
        'time' : 0,
        'timestamp' : '',
        'time_delta' : 0,
        'close' : 0,
        'open' : 0,
        'price_delta' : 0,
        'high' : 0,
        'low' : 0,
        'buys' : 0,
        'sells' : 0,
        'delta' : 0,
        'delta_cumulative' : 0,
        'total' : 0,
        'oi_cumulative': 0,
        'oi_delta': 0,
    }

    return newCandle



def getPVAStatus(newBlocks):

    last10vols = []

    for b in newBlocks:

        returnPVA = {
            'pva150' : False,
            'pva200' : False,
            'vol': 0,
            'percentage' : 0,
            'deltapercentage' : 0,
            'PVAbearDIV' : None,
            'PVAbullDIV' : None,
            'flatOI' : None
        }

        total = 0

        for v in last10vols:
            total += v

        average = total/10

        if len(last10vols) == 10:
            returnPVA['percentage'] = round((b['total']/average)*100)

            if b['total'] > average * 2:
                returnPVA['pva200'] = True

            elif b['total'] > average * 1.5:
                returnPVA['pva150'] = True

        if len(last10vols) == 10:
            last10vols.pop(0)

        last10vols.append(b['total'])

        b['pva_status'] = returnPVA

    return newBlocks


def getBlocks(size, blocksString):

    ## get all the timeblocks (5Min)
    blocks = json.loads(blocksString)

    print(len(blocks))

    # new list of candle blocks
    newList = []

    ## new candle of size
    newCandle = {}

    firstUnit = {}

    count = 1

    for unit in blocks:
        # print('count', count, unit)

        ## ADD fist unit
        if count == 1:
            newCandle = {}
            for y in unit:
                # create new candle key value pairs
                newCandle[y] = unit[y]
                firstUnit[y] = unit[y]

            count += 1

        ## add more units
        elif count < size:
            if unit['low'] < newCandle['low']:
                newCandle['low'] = unit['low']

            if unit['high'] > newCandle['high']:
                newCandle['high'] = unit['high']

            newCandle['buys'] += unit['buys']
            newCandle['sells'] += unit['sells']
            newCandle['delta'] += unit['buys'] - unit['sells']
            newCandle['total'] += unit['total']

            count += 1

        ## add last unit
        elif count == size:
            ## also update price and delta
            if unit['low'] < newCandle['low']:
                newCandle['low'] = unit['low']

            if unit['high'] > newCandle['high']:
                newCandle['high'] = unit['high']

            newCandle['buys'] += unit['buys']
            newCandle['sells'] += unit['sells']
            newCandle['delta'] += unit['buys'] - unit['sells']
            newCandle['total'] += unit['total']

            newCandle['close'] = unit['close']
            newCandle['price_delta'] = newCandle['close'] - newCandle['open']
            newCandle['oi_cumulative'] = unit['oi_cumulative']
            newCandle['oi_delta'] = newCandle['oi_cumulative'] - newCandle['oi_open']
            newCandle['time_delta'] = newCandle['trade_time_ms'] - unit['trade_time_ms']


            newList.append(newCandle)

            count = 1

    newBlocks = getPVAStatus(newList)


    print(len(newBlocks))
    return json.dumps(newBlocks)

# getVolumeBlock()
