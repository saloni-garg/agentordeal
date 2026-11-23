import json, sys
for line in sys.stdin:
    try: req = json.loads(line)
    except Exception: continue
    rid = req.get("id")
    if rid is None: continue
    sys.stdout.write(json.dumps({"jsonrpc":"2.0","method":"notifications/progress","params":{"note":"working"}})+"\n"); sys.stdout.flush()
    m = req.get("method")
    if m == "initialize": res = {"protocolVersion":"2024-11-05","capabilities":{},"serverInfo":{"name":"noisy","version":"0"}}
    elif m == "tools/list": res = {"tools":[{"name":"echo","description":"echo","inputSchema":{"type":"object"}}]}
    elif m == "tools/call": res = {"content":[{"type":"text","text":"ok"}]}
    else: res = {}
    sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":rid,"result":res})+"\n"); sys.stdout.flush()
