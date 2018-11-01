import math
import numpy as np
import matplotlib.pyplot as plt
from HelperFunctions import get_intervals
from CompositeCurve import CompositeCurve
from Utility import Utility

TYPE_HOT = 0
TYPE_COLD = 1


class BalancedCompositeCurve(CompositeCurve):
    def __init__(self, hot_streams, cold_streams, hot_intervals, cold_intervals, hot_utility, cold_utility,
                 hot_utility_stream, cold_utility_stream):
        hot_streams.append(hot_utility_stream.fit(hot_utility))
        cold_streams.append(cold_utility_stream.fit(cold_utility))

        hot_intervals = get_intervals(hot_streams)
        cold_intervals = get_intervals(cold_streams)

        super().__init__(hot_streams, cold_streams, hot_intervals, cold_intervals, hot_utility=0, cold_utility=0)

    def get_area_target(self, verbose=True):
        intervals = []

        hcc = self.hot_composite_curve.copy()
        hcc.sort(key=lambda i: i.T_c)
        ccc = self.cold_composite_curve.copy()
        ccc.sort(key=lambda i: i.T_c)

        hot_idx = 0
        cold_idx = 0

        q = 0
        q_balance = 0

        T_h_interval = hcc[0].T_c
        T_c_interval = ccc[0].T_c

        # Iterate through cold and hot composite curves.
        # Create a combined balanced composite curve interval based on which combined stream
        # has lower heat load.
        while hot_idx < len(hcc) or cold_idx < len(ccc):
            # No more hot streams
            if hot_idx >= len(hcc):
                # TO-DO handle only cold stream
                cold_idx += 1

            if cold_idx >= len(ccc):
                hot_idx += 1

            hot_interval = hcc[hot_idx]
            cold_interval = ccc[cold_idx]
            hot_load = q_balance if q_balance > 0 else hot_interval.get_heat_load()
            cold_load = -q_balance if q_balance < 0 else cold_interval.get_heat_load()

            q_old = q
            q_balance = hot_load - cold_load

            if hot_load < cold_load:
                q += hot_load

                if q_balance == 0:
                    cold_idx += 1
                hot_idx += 1
            else:
                q += cold_load

                if q_balance == 0:
                    hot_idx += 1
                cold_idx += 1

            heat_interval = BalancedCompositeCurveHeatInterval(
                q_old, q, T_h_interval, T_c_interval, hot_interval, cold_interval)

            intervals.append(heat_interval)

            T_h_interval += (q - q_old) / hot_interval.CP
            T_c_interval += (q - q_old) / cold_interval.CP

        if verbose:
            for i in intervals:
                print(i)
        return sum([x.get_area() for x in intervals])


class BalancedCompositeCurveHeatInterval:
    def __init__(self, q_low, q_high, T_h, T_c, hot_interval, cold_interval):
        # Get heat load vars
        self.q_high = q_high
        self.q_low = q_low
        self.dq = q_high - q_low

        # Load up hcc and ccc intervals and save them here
        self.hot_interval = hot_interval
        self.cold_interval = cold_interval

        # Load up temperature intervals for both hot and cold streams
        self.T_h_low = T_h
        self.T_c_low = T_c
        self.T_h_high = T_h + self.dq/hot_interval.CP
        self.T_c_high = T_c + self.dq/cold_interval.CP

        self._import_streams_from_interval(hot_interval)
        self._import_streams_from_interval(cold_interval)
        self.get_area()

    def _import_streams_from_interval(self, interval):
        pass

    def get_lmtd(self):
        upper_term = (self.T_h_high - self.T_c_high) - (self.T_h_low - self.T_c_low)
        lower_term = math.log((self.T_h_high - self.T_c_high) / (self.T_h_low - self.T_c_low))
        return upper_term / lower_term

    def get_area(self):
        area = 0

        # Sum up all hot stream area (before LMTD)
        for s in self.hot_interval.streams:
            area += s.CP * (self.T_h_high - self.T_h_low) / s.h

        # Sum up all cold stream area (before LMTD)
        for s in self.cold_interval.streams:
            area += s.CP * (self.T_c_high - self.T_c_low) / s.h

        return area/self.get_lmtd()

    def __str__(self):
        return "BCC Area Segment with Heat Load interval from {} to {} (dQ = {}) and\n    LMTD = {}, Area = {}".format(
            self.q_low, self.q_high, self.dq, self.get_lmtd(), self.get_area()
        )


class InvalidIntervalException(Exception):
    pass


# Unit tests
# u1 = Utility('hot', T_s=150, CP=40)
# print(u1)
# u2 = Utility('cold', T_t=150, CP=20)
# print(u2)
# u3 = Utility('hot', T_s=240, T_t=239)
# print(u3.fit(7500))
# u4 = Utility('cold', T_s=20, T_t=30)
# print(u4.fit(10000))