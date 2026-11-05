"""Bound trace, observation and score emissions for the GPT expansion."""
class ServiceUnits:
    """Admission meter shared by all exporter and score-worker threads in one service allocation."""
    def __init__(self, limit):
        from threading import Lock
        self.limit = limit
        self.spent = 0
        self.exhausted = False
        self.traces = set()
        self.lock = Lock()

    def admit(self, trace=None):
        with self.lock:
            units = 1 + int(trace is not None and trace not in self.traces)
            if self.exhausted or self.spent + units > self.limit:
                self.exhausted = True
                raise RuntimeError('Langfuse unit reservation exhausted')
            self.spent += units
            if trace is not None:
                self.traces.add(trace)


def bind_score_meter(client, meter):
    original = client._resources.add_score_task
    def bounded(*args, **kwargs):
        meter.admit()
        return original(*args, **kwargs)
    client._resources.add_score_task = bounded
    return original


def bounded_filter(policy, meter):
    def check(span):
        if not policy(span):
            return False
        # The SDK also consults this filter at span start for root labelling.
        if span.end_time is not None:
            meter.admit(span.context.trace_id)
        return True
    return check


class MeteredRuntimeClient:
    """Reserve each runtime span and each new trace before the SDK receives them."""
    def __init__(self, client, meter):
        self.client = client
        self.meter = meter

    def start_observation(self, **kwargs):
        self.meter.admit(kwargs['trace_context']['trace_id'])
        return self.client.start_observation(**kwargs)

    def __getattr__(self, name):
        return getattr(self.client, name)
