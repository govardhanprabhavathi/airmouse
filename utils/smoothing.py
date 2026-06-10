import math

class OneEuroFilter:
    def __init__(self, t0, x0, mincutoff=1.0, beta=0.007, dcutoff=1.0):
        self.mincutoff = float(mincutoff)
        self.beta = float(beta)
        self.dcutoff = float(dcutoff)
        self.x_prev = float(x0)
        self.dx_prev = 0.0
        self.t_prev = float(t0)

    def __call__(self, t, x):
        dt = t - self.t_prev
        if dt <= 0:
            return self.x_prev

        # estimate the current variation of the signal
        edx = (x - self.x_prev) / dt
        # filter the derivative
        alpha_d = self.smoothing_factor(dt, self.dcutoff)
        dx = alpha_d * edx + (1.0 - alpha_d) * self.dx_prev

        # use it to update the cutoff frequency
        cutoff = self.mincutoff + self.beta * abs(dx)
        # filter the signal
        alpha = self.smoothing_factor(dt, cutoff)
        x_filtered = alpha * x + (1.0 - alpha) * self.x_prev

        # update state
        self.x_prev = x_filtered
        self.dx_prev = dx
        self.t_prev = t

        return x_filtered

    def smoothing_factor(self, dt, cutoff):
        r = 2.0 * math.pi * cutoff * dt
        return r / (r + 1.0)

def smooth_coordinates(prev_x, prev_y, curr_x, curr_y, alpha):
    """
    Standard Exponential Moving Average fallback
    """
    if prev_x is None or prev_y is None:
        return curr_x, curr_y
    smooth_x = prev_x + alpha * (curr_x - prev_x)
    smooth_y = prev_y + alpha * (curr_y - prev_y)
    return int(smooth_x), int(smooth_y)
