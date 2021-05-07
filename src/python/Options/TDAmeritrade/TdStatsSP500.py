"""
This is a doc string.
"""
from datetime import datetime
import time

from TDAmeritrade import td_api_key
from TDAmeritrade.Statistics import Statistics
from TDAmeritrade.TDA_Interface import call_tda
from TDAmeritrade.TdProcess import get_avg_iv, get_realvol, process_putcall_data
from Utilities import build_list

totalPuts = 0
totalCalls = 0
valuePuts = 0.0
valueCalls = 0.0


def is_success(cnt):
    ret = False
    try:
        if cnt['status'] == "SUCCESS":
            ret = True
    finally:
        return ret


redo_list = []


def process_code(cod, redo):
    p = dict(apikey=td_api_key, symbol=cod)
    content = call_tda(url, p)

    if is_success(content):
        print("Processing : ", cod)

        ul = float(content['underlyingPrice'])

        sts = Statistics(cod)

        process_putcall_data(content['callExpDateMap'], sts, ul)
        process_putcall_data(content['putExpDateMap'], sts, ul)

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
        if redo:
            redo_list.append(cod)
            time.sleep(15.0)


if __name__ == '__main__':

    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S\n\n")

    main_codes = build_list("D:/dev/MarketTools - dev/lists/spx_components.csv")
    main_codes.sort()

    url = r"https://api.tdameritrade.com/v1/marketdata/chains"

    statlist = []
    totstats = Statistics("Combined SPX Individual Components")

    for code in main_codes:
        process_code(code, True)

    time.sleep(10.0)

    print("Redo List")
    for code in redo_list:
        process_code(code, False)

    totstats.calc()
    print(totstats)

    with open("out/tdSP500stats.txt", 'w') as fp:
        for stats in statlist:
            fp.write("{}"
                     ""
                     "\n".format(stats))
        fp.write("\n{}\n".format(totstats))
        fp.write("\n\n{}".format(date_time))
