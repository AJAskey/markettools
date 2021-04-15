import math
from datetime import date, datetime, timedelta

from TDAmeritrade import td_api_key
from TDAmeritrade.OptionData import OptionData
from TDAmeritrade.TDA_Interface import call_tda
from Utilities import datetime_to_str


def process_putcall_data(data, opts, u):
    """
    Procedure process_putcall_data sums up option volume and open interest.
    :param data: JSON data from TDAmeritrade representing either puts or calls of one symbol.
    :param opts: Data structure of option 'Statistics' to be accumulated.
    :param u: Price of the underlying stock for this symbol.
    """
    for expdate in data.keys():
        for strike in data[expdate].keys():
            for option in data[expdate][strike]:
                jd = OptionData(option, u)
                if jd.valid:
                    if jd.oi > 0:
                        if jd.mark > 0.0:
                            if jd.type == "PUT":
                                opts.totalPutsOi += jd.oi
                                opts.totalPutsVol += jd.volume
                                opts.dollarPutsOi += float(jd.oi) * float(jd.last)
                                opts.dollarPutsVol += float(jd.volume) * float(jd.last)
                            elif jd.type == "CALL":
                                opts.totalCallsOi += jd.oi
                                opts.totalCallsVol += jd.volume
                                opts.dollarCallsOi += float(jd.oi) * float(jd.last)
                                opts.dollarCallsVol += float(jd.volume) * float(jd.last)


def process(data, u):
    retlist = []
    for expdate in data.keys():
        for strike in data[expdate].keys():
            for option in data[expdate][strike]:
                jd = OptionData(option, u)
                if jd.valid:
                    retlist.append(jd)
    return retlist


def get_realvol(cod, td):
    tdscaler = 252.0 / float(td)

    today = datetime.now()
    dldays = -1 * ((td * 7 / 5) + 25)
    days = today + timedelta(days=dldays)
    stdate = int(days.timestamp() * 1000)

    urlPrice = r"https://api.tdameritrade.com/v1/marketdata/{}/pricehistory".format(cod)
    parm = dict(apikey=td_api_key, periodType='month', frequencyType='daily', startDate=stdate)
    jsondata = call_tda(urlPrice, parm)
    knt = len(jsondata)
    if knt < 1:
        print("get_realvol() with no return data for ", cod)
        return float(0.0)

    try:
        cnd = jsondata['candles']
        # print_json(cnd)

        knt = int(0)
        preval = float(0.0)
        summ = float(0.0)
        for val in reversed(cnd):
            close = float(val['close'])
            if knt > 0 and preval > 0.0:
                nlog = math.log(close / preval) ** 2
                summ += nlog
            knt += 1
            if knt > td:
                break
            preval = close
            # ms = val['datetime']
            # dt = datetime.fromtimestamp(ms / 1000)
            # print(dt, close, knt)

        num = summ * tdscaler
        rv = math.sqrt(num) * 100.0
    except:
        rv = float(0.0)

    return rv


def get_avg_iv(jsondata, underlying, debug):
    ivtot = float(0.0)
    knt = int(0)
    for expdate in jsondata.keys():
        for strike in jsondata[expdate].keys():
            for option in jsondata[expdate][strike]:
                opt = OptionData(option, underlying)
                if opt.valid:
                    if 6 < opt.daysToExpiration < 183:
                        if abs(opt.ul_pct) < 25.0:
                            if opt.volatility > 0.0:
                                ivtot += opt.volatility
                                knt += 1
                                if debug:
                                    print(option['symbol'], opt.volatility, ivtot, knt, opt.daysToExpiration)
    aiv = float(0.0)
    if knt > 0:
        aiv = ivtot / float(knt)
    return aiv


def buildstr(data):
    tmp = "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}{}".format(
        data.type, datetime_to_str(data.expiration),
        data.daysToExpiration, data.strike, data.oi, data.volume,
        data.last, data.bid, data.ask, data.mark, data.tvalue,
        data.volatility, data.delta, data.gamma, data.theta, data.vega, data.rho,
        datetime_to_str(data.tradeTime), data.premium,
        "\n")
    ret = tmp.replace("nan,", "0.0,")
    return ret


def get_ul_pct(opt, u):
    ulp = (float(opt.strike) / float(u) * 100.0) - 100.0
    return ulp


def header(file, cod, underlying):
    file.write("Type,Expiration,Days,Strike,OI,Volume,Last,Bid,Ask,Mark,TValue,")
    file.write("IV,Delta,Gamma,Theta,Vega,Rho,LastTrade,Premium,,")
    file.write(cod)
    file.write(",")
    file.write(str(underlying))
    file.write("\n")


if __name__ == '__main__':
    # code = 'SPY'

    etf_codes = ['XLB', 'XLE', 'XLF', 'XLI', 'XLK', 'XLP', 'XLU', 'XLV', 'XLY', 'SMH',
                 'IBB', 'IWM', 'DIA', 'QQQ', 'SPY']

    test_codes = ['SPY', 'QQQ', 'DIA']

    url = r"https://api.tdameritrade.com/v1/marketdata/chains"

    for code in test_codes:

        p = dict(apikey=td_api_key, symbol=code)
        content = call_tda(url, p)

        if content['status'] == "SUCCESS":

            ul = content['underlyingPrice']

            avgciv = get_avg_iv(content['callExpDateMap'], ul, False)
            avgpiv = get_avg_iv(content['putExpDateMap'], ul, False)
            rvol = get_realvol(code, 22)

            calls = process(content['callExpDateMap'], ul)
            puts = process(content['putExpDateMap'], ul)

            strToday = date.today().strftime("%Y%m%d")
            filename = "out/{c}-{d}.csv".format(c=code, d=strToday)
            print(filename)
            with open(filename, 'w') as fp:
                header(fp, code, ul)
                for c in calls:
                    if c.valid:
                        if c.mark > 0.099:
                            fp.write(buildstr(c))
                for p in puts:
                    if p.valid:
                        if p.mark > 0.099:
                            fp.write(buildstr(p))
