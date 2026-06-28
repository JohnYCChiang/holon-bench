def split(text):
    parts = text.split("---")
    if len(parts) >= 3:
        return {"ok": True, "frontmatter": parts[1].strip(), "body": parts[2].strip()}
    return {"ok": True, "frontmatter": "", "body": text.strip()}
