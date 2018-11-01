import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


class Stream:
    TYPE_HOT = 0
    TYPE_COLD = 1

    # Constructor/factory methods
    def __init__(self, T_s, T_t, CP, h=1):
        if T_s == T_t:
            raise ValueError("Stream cannot have equal supply and target temperatures!")
        self.T_s = T_s
        self.T_t = T_t
        self.CP = CP
        self.h = h

        self.Q = abs(T_s - T_t) * CP
        self.type = self.TYPE_HOT if (T_s > T_t) else self.TYPE_COLD

    @classmethod
    def clone(self, stream_obj, T_s=None, T_t=None, CP=None, h=None):
        T_s = stream_obj.T_s if T_s is None else T_s
        T_t = stream_obj.T_t if T_t is None else T_t
        CP = stream_obj.CP if CP is None else CP
        h = stream_obj.h if h is None else h
        return Stream(T_s, T_t, CP, h)

    # Object methods
    def is_hot(self):
        return self.type == self.TYPE_HOT

    def shift(self, dt):
        '''Returns deep copy of the stream with applied shifted temperatures'''
        t_shift = (-dt) if self.is_hot() else dt
        return Stream.clone(self, self.T_s + t_shift, self.T_t + t_shift)

    # Override print behaviour
    def __str__(self):
        type_str = "Hot" if self.is_hot() else "Cold"
        return ("{0:s} stream with Ts={1:f} Tt={2:f} CP={3:f}  Q={4:f} h={5:f}".format(
            type_str, self.T_s, self.T_t, self.CP, self.Q, self.h))


class StreamManager():
    def __init__(self, streams_list=None):
        self.streams = []
        if not streams_list is None:
            for s in streams_list:
                self.add_stream(s)

    def add_stream(self, stream):
        if isinstance(stream, list):
            if len(stream) == 3:
                self.streams.append(Stream(stream[0], stream[1], stream[2]))
            elif len(stream) == 4:
                self.streams.append(Stream(stream[0], stream[1], stream[2], stream[3]))
            else:
                raise IndexError('Input stream data has too many/few items!')
        else:
            self.streams.append(stream)

    def get_streams(self):
        return self.streams

    def get_hot_streams(self):
        return [s for s in self.streams if s.type == Stream.TYPE_HOT]

    def get_cold_streams(self):
        return [s for s in self.streams if s.type == Stream.TYPE_COLD]

    def print_streams(self):
        for s in self.streams:
            print(s)


# Unit tests
# s = Stream(20, 135, 2, 0.2)
# s2 = Stream.clone(s, T_s=100)
# s3 = s.shift(10)
# print(s)
# print(s2)
# print(s3)

# Unit Tests
# streams = [
#     [30, 140, 5],
#     [105, 230, 12],
#     [160, 75, 9],
#     [350, 90, 3],
#     [260, 80, 1.2]
# ]
# sm = StreamManager()
# for s in streams:
#     sm.add_stream(s)
#
# sm.print_streams()