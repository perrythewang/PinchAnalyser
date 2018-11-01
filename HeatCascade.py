import pandas as pd


class HeatCascade:
    def __init__(self, streams, intervals):
        # Populate heat cascade intervals
        self.cascades = []
        for i in range(len(intervals) - 1):
            interval = HeatCascadeInterval(intervals[i], intervals[i + 1])
            for s in streams:
                interval.add(s)
            self.cascades.append(interval)

        # Perform heat cascade to find shifted pinch temperature
        q = 0
        violation = 1
        for c in self.cascades:
            q = c.infeasible_cascade(q)
            violation = min(violation, q)

        # Feasible heat cascade
        q = -violation
        self.T_pinch = None
        for c in self.cascades:
            q = c.feasible_cascade(q)
            if q == 0:
                self.T_pinch = c.T_c

        self.hot_utility = -violation
        self.cold_utility = self.cascades[-1].fhc

    def get_results(self):
        return self.T_pinch, self.hot_utility, self.cold_utility

    def print_table(self):
        print('===== PROBLEM TABLE ANALYSIS =====')
        print("Pinch temperature is at shifted T = {}".format(self.T_pinch))
        print("Minimum Hot Utility = {}, Minimum Cold Utility = {}".format(self.hot_utility, self.cold_utility))

        cascades_list = [self.cascades[0].T_h, 0, 0, 0, 0, self.hot_utility]
        for c in self.cascades:
            cascades_list.append([c.T_c, c.dT, c.CP_total, c.dH, c.ihc, c.fhc])
        print(pd.DataFrame(cascades_list,
                           columns=['S', 'dS', 'CP total', 'dH', 'Infeasible Cascade', 'Feasible Cascade']))
        print("=" * 32)


class HeatCascadeInterval:
    def __init__(self, T_h, T_c):
        if T_h <= T_c:
            raise InvalidIntervalException('Hot temperature of interval cannot be colder than cold temperature')
        self.T_h = T_h
        self.T_c = T_c
        self.CP_total = 0
        self.dH = 0
        self.dT = T_h - T_c

    def add(self, stream):
        if stream.is_hot():
            if stream.T_s > self.T_c and stream.T_t < self.T_h:
                self.CP_total += stream.CP
                self.dH = self.CP_total * self.dT
        elif not stream.is_hot():
            if stream.T_t > self.T_c and stream.T_s < self.T_h:
                self.CP_total -= stream.CP
                self.dH = self.CP_total * self.dT

    def infeasible_cascade(self, q):
        self.ihc = q + self.dH
        return self.ihc

    def feasible_cascade(self, q):
        self.fhc = q + self.dH
        return self.fhc


class InvalidIntervalException(Exception):
    pass
