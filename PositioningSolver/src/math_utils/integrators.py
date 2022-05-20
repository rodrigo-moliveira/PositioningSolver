def integrate_euler(y0, x0_dot, step, f=None, x0=None):
    # x0_dot = f(x0, y0) melhor?
    return y0 + step * x0_dot
