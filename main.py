from pinch_analysis import PinchAnalyser
from utility import Utility
from data_loader import load_streams_from_csv
import matplotlib.pyplot as plt
import numpy as np


# SYSTEM TEST
def get_default_streams():
    default_streams = [[20, 180, 200, 0.6],
                       [140, 230, 300, 0.8],
                       [250, 40, 150, 1],
                       [200, 80, 250, 0.8]]
    default_hu = Utility('hot', T_s=240, T_t=239, h=3)
    default_cu = Utility('cold', T_s=20, T_t=30, h=1)
    return default_streams, default_hu, default_cu


def system_test():
    streams, hu, cu = get_default_streams()
    pinch = PinchAnalyser(streams)
    pinch.get_area_target(hu, cu, 10, verbose=False)
    print(pinch.balanced_composite_curve.get_total_cost())
    assert abs(pinch.balanced_composite_curve.get_total_area() - 7410) < 0.1


# Run the application on the stream data
streams = load_streams_from_csv('test.csv')

hu = Utility('hot', T_s=900, T_t=899, h=1)
cu = Utility('cold', T_s=20, T_t=30, h=1)

pinch = PinchAnalyser(streams)
# pinch.get_composite_curve(dT_min=20, plot=True)
# pinch.get_balanced_composite_curve(hu, cu, dT_min=20, verbose=True)
pinch.get_area_target(hu, cu, 10, verbose=False)
print(pinch.balanced_composite_curve.get_total_cost())

dtmin = range(5,50)
costs = []
for i in dtmin:
    pinch.get_area_target(hu, cu, i, verbose=False)
    costs.append(pinch.balanced_composite_curve.get_total_cost())

plt.plot(dtmin, costs)

plt.show()

# Costing assume Pressure of 43.5 psig
# Material assume carbon steel on both, FM=1
# Assume tube length of 12 ft, FL = 1.12