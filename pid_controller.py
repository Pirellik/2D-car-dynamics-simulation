import numpy as np


class PidController:
    def __init__(self, p_gain, i_gain, d_gain, set_point=0):
        self.p_gain = p_gain
        self.i_gain = i_gain
        self.d_gain = d_gain
        self.set_point = set_point
        self.integrated_error = 0
        self.previous_error = 0

    def get_control(self, process_value):
        error = self.set_point - process_value
        control = self.p_gain * error + self.i_gain * self.integrated_error + self.d_gain * (error - self.previous_error)
        self.previous_error = error
        self.integrated_error += error
        return np.sign(control) * min(abs(control), 30)
