import math
import numpy as np
import matplotlib.pyplot as plt
from helper_functions import get_intervals
from composite_curve import CompositeCurve

TYPE_HOT = 0
TYPE_COLD = 1


class BalancedCompositeCurve(CompositeCurve):
    def __init__(self, hot_streams, cold_streams, hot_utility, cold_utility,
                 hot_utility_stream, cold_utility_stream, T_pinch, dTmin):
        hot_streams.append(hot_utility_stream.fit(hot_utility))
        cold_streams.append(cold_utility_stream.fit(cold_utility))

        hot_intervals = get_intervals(hot_streams)
        cold_intervals = get_intervals(cold_streams)

        self.bcc_intervals = []
        self.q_intervals = []

        super().__init__(hot_streams, cold_streams,
                         hot_intervals, cold_intervals,
                         hot_utility=0, cold_utility=0,
                         T_pinch=T_pinch, dTmin=dTmin)

    def get_area_target(self, verbose=True):
        self.get_heat_intervals(self.hot_composite_curve, self.cold_composite_curve)
        if verbose:
            self.print_report()
            self.plot_from_heat_intervals()
        return self.get_total_area()

    def get_heat_intervals(self, hcc, ccc):
        hcc = hcc.copy()
        hcc.sort(key=lambda intv: intv.T_c)
        ccc = ccc.copy()
        ccc.sort(key=lambda intv: intv.T_c)

        q_intervals = set()
        q = 0
        for intv in hcc:
            q_old = q
            q += intv.get_heat_load()
            q = np.round(q, decimals=6)
            q_intervals.add(q)
            intv.Q = (q_old, q)

        q = 0
        for intv in ccc:
            q_old = q
            q += intv.get_heat_load()
            q = np.round(q, decimals=6)
            q_intervals.add(q)
            intv.Q = (q_old, q)

        q_intervals = [0] + sorted(list(q_intervals))

        T_h_start = hcc[0].T_c
        T_c_start = ccc[0].T_c

        for i in range(len(q_intervals) - 1):
            bcc_interval = BalancedCompositeCurveHeatInterval(
                q_intervals[i], q_intervals[i+1], T_h_start, T_c_start)
            bcc_interval.take_streams_from_curves(hcc, ccc)
            T_h_start, T_c_start = bcc_interval.get_final_temps()
            self.bcc_intervals.append(bcc_interval)

        self.q_intervals = q_intervals

    def get_total_area(self):
        return sum([intv.get_area() for intv in self.bcc_intervals])

    def get_total_cost(self):
        # In BCC, utilities have already been added. Therefore, no heater/cooler is counted in Nmin.
        n_min_exchangers = len(self.get_streams_below_pinch()) + len(self.get_streams_above_pinch()) - 2
        print(self.get_total_area())
        area_per_exchanger = self.get_total_area()/n_min_exchangers
        return n_min_exchangers * self._get_base_cost(area_per_exchanger)

    @staticmethod
    def _get_base_cost(area):
        '''
        Calculates base cost for fixed head Heat Exchanger based on area correlation
        :param area: HE area (m2)
        :return: base cost ($)
        '''
        # conversion from m2 to ft2
        area = 10.76391041671 * area
        return math.exp(11.0545 - 0.9228 * math.log(area) + 0.09861 * math.log(area) ** 2)

    def plot_from_heat_intervals(self):
        temps_h = [self.bcc_intervals[0].T_h_start]
        temps_c = [self.bcc_intervals[0].T_c_start]
        heats = [0]
        for intv in self.bcc_intervals:
            temps_h.append(intv.T_h_start)
            temps_c.append(intv.T_c_start)
            temps_h.append(intv.T_h_end)
            temps_c.append(intv.T_c_end)
            heats.append(intv.q_start)
            heats.append(intv.q_end)

        plt.figure(figsize=(8,4.5))
        plt.plot(heats, temps_h, 'r')
        plt.plot(heats, temps_c, 'b')
        plt.show()

    def print_report(self):
        print("===== Balanced Composite Curve =====")
        for intv in self.bcc_intervals:
            print(intv)
        print("====================================")


class BalancedCompositeCurveHeatInterval:
    def __init__(self, q_start, q_end, T_h_start, T_c_start):
        self.q_start = q_start
        self.q_end = q_end
        self.heat_load = q_end - q_start

        self.T_h_start = T_h_start
        self.T_c_start = T_c_start
        self.T_h_end = 0
        self.T_c_end = 0

        self.hot_streams = []
        self.cold_streams = []

        self.hot_CP = 0
        self.cold_CP = 0

    def take_streams_from_curves(self, hcc, ccc, verbose=False):
        for intv in hcc:
            if self._intersect(intv.Q, (self.q_start, self.q_end)):
                if intv.Q[1] - intv.Q[0] < 1e-6:
                    self.T_h_start = intv.T_h
                self.hot_streams += intv.streams

        for intv in ccc:
            if self._intersect(intv.Q, (self.q_start, self.q_end)):
                if intv.Q[1] - intv.Q[0] < 1e-6:
                    self.T_c_start = intv.T_h
                self.cold_streams += intv.streams

        self._get_combined_CP()

    def _get_combined_CP(self):
        for s in self.hot_streams:
            self.hot_CP += s.CP

        for s in self.cold_streams:
            self.cold_CP += s.CP

        assert self.hot_CP != 0 and self.cold_CP != 0

    def get_final_temps(self):
        self.T_h_end = self.T_h_start + self.heat_load/self.hot_CP
        self.T_c_end = self.T_c_start + self.heat_load/self.cold_CP

        return self.T_h_end, self.T_c_end

    def get_lmtd(self):
        upper_term = (self.T_h_end - self.T_c_end) - (self.T_h_start - self.T_c_start)
        lower_term = math.log((self.T_h_end - self.T_c_end) / (self.T_h_start - self.T_c_start))
        return upper_term / lower_term

    def get_area(self):
        area = 0
        for stream in self.hot_streams:
            area += stream.CP * (self.T_h_end - self.T_h_start) / stream.h

        for stream in self.cold_streams:
            area += stream.CP * (self.T_c_end - self.T_c_start) / stream.h

        return area / self.get_lmtd()

    @staticmethod
    def _intersect(r1, r2):
        if r1[0] == r1[1]:
            return r2[1] > r1[1] and r2[0] <= r1[0]
        if r2[0] == r2[1]:
            return r1[1] > r2[1] and r1[0] <= r2[0]
        return max(r1[0], r2[0]) < min(r1[-1], r2[-1])

    def __str__(self):
        return ("BCC Area Segment with Heat Load interval from {} to {} (dQ = {}) \n    LMTD = {}, Area = {}".format(
            self.q_start, self.q_end, (self.q_end - self.q_start), self.get_lmtd(), self.get_area()) + (
            "\n    T_hot = {} to {}, T_cold = {} to {}".format(self.T_h_start, self.T_h_end, self.T_c_start, self.T_c_end))
        )


class InvalidIntervalException(Exception):
    pass


# b = BalancedCompositeCurveHeatInterval(0,1, 0, 1)
# print(b._intersect((8.8, 11), (8,9)))
# print(b._intersect((9,9), (10,10)))
# print(b._intersect((9,9), (9,10)))
# print(b._intersect((9,9), (8,9)))
# print(b._intersect((8,9), (9,9)))
# print(b._intersect((9,10), (9,9)))
# print(b._intersect((9,10), (10,11)))

# Unit tests
# u1 = Utility('hot', T_s=150, CP=40)
# print(u1)
# u2 = Utility('cold', T_t=150, CP=20)
# print(u2)
# u3 = Utility('hot', T_s=240, T_t=239)
# print(u3.fit(7500))
# u4 = Utility('cold', T_s=20, T_t=30)
# print(u4.fit(10000))