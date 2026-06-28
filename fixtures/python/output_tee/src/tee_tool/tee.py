class Tee:
    def __init__(self, sinks):
        self.sinks = list(sinks)
        self.bytes_written = 0

    def write(self, data):
        self.sinks[0].write(data)
        self.bytes_written += len(data) * len(self.sinks)
        return len(data)

    def flush(self):
        for sink in self.sinks:
            if hasattr(sink, "flush"):
                sink.flush()


def tee(chunks, sinks):
    t = Tee(sinks)
    n = 0
    for chunk in chunks:
        t.write(chunk)
        n += 1
    return {"ok": True, "bytes": t.bytes_written, "chunks": n}
