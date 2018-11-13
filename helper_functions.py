# Export methods
def get_intervals(streams):
    intervals = set()
    for s in streams:
        intervals.add(s.T_s)
        intervals.add(s.T_t)
    return sorted(list(intervals), reverse=True)
