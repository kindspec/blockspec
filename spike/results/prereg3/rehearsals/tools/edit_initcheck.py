import sys

f = sys.argv[1]
s = open(f).read()
a = '''        checked = agent_cmd != "claude"
        for line in p.stdout:
            log(line.rstrip("\\n"))
            if not checked:
                try:
                    ev = json.loads(line)
                except ValueError:
                    ev = None
                if isinstance(ev, dict) and ev.get("type") == "system" and ev.get("subtype") == "init":
                    checked = True
                    tools, mcp = sorted(ev.get("tools") or []), ev.get("mcp_servers")
                    if tools != INIT_TOOLS or mcp != []:
                        log(f"INIT CHECK FAILED: tools {tools}, mcp_servers {mcp}; stopping the agent")
                        p.terminate()
                    else:
                        log(f"init check: tools {tools}, mcp_servers []")'''
b = '''        checked = False  # round 2, L-b: stubs are checked too
        for line in p.stdout:
            log(line.rstrip("\\n"))
            if not checked:
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue  # not JSON; the first JSON event decides
                checked = True
                if not (isinstance(ev, dict) and ev.get("type") == "system" and ev.get("subtype") == "init"):
                    log("INIT CHECK FAILED: the first JSON event is not system/init; stopping the agent")
                    p.terminate()
                    continue
                tools, mcp = sorted(ev.get("tools") or []), ev.get("mcp_servers")
                if tools != INIT_TOOLS or mcp != []:
                    log(f"INIT CHECK FAILED: tools {tools}, mcp_servers {mcp}; stopping the agent")
                    p.terminate()
                else:
                    log(f"init check: tools {tools}, mcp_servers []")
        if not checked:
            log("INIT CHECK FAILED: the stream ended with no init event")'''
assert s.count(a) == 1, s.count(a)
open(f, "w").write(s.replace(a, b))
print("ok")
