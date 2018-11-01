from PinchAnalysis import PinchAnalyser
from BalancedCompositeCurve import Utility

# Unit and integration tests
streams = [
    [250, 40, 150, 1.0],
    [200, 80, 250, 0.8],
    [20, 180, 200, 0.6],
    [140, 230, 300, 0.8]
]
hu = Utility('hot', T_s=240, T_t=239, h=3)
cu = Utility('cold', T_s=20, T_t=30, h=1)

pinch = PinchAnalyser(streams)
pinch.get_composite_curve(dT_min=10, verbose=False)
pinch.get_balanced_composite_curve(hu, cu, verbose=False)
pinch.get_area_target(hu, cu, 10)
