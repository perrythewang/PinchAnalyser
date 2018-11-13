from stream import StreamManager
from heat_cascade import HeatCascade
from composite_curve import CompositeCurve
from balanced_composite_curve import BalancedCompositeCurve
from helper_functions import get_intervals


class PinchAnalyser:
    def __init__(self, streams):
        self.streamManager = StreamManager(streams)
        self.streams = self.streamManager.get_streams()
        self.T_pinch = None
        self.T_pinch_actual = None
        self.composite_curve = None
        self.balanced_composite_curve = None
        self.heat_cascade = None

    def problem_table_analysis(self, dT_min=5, verbose=True):
        shifted_streams = self._shifted_temp_streams(self.streams, dT_min)
        shifted_intervals = get_intervals(shifted_streams)

        self.heat_cascade = HeatCascade(shifted_streams, shifted_intervals)
        if verbose:
            self.heat_cascade.print_table()

        self.T_pinch, self.hot_utility, self.cold_utility = self.heat_cascade.get_results()
        self.T_pinch_actual = (self.T_pinch + dT_min/2, self.T_pinch - dT_min/2)

    def get_composite_curve(self, dT_min=None, plot=True):
        if dT_min is not None:
            self.problem_table_analysis(dT_min=dT_min, verbose=False)

        if self.T_pinch is None:
            print(
                'Pinch analysis has not been carried out yet! Composite curves will be drawn using default dTmin=5degC')
            self.problem_table_analysis(verbose=False)

        self.composite_curve = CompositeCurve(
            self.streamManager.get_hot_streams(),
            self.streamManager.get_cold_streams(),
            get_intervals(self.streamManager.get_hot_streams()),
            get_intervals(self.streamManager.get_cold_streams()),
            self.hot_utility,
            self.cold_utility,
            self.T_pinch
        )

        if plot:
            self.composite_curve.plot()

    def get_balanced_composite_curve(self, hot_utility_stream, cold_utility_stream, dT_min=5, verbose=True):
        '''Only functional for single HU and CU'''
        if self.T_pinch is None:
            self.get_composite_curve(dT_min=dT_min, plot=False)

        self.balanced_composite_curve = BalancedCompositeCurve(
            self.streamManager.get_hot_streams(),
            self.streamManager.get_cold_streams(),
            self.hot_utility,
            self.cold_utility,
            hot_utility_stream,
            cold_utility_stream,
            self.T_pinch,
            dT_min
        )

        if verbose:
            self.balanced_composite_curve.plot()

    def test_balanced_composite_curve_q_intervals(self):
        print(self.balanced_composite_curve.get_area_target())

    def get_area_target(self, hot_utility_stream, cold_utility_stream, dT_min=5, verbose=True):
        self.problem_table_analysis(dT_min, verbose=False)
        self.get_balanced_composite_curve(hot_utility_stream, cold_utility_stream, verbose=verbose)

        return self.balanced_composite_curve.get_area_target(verbose=verbose)

    # Private methods
    def _shifted_temp_streams(self, streams, dt_min):
        dt = dt_min / 2.0
        return [s.shift(dt) for s in streams]
