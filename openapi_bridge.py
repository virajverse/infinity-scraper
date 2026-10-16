import asyncio
import sys
import inspect
from pathlib import Path
from typing import Any
from pydantic import create_model

# Ensure infinity-scraper src directory is in path
CURRENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CURRENT_DIR / "src"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from infinity_scraper.server import mcp

app = FastAPI(
    title="Infinity Scraper Tools",
    description="OpenAPI Tool Server for Open WebUI exposing all InfinityScrape MCP tools",
    version="2.0.0",
    servers=[
        {"url": "/", "description": "Current Server (Auto-Resolved)"}
    ]

)

# Enable CORS so Open WebUI can connect without browser/network restrictions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# 🛠️ MCP TOOL REGISTRATION (Direct Clean Tool Access)
# =============================================================================
def register_tool_endpoint(tool):
    fn = tool.fn
    sig = inspect.signature(fn)
    tool_name = tool.name

    if not sig.parameters:
        async def no_param_handler():
            try:
                if inspect.iscoroutinefunction(fn):
                    return await asyncio.wait_for(fn(), timeout=120.0)
                return await asyncio.wait_for(asyncio.to_thread(fn), timeout=120.0)
            except asyncio.TimeoutError:
                return {"error": f"Tool '{tool_name}' timed out after 120s"}
            except Exception as e:
                return {"error": f"Tool execution failed: {str(e)}"}
        no_param_handler.__name__ = tool_name
        app.post(f"/{tool_name}", summary=tool_name, description=tool.description)(no_param_handler)
        app.get(f"/{tool_name}", summary=tool_name, description=tool.description)(no_param_handler)
        return

    fields = {}
    for name, param in sig.parameters.items():
        ann = param.annotation if param.annotation != inspect.Parameter.empty else Any
        default = param.default if param.default != inspect.Parameter.empty else ...
        fields[name] = (ann, default)

    ReqModel = create_model(f"{tool_name}_Payload", **fields)

    async def param_handler(payload: ReqModel):
        kwargs = payload.model_dump(exclude_unset=False)
        filtered = {k: v for k, v in kwargs.items() if k in sig.parameters}
        try:
            if inspect.iscoroutinefunction(fn):
                return await asyncio.wait_for(fn(**filtered), timeout=120.0)
            return await asyncio.wait_for(asyncio.to_thread(fn, **filtered), timeout=120.0)
        except asyncio.TimeoutError:
            return {"error": f"Tool '{tool_name}' timed out after 120s"}
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}

    param_handler.__name__ = tool_name
    app.post(f"/{tool_name}", summary=tool_name, description=tool.description)(param_handler)



for tool in mcp._tool_manager.list_tools():
    register_tool_endpoint(tool)


@app.get("/")
def root():
    tools = [t.name for t in mcp._tool_manager.list_tools()]
    return {
        "status": "online",
        "service": "Infinity Scraper OpenAPI Bridge",
        "total_tools": len(tools),
        "tools": tools
    }


@app.get("/health")
def health():
    return {"status": "healthy", "service": "infinity-scraper-openapi-bridge"}


# Tolerance alias for Open WebUI
@app.get("/openapi.json/openapi.json")
def openapi_double_alias():
    return JSONResponse(content=app.openapi())


@app.get("/api/config")
def api_config():
    return {"status": "ok", "service": "infinity-scraper"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

