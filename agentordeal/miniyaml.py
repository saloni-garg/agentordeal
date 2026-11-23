"""A tiny YAML-subset parser, stdlib only.

Supports exactly what promptfoo-style config files use in practice:
block mappings, block sequences, inline flow maps/lists, quoted and
plain scalars, and comments. It is NOT a general YAML implementation:
no anchors, tags, multi-line scalars, or multiple documents. Anything
outside the subset raises MiniYAMLError rather than guessing.
"""
class MiniYAMLError(ValueError):
    pass

def _scalar(s):
    s = s.strip()
    if s == "" or s == "~" or s.lower() == "null": return None
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        body = s[1:-1]
        return body.replace('\\"', '"').replace("\\n", "\n") if s.startswith('"') else body.replace("''", "'")
    if s.startswith("{") and s.endswith("}"):
        inner = s[1:-1].strip()
        out = {}
        if inner:
            for part in _split_flow(inner):
                k, _, v = part.partition(":")
                out[_scalar(k)] = _scalar(v)
        return out
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        return [_scalar(p) for p in _split_flow(inner)] if inner else []
    low = s.lower()
    if low in ("true", "false"): return low == "true"
    try: return int(s)
    except ValueError: pass
    try: return float(s)
    except ValueError: pass
    return s

def _split_flow(s):
    parts, depth, cur, quote = [], 0, "", None
    for ch in s:
        if quote:
            cur += ch
            if ch == quote: quote = None
            continue
        if ch in "\"'": quote = ch; cur += ch; continue
        if ch in "{[": depth += 1
        if ch in "}]": depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur); cur = ""; continue
        cur += ch
    if cur.strip(): parts.append(cur)
    return [p.strip() for p in parts]

def _lines(text):
    out = []
    for raw in text.splitlines():
        if not raw.strip() or raw.strip().startswith("#"): continue
        indent = len(raw) - len(raw.lstrip(" "))
        out.append((indent, raw.strip()))
    return out

def _parse_block(lines, i, indent):
    if i >= len(lines): return None, i
    if lines[i][1].startswith("- ") or lines[i][1] == "-":
        seq = []
        while i < len(lines) and lines[i][0] == indent and (lines[i][1].startswith("- ") or lines[i][1] == "-"):
            item_text = lines[i][1][1:].strip()
            if item_text == "":
                val, i = _parse_block(lines, i + 1, lines[i + 1][0] if i + 1 < len(lines) else indent + 2)
                seq.append(val); continue
            # inline start of a nested block: re-inject as a virtual line
            virtual = (indent + 2, item_text)
            sub = [virtual]
            j = i + 1
            while j < len(lines) and lines[j][0] > indent:
                sub.append(lines[j]); j += 1
            val, _ = _parse_block(sub, 0, indent + 2)
            seq.append(val); i = j
        return seq, i
    mapping = {}
    while i < len(lines) and lines[i][0] == indent and not lines[i][1].startswith("- "):
        text = lines[i][1]
        key, sep, rest = text.partition(":")
        if not sep: raise MiniYAMLError(f"expected 'key: value', got: {text!r}")
        key = _scalar(key)
        rest = rest.strip()
        if rest:
            mapping[key] = _scalar(rest); i += 1
        else:
            if i + 1 < len(lines) and lines[i + 1][0] > indent:
                val, i = _parse_block(lines, i + 1, lines[i + 1][0])
                mapping[key] = val
            else:
                mapping[key] = None; i += 1
    return mapping, i

def load(text):
    lines = _lines(text)
    if not lines: return None
    val, _ = _parse_block(lines, 0, lines[0][0])
    return val
