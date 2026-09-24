# Start HTTP-SSE MCP server
```bash
fastmcp run src/simple-stdio-mcp-server.py --transport http --host localhost --port 8080
``` 

## MCP Client - Initialize Request
```json
{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "roots": {
                "listChanged": true
            }
        },
        "clientInfo": {
            "name": "MCP Demo Client",
            "version": "1.0.0"
        }
    }
}
```
## MCP Client - Initialized Notification
```json
{
    "jsonrpc": "2.0",
    "method": "notifications/initialized",
    "params": {}
}
```
## MCP Client - Initialized Notification
```json
{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "upload_file",
        "arguments": {
            "file_uri": "abc.txt"
        }
    }
}
```


```bash
# MCP client first POST initialize request to server
curl -v -X POST -N -s \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  --data "@mcp-messages/init-request.json" \
  http://localhost:8080/mcp

# after received the init-response, the client POST initialize noti with mcp-session-id header
curl -v -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json,text/event-stream" \
  -H "mcp-session-id: 2343cf2f1b2f4847b2ae019409731bc4" \
  --data "@mcp-messages/init-notification.json" \
  http://localhost:8080/mcp

# then it make a tools/call request
curl -v -N -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json,text/event-stream" \
  -H "mcp-session-id: 2343cf2f1b2f4847b2ae019409731bc4" \
  --data "@mcp-messages/upload-file-request.json" \
  http://localhost:8080/mcp
```