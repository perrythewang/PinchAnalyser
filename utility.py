from stream import Stream

VAR_TS = 0
VAR_TT = 1
VAR_CP = 2


class Utility:

    def __init__(self, type='hot', T_s=None, T_t=None, CP=None, h=1):
        # type comes in string 'hot' or 'cold'
        self.type = -1 if type == 'hot' else 1
        self.h = h
        _dof = self._degrees_of_freedom(T_s, T_t, CP)
        if _dof > 0:
            raise ValueError \
                ("Too few parameters supplied! Utility requires exactly 1 degree of freedom to fit to the process!")
        elif _dof < 0:
            raise ValueError \
                ("Too many parameters supplied! Utility requires exactly 1 degree of freedom to fit to the process!")
        else:
            self.T_s = T_s
            self.T_t = T_t
            self.CP = CP

        self.variable = VAR_TS * (T_s is None) + VAR_TT * (T_t is None) + VAR_CP * (CP is None)

    def _degrees_of_freedom(self, T_s, T_t, CP):
        return (T_s is None) + (T_t is None) + (CP is None) - 1

    def fit(self, Q):
        Q = self.type * Q
        if self.variable == VAR_TS:
            T_s = self.T_t - Q/ self.CP
            return Stream(T_s, self.T_t, self.CP, h=self.h)
        elif self.variable == VAR_TT:
            T_t = self.T_s + Q / self.CP
            return Stream(self.T_s, T_t, self.CP, h=self.h)
        else:
            CP = Q / (self.T_t - self.T_s)
            return Stream(self.T_s, self.T_t, CP, h=self.h)

    def __str__(self):
        type_str = 'Hot' if self.type == -1 else 'Cold'
        if self.variable == VAR_TS:
            defined_str = 'Tt={} CP={}'.format(self.T_t, self.CP)
            var_str = 'Ts'
        elif self.variable == VAR_TT:
            defined_str = 'Ts={} CP={}'.format(self.T_s, self.CP)
            var_str = 'Tt'
        else:
            defined_str = 'Ts={} Tt={}'.format(self.T_s, self.T_t)
            var_str = 'CP'

        return "{} Utility with {} and variable {}".format(type_str, defined_str, var_str)

