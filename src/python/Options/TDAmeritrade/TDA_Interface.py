import json

import requests

from TDAmeritrade.OptionData import OptionData


def call_tda(url, params):
    try:
        page = requests.get(url=url, params=params)
        content = json.loads(page.content)
    except:
        content = ""
    return content


def get_tda_list(url, params, min_dte, max_dte, min_oi, min_vol, min_price, max_iv, opt_type):
    ret = []
    ul = float(0.0)
    opt = call_tda(url, params)

    if len(opt) > 0:

        ul = float(opt['underlyingPrice'])

        if opt_type == "CALL":
            data = opt['callExpDateMap']
        else:
            data = opt['putExpDateMap']

        for expdate in data.keys():
            for strike in data[expdate].keys():
                for option in data[expdate][strike]:
                    jd = OptionData(option, ul)
                    if jd.valid:
                        if jd.oi >= min_oi:
                            if jd.volume >= min_vol:
                                if jd.mark >= min_price:
                                    if jd.volatility <= max_iv:
                                        if (jd.daysToExpiration >= min_dte) and (jd.daysToExpiration <= max_dte):
                                            if jd.mark > 0.0:
                                                ret.append(jd)
    return ul, ret


def print_opt_list(data):
    for d in data:
        print(d)
