class Statistics:

    def __init__(self, symbol):
        self.code = symbol

        self.totalPutsOi = 0
        self.totalPutsVol = 0
        self.dollarPutsOi = 0.0
        self.dollarPutsVol = 0.0

        self.totalCallsOi = 0
        self.totalCallsVol = 0
        self.dollarCallsOi = 0.0
        self.dollarCallsVol = 0.0

        self.putcall = 0.0
        self.putcallio = 0.0
        self.dollarputcall = 0.0
        self.dollarputcalloi = 0.0

        self.calliv = 0.0
        self.putiv = 0.0
        self.avgiv = 0.0
        self.realvol = 0.0
        self.callpremium = 0.0
        self.putpremium = 0.0
        self.premium = 0.0

    def __str__(self):
        width = 15

        tot_vol = self.totalPutsVol + self.totalCallsVol

        ret = " {}:\n".format(self.code)
        if tot_vol > 0:
            s_totalPutsVol = "{:,d}".format(self.totalPutsVol)
            s_totalCallsVol = "{:,d}".format(self.totalCallsVol)

            ret = "\tVolume Put   : {}\t\tCall : {}\t : {:.2f}\n".format(
                s_totalPutsVol.rjust(width), s_totalCallsVol.rjust(width), self.putcall)

            s_dollarPutsVol = "${:,d}".format(int(self.dollarPutsVol * 100.0))
            s_dollarCallsVol = "${:,d}".format(int(self.dollarCallsVol * 100.0))
            ret += "\tVolume Put $ : {}\t\tCall : {}\t : {:.2f}\n".format(
                s_dollarPutsVol.rjust(width), s_dollarCallsVol.rjust(width), self.dollarputcall)

        s_totalPutsOi = "{:,d}".format(self.totalPutsOi)
        s_totalCallsOi = "{:,d}".format(self.totalCallsOi)
        s_dollarPutsOi = "${:,d}".format(int(self.dollarPutsOi * 100.0))
        s_dollarCallsOi = "${:,d}".format(int(self.dollarCallsOi * 100.0))

        ret += "\tOI Put       : {}\t\tCall : {}\t : {:.2f}\n".format(
            s_totalPutsOi.rjust(width), s_totalCallsOi.rjust(width), self.putcallio)
        ret += "\tOI Put     $ : {}\t\tCall : {}\t : {:.2f}\n".format(
            s_dollarPutsOi.rjust(width), s_dollarCallsOi.rjust(width), self.dollarputcalloi)

        if self.putiv > 0.0:
            s_putiv = "{:.2f}".format(self.putiv)
            s_calliv = "{:.2f}".format(self.calliv)
            s_realvol = "{:.2f}".format(self.realvol)
            s_premium = "{:7.2f}".format(self.premium)
            s_putpremium = "{:.2f}".format(self.putpremium)
            s_callpremium = "{:.2f}".format(self.callpremium)
            tmp = "\tAvg IV Put   : {}\t\tCall : {}\t   RealVol :{}\tPremium :{}".format(
                s_putiv.rjust(width), s_calliv.rjust(width), s_realvol.rjust(6), s_premium.rjust(6))
            ret += tmp

        return ret

    def calc(self):
        if self.totalCallsVol > 0:
            self.putcall = self.totalPutsVol / self.totalCallsVol
            self.dollarputcall = self.dollarPutsVol / self.dollarCallsVol
        if self.totalCallsOi > 0:
            self.putcallio = self.totalPutsOi / self.totalCallsOi
            self.dollarputcalloi = self.dollarPutsOi / self.dollarCallsOi
        self.avgiv = float(self.putiv + self.calliv) / 2.0
        if self.realvol != 0.0:
            self.premium = ((self.avgiv / self.realvol) - 1.0) * 100.0
