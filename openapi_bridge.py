import sys
from pathlib import Path

# Ensure infinity-scraper src is in path
CURRENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CURRENT_DIR / "src"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from infinity_scraper.server import mcp

app = FastAPI(
    title="Infinity Scraper Tools",
    description="OpenAPI Tool Server for Open WebUI exposing all 25 InfinityScrape MCP tools",
    version="1.0.0"
)

# Enable CORS so Open WebUI can connect without browser/network restrictions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all 25 MCP tools as OpenAPI endpoints
for tool in mcp._tool_manager.list_tools():
    app.post(f"/{tool.name}", summary=tool.name, description=tool.description)(tool.fn)

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Infinity Scraper OpenAPI Bridge",
        "total_tools": len(mcp._tool_manager.list_tools())
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
