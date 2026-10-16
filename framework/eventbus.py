"""Event bus with fan-out: one event is delivered to every subscribed pipeline.
Star shape: event in the center, multiple independent pipelines radiating out."""
from collections import defaultdict


class StopPipeline(Exception):
    def __init__(self, reason):
        self.reason = reason
        super().__init__(reason)


class Pipeline:
    def __init__(self, name):
        self.name = name
        self.filters = []

    def use(self, fn):
        self.filters.append(fn)
        return self

    def run(self, ctx):
        ctx.setdefault("_logs", [])
        for f in self.filters:
            name = getattr(f, "name", f.__name__)
            try:
                f(ctx)
                ctx["_logs"].append(f"[{self.name}] ok: {name}")
            except StopPipeline as e:
                ctx["_logs"].append(f"[{self.name}] STOP at {name}: {e.reason}")
                break
        return ctx


class EventBus:
    def __init__(self):
        self.subscribers = defaultdict(list)  # event_type -> [Pipeline]

    def subscribe(self, event_type: str, pipeline: Pipeline):
        self.subscribers[event_type].append(pipeline)

    def publish(self, event_type: str, event: dict):
        """Fan-out: run every subscribed pipeline independently.
        One pipeline failing does NOT stop the others."""
        results = []
        for pipe in self.subscribers.get(event_type, []):
            ctx = dict(event)
            try:
                pipe.run(ctx)
                results.append((pipe.name, "done", ctx["_logs"]))
            except Exception as e:
                results.append((pipe.name, f"crashed: {e}", ctx.get("_logs", [])))
        return results
