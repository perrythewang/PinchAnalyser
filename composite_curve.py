import matplotlib.pyplot as plt

TYPE_HOT = 0
TYPE_COLD = 1


class CompositeCurve:
    def __init__(self, hot_streams, cold_streams,
                 hot_intervals, cold_intervals,
                 hot_utility, cold_utility,
                 T_pinch, dTmin):
        # Populate composite curve intervals
        self.hot_streams = hot_streams
        self.cold_streams = cold_streams
        self.hot_composite_curve = []
        self.cold_composite_curve = []
        self.hot_utility = hot_utility
        self.cold_utility = cold_utility
        self.T_pinch = T_pinch
        self.dTmin = dTmin

        for i in range(len(hot_intervals) - 1):
            interval = CompositeCurveInterval(TYPE_HOT, hot_intervals[i], hot_intervals[i + 1])
            interval.extract(hot_streams)
            self.hot_composite_curve.append(interval)

        for i in range(len(cold_intervals) - 1):
            interval = CompositeCurveInterval(TYPE_COLD, cold_intervals[i], cold_intervals[i + 1])
            interval.extract(cold_streams)
            self.cold_composite_curve.append(interval)

    def plot(self):
        plt.figure(figsize=(8, 4.5))
        q = 0
        for interval in reversed(self.hot_composite_curve):
            q_next = q + interval.CP * interval.dT
            plt.plot((q, q_next), (interval.T_c, interval.T_h), 'r-')
            q = q_next

        q = self.cold_utility
        for interval in reversed(self.cold_composite_curve):
            q_next = q + interval.CP * interval.dT
            plt.plot((q, q_next), (interval.T_c, interval.T_h), 'b-')
            q = q_next

        plt.show()

    def get_streams_below_pinch(self):
        streams = []
        for stream in self.hot_streams:
            if stream.T_t < self.T_pinch + self.dTmin/2:
                streams.append(stream)

        for stream in self.cold_streams:
            if stream.T_s < self.T_pinch - self.dTmin/2:
                streams.append(stream)

        return streams

    def get_streams_above_pinch(self):
        streams = []
        for stream in self.hot_streams:
            if stream.T_s > self.T_pinch + self.dTmin/2:
                streams.append(stream)

        for stream in self.cold_streams:
            if stream.T_t > self.T_pinch - self.dTmin/2:
                streams.append(stream)

        return streams


class CompositeCurveInterval:
    def __init__(self, type, T_h, T_c):
        if T_h <= T_c:
            raise InvalidIntervalException('Hot temperature of interval cannot be colder than cold temperature')
        self.T_h = T_h
        self.T_c = T_c
        self.dT = T_h - T_c

        self.type = type
        self.CP = 0
        self.streams = []
        self.Q = -1

    def extract(self, streams):
        for s in streams:
            if s.is_hot():
                if s.T_s > self.T_c and s.T_t < self.T_h:
                    self.CP += s.CP
                    self.streams.append(s)
            elif not s.is_hot():
                if s.T_t > self.T_c and s.T_s < self.T_h:
                    self.CP += s.CP
                    self.streams.append(s)
        # assert len(self.streams) > 0

    def get_heat_load(self):
        return self.CP * self.dT

    def __str__(self):
        type_str = "Hot" if self.type == TYPE_HOT else "Cold"
        return "{} Composite Curve Interval from Th={} to Tc={} with CP={} ({} streams)".format(
            type_str, self.T_h, self.T_c, self.CP, len(self.streams))


class InvalidIntervalException(Exception):
    pass

