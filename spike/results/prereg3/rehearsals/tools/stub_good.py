#!/usr/bin/python3
import sys, json
print(json.dumps({"type": "system", "subtype": "init", "tools": ["Edit","Glob","Grep","Read","Write"], "mcp_servers": []}))
print("done")
