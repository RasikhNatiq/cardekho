# main.py
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
from typing import Optional
from datetime import datetime
from .caragent import CarCSVAgent
from .schemas import QueryRequest, QueryResponse, DatasetInfo, HealthCheck

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global agent instance
agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global agent
    logger.info("Initializing CarCSVAgent...")
    agent = CarCSVAgent()
    logger.info(f"Agent initialized. Dataset has {len(agent.df)} records.")
    yield
    # Shutdown
    logger.info("Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Car Search API",
    description="API for natural language car search using LLM-powered filtering",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Dependency to get agent instance
def get_agent():
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    return agent

@app.get("/", tags=["Frontend"])
async def root():
    """Serve the frontend HTML."""
    from fastapi.responses import FileResponse
    return FileResponse("static/index.html")

@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "dataset_loaded": agent is not None and len(agent.df) > 0,
        "openrouter_connected": True,  # You might want to add actual connectivity check
        "total_cars": len(agent.df) if agent else None
    }

@app.get("/dataset", response_model=DatasetInfo, tags=["Dataset"])
async def get_dataset_info(agent: CarCSVAgent = Depends(get_agent)):
    """Get information about the loaded dataset."""
    return agent.get_dataset_info()

@app.get("/search", response_model=QueryResponse, tags=["Search"])
async def search_cars(
    q: str = Query(..., description="Natural language query for searching cars"),
    max_results: Optional[int] = Query(100, description="Maximum number of results to return"),
    agent: CarCSVAgent = Depends(get_agent)
):
    """
    Search cars using natural language query.
    
    Example queries:
    - "Find red cars with mileage above 15 km/l"
    - "Show me cars under 10 lakhs"
    - "Toyota cars from 2020"
    - "SUV with automatic transmission"
    """
    try:
        result = agent.query(q)
        # Limit results if needed
        if max_results and len(result["results"]) > max_results:
            result["results"] = result["results"][:max_results]
            result["returned_results"] = max_results
        
        return result
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search", response_model=QueryResponse, tags=["Search"])
async def search_cars_post(
    request: QueryRequest,
    agent: CarCSVAgent = Depends(get_agent)
):
    """
    Search cars using natural language query (POST version).
    
    Use this endpoint for longer queries or when you want to specify max_results.
    """
    try:
        result = agent.query(request.query)
        # Limit results if needed
        if request.max_results and len(result["results"]) > request.max_results:
            result["results"] = result["results"][:request.max_results]
            result["returned_results"] = request.max_results
        
        return result
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api", tags=["API"])
async def api_info():
    """API information."""
    return {
        "message": "Car Search API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "dataset_info": "/dataset",
            "search": "/search",
            "search_get": "/search?q={query}"
        }
    }

# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )