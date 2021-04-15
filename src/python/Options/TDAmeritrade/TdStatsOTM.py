from TDAmeritrade.OptionData import OptionData
from TDAmeritrade import td_api_key
from TDAmeritrade.Statistics import Statistics
from TDAmeritrade.TDA_Interface import call_tda
from TDAmeritrade.TdProcess import get_avg_iv, get_realvol

totalPuts = 0
totalCalls = 0
valuePuts = 0.0
valueCalls = 0.0


def valid_strike(stk, low, high):
    ret = False
    if stk < low:
        ret = True
    elif stk > high:
        ret = True
    return ret


def valid_put_strike(stk, low):
    ret = False
    if stk < low:
        ret = True
    return ret


def valid_call_strike(stk, high):
    ret = False
    if stk > high:
        ret = True
    return ret


def process(data, opts, ulp):
    stklow = ulp * 0.90
    stkhigh = ulp * 1.10
    for expdate in data.keys():
        for strike in data[expdate].keys():
            for option in data[expdate][strike]:
                jd = OptionData(option)
                if jd.valid:
                    if jd.oi > 0:
                        if jd.mark > 0.0:
                            if jd.daysToExpiration > 0:
                                if jd.type == "PUT":
                                    if valid_put_strike(jd.strike, stklow):
                                        opts.totalPutsOi += jd.oi
                                        opts.totalPutsVol += jd.volume
                                        opts.dollarPutsOi += float(jd.oi) * float(jd.last)
                                        opts.dollarPutsVol += float(jd.volume) * float(jd.last)
                                elif jd.type == "CALL":
                                    if valid_call_strike(jd.strike, stkhigh):
                                        opts.totalCallsOi += jd.oi
                                        opts.totalCallsVol += jd.volume
                                        opts.dollarCallsOi += float(jd.oi) * float(jd.last)
                                        opts.dollarCallsVol += float(jd.volume) * float(jd.last)


def is_success(cnt):
    ret = False
    try:
        if cnt['status'] == "SUCCESS":
            ret = True
    finally:
        return ret


def process_code(cod):
    p = dict(apikey=td_api_key, symbol=cod)
    content = call_tda(url, p)

    if is_success(content):
        print("Processing : ", cod)

        ul = float(content['underlyingPrice'])

        sts = Statistics(cod)

        process(content['callExpDateMap'], sts, ul)
        process(content['putExpDateMap'], sts, ul)

        sts.calliv = get_avg_iv(content['callExpDateMap'], ul, False)
        sts.putiv = get_avg_iv(content['putExpDateMap'], ul, False)
        sts.realvol = get_realvol(cod, 22)
        if sts.realvol > 0.0:
            sts.putpremium = ((sts.putiv / sts.realvol) - 1.0) * 100.0
            sts.callpremium = ((sts.calliv / sts.realvol) - 1.0) * 100.0

        totstats.code += " " + cod

        totstats.totalPutsVol += sts.totalPutsVol
        totstats.totalCallsVol += sts.totalCallsVol
        totstats.totalPutsOi += sts.totalPutsOi
        totstats.totalCallsOi += sts.totalCallsOi

        totstats.dollarPutsVol += sts.dollarPutsVol
        totstats.dollarCallsVol += sts.dollarCallsVol
        totstats.dollarPutsOi += sts.dollarPutsOi
        totstats.dollarCallsOi += sts.dollarCallsOi

        sts.calc()
        statlist.append(sts)

    else:
        print("Bad code : ", cod)


if __name__ == '__main__':

    main_codes = ['XLB', 'XLC', 'XLE', 'XLF', 'XLI', 'XLK', 'XLP', 'XLU', 'XLV', 'XLY', 'XHB', 'XRT', 'SMH',
                  'IBB', 'IWM', 'DIA', 'QQQ', 'SPY']

    misc_codes = ['TLT', 'SLV', 'GLD']

    test_codes = ['QQQ', 'SPY']

    url = r"https://api.tdameritrade.com/v1/marketdata/chains"

    statlist = []
    totstats = Statistics("Combined")

    for code in main_codes:
        process_code(code)

    totstats.calc()
    print(totstats)

    with open("out/tdstats.txt", 'w') as fp:
        for stats in statlist:
            fp.write("{}\n".format(stats))
        fp.write("\n{}\n".format(totstats))
