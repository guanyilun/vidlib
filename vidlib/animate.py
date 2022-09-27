from manimlib import *
from datetime import datetime

def endless_loop(start=0, stop=1, period=10):
    """This function produces a function that enables an endless loop of a given period.
    By default it goes from 0 to 1 in 10 seconds.
    
    Parameters
    ----------
    start : float
        start value of the loop
    stop : float
        stop value of the loop
    period : float
        period of the loop in seconds
    
    Return
    ------
    function
        the function that enables the endless loop
    
    """
    t0 = datetime.now().timestamp()
    def f():
        t = (datetime.now().timestamp() - t0) % period
        return t/period*(stop - start) + start
    return f

class EndlessLoopTracker:
    def __init__(self, start=0, stop=1, period=10):
        self.start = start
        self.stop = stop
        self.period = period
        self.f = endless_loop(start, stop, period)

    def get_value(self):
        return self.f()