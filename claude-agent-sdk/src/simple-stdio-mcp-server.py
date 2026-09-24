import asyncio
from typing import TypedDict
import uuid

from fastmcp import FastMCP
from fastmcp.dependencies import CurrentContext
from fastmcp.server.context import Context

mcp = FastMCP(name="Simple Stdio MCP Server")

class UploadFileResult(TypedDict):
    success: bool
    file_id: uuid.UUID

@mcp.tool
async def upload_file(file_uri:str, ctx:Context = CurrentContext()) -> UploadFileResult:
    await ctx.info(f"Check if the file exists...")
    
    await ctx.info(f"Start uploading the file {file_uri}...")
    for pct in (0,100,5):
        await ctx.report_progress(progress=pct, total=100)
    
    await ctx.info(f"File upload completed!")

    return UploadFileResult(success=True, file_id=uuid.uuid4())

#if __name__ == "__main__":
#    mcp.run(transport="stdio")
