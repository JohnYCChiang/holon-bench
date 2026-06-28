def parse(text):
    env = {}
    for raw in text.split("\n"):
        if not raw.strip():
            continue
        key, value = raw.split("=")
        env[key.strip()] = value.strip()
    return {"ok": True, "env": env}
