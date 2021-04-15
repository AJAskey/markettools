from TDAmeritrade import td_api_key
from TDAmeritrade.TDA_Interface import get_tda_list, print_opt_list
from TDAmeritrade.TdProcess import get_realvol


def process(code, datype, min_vol, min_dte, theta_decay, price_chg_percent):
    url = r"https://api.tdameritrade.com/v1/marketdata/chains"

    p = dict(apikey=td_api_key, symbol=code)
    ul, daList = get_tda_list(url=url, params=p, min_dte=min_dte, max_dte=min_dte + 200, min_oi=500,
                              min_vol=min_vol, min_price=0.10, max_iv=40.0, opt_type=datype)

    print_opt_list(daList)

    ul_chg = ul * price_chg_percent

    realvol = get_realvol(code, 22)

    print("code,ul,ul_chg,delta,theta,delta_price,theta_price,price,bot,sold,gain")

    fname = "out/{}-{}-model.csv".format(code, datype)
    with open(fname, 'w') as fp:
        fp.write("code,ul,ul_chg,delta,theta,delta_price,theta_price,price chg,hv,iv,bot,sold,gain\n")
        for data in daList:
            delta_price = abs(data.delta * ul_chg)
            theta_price = abs(data.theta * theta_decay)
            price_chg = float(delta_price - theta_price)

            bot = data.mark
            sold = data.mark + price_chg
            chg = (sold / bot) - 1.0

            str = ""
            str += "{}".format(data.symbol)
            str += ",{:.2f}".format(ul)
            str += ",{:.2f}".format(ul_chg)
            str += ",{:.4f}".format(abs(data.delta))
            str += ",{:.4f}".format(data.theta)
            str += ",{:.2f}".format(delta_price)
            str += ",{:.2f}".format(theta_price)
            str += ",{:.2f}".format(price_chg)
            str += ",{:.2f}".format(realvol)
            str += ",{:d}".format(int(data.volatility))
            str += ",{:.2f}".format(bot)
            str += ",{:.2f}".format(sold)
            str += ",{:.2f}".format(chg)
            print(str)
            str += "\n"
            if data.mark < 3.01:
                fp.write(str)


if __name__ == '__main__':
    mvol = int(0)

    process("SPY", "PUT", min_vol=mvol, min_dte=55, theta_decay=10, price_chg_percent=0.10)
    process("SPY", "CALL", min_vol=mvol, min_dte=55, theta_decay=10, price_chg_percent=0.10)

