import sys
import json

print("✅ Python MCP Server Started", file=sys.stderr)

while True:
    try:
        line = sys.stdin.readline()
        if not line:
            break
            
        request = json.loads(line.strip())
        
        if request.get("method") == "tools/list":
            response = {
                "jsonrpc": "2.0",
                "id": request.get("id", 1),
                "result": {
                    "tools": [
                        {
                            "name": "send_email",
                            "description": "Send an email",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "to": {"type": "string"},
                                    "subject": {"type": "string"},
                                    "body": {"type": "string"}
                                },
                                "required": ["to", "subject", "body"]
                            }
                        }
                    ]
                }
            }
            print(json.dumps(response), flush=True)
            break  # Stop after first request for demo
            
    except Exception as e:
        print(json.dumps({
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32603, "message": str(e)}
        }), flush=True)
        break