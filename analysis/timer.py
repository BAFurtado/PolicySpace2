from timeit import default_timer as timer


class Timer:
    """Tracks running times"""
    def start(self):
        self._start = timer()

    def elapsed(self, fmt=False):
        elapsed =  timer() - self._start
        if fmt:
            m, s = divmod(elapsed, 60)
            h, m = divmod(m, 60)
            return h, m, s
        return elapsed
