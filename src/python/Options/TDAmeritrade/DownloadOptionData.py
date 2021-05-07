import json
from datetime import date, datetime

from TDAmeritrade import td_api_key, TdProcess
from TDAmeritrade.TDA_Interface import call_tda

codes = ['SPY']


def opt_to_str(opt):
    # double currentPriceOfUnderlying;
    # DateTime expiry;
    # double strikePrice;
    # long daysToExpiry;
    # double volatility;
    # double delta;
    # double gamma;
    # double rho;
    # double vega;
    # double theta;

    s = opt.description.split()
    date_time_str = "{}-{}-{}".format(s[1], s[2], s[3])
    date_time_obj = datetime.strptime(date_time_str, '%b-%d-%Y')
    ss = "{}, {:.2f}, {}, {}, {}, ".format(s[0], opt.ul, s[5], date_time_obj.strftime("%d %b %Y"), s[4])
    ss1 = "{:d}, {:.2f}, ".format(opt.daysToExpiration, opt.volatility)
    ss2 = "{}, {}, {}, {}, {}, ".format(opt.delta, opt.gamma, opt.rho, opt.vega, opt.theta)
    ss3 = "{}, {}\n".format(opt.volume, opt.oi)
    ret = ss + ss1 + ss2 + ss3
    return ret


if __name__ == '__main__':
    today = date.today()
    print("Today's date:", today)

    strToday = today.strftime("%Y%m%d")

    for code in codes:
        url = r"https://api.tdameritrade.com/v1/marketdata/chains"
        p = dict(apikey=td_api_key, symbol=code)
        content = call_tda(url, p)

        if content['status'] == "SUCCESS":
            ul = content['underlyingPrice']

            filename = "out/{c}-{d}.json".format(c=code, d=strToday)
            print("Writing : ", filename)
            with open(filename, 'w') as json_file:
                json.dump(content, indent=2, ensure_ascii=True, fp=json_file)
            filename = "out/{c}-{d}.csv".format(c=code, d=strToday)
            print("Writing : ", filename)
            calls = TdProcess.process(content['callExpDateMap'], ul)
            puts = TdProcess.process(content['putExpDateMap'], ul)
            with open(filename, 'w') as csv_file:
                for p in puts:
                    if p.valid:
                        csv_file.write(opt_to_str(p))
                for c in calls:
                    if c.valid:
                        csv_file.write(opt_to_str(c))
