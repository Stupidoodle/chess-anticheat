import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chess.engine
from typing import List, Optional, Dict
import structlog
from prometheus_client import Counter, Histogram, start_http_server
from contextlib import asynccontextmanager

# Configure logging
logger = structlog.get_logger()

# Configure metrics
ANALYSIS_DURATION = Histogram(
    "engine_analysis_duration_seconds", "Time spent on position analysis", ["depth"]
)
ENGINE_ERRORS = Counter("engine_errors_total", "Total number of engine errors")


class AnalysisRequest(BaseModel):
    fen: str
    depth: Optional[int] = 20
    multipv: Optional[int] = 1
    time_limit: Optional[float] = None


class AnalysisResponse(BaseModel):
    moves: List[Dict]
    depth: int
    time: float
    nodes: int
    score: float


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialization
    logger.info("Starting application...")
    try:
        # Start Prometheus metrics server
        start_http_server(8000)

        # Initialize the Stockfish engine
        transport, engine = await chess.engine.popen_uci("/usr/local/bin/stockfish")
        await engine.configure(
            {
                "Threads": int(os.getenv("ENGINE_THREADS", 2)),
                "Hash": int(os.getenv("MAX_HASH_SIZE", 1024)),
            }
        )

        app.state.engine = engine
        logger.info("Engine and metrics server initialized")
        yield
    except Exception as e:
        logger.error("Error during initialization", error=str(e))
        raise
    finally:
        # Cleanup
        if app.state.engine:
            await app.state.engine.quit()
            logger.info("Engine shut down")


# Initialize FastAPI application with lifespan
app = FastAPI(title="Chess Engine Service", lifespan=lifespan)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if not getattr(app.state, "engine", None):
        raise HTTPException(status_code=503, detail="Engine not initialized")
    return {"status": "healthy"}


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_position(request: AnalysisRequest):
    """Analyze a chess position."""
    engine = getattr(app.state, "engine", None)
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")

    try:
        board = chess.Board(request.fen)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid FEN string")

    try:
        with ANALYSIS_DURATION.labels(depth=request.depth).time():
            results = await engine.analyse(
                board,
                chess.engine.Limit(depth=request.depth, time=request.time_limit),
                multipv=request.multipv,
            )

        # Process analysis results
        moves = []
        for result in results:
            moves.append(
                {
                    "move": result.get("pv")[0].uci(),
                    "score": result.get("score").relative.score(mate_score=10000),
                    "mate": result.get("score").relative.mate(),
                    "pv": [move.uci() for move in result.get("pv")[:5]],
                }
            )

        return AnalysisResponse(
            moves=moves,
            depth=results[0]["depth"],  # Does this value change on multipv
            time=results[0]["time"],  # Does this value change on multipv
            nodes=results[0]["nodes"],  # Does this value change on multipv
            score=moves[0]["score"],
        )
    except Exception as e:
        ENGINE_ERRORS.inc()
        logger.error("Analysis failed", error=str(e))
        raise HTTPException(status_code=500, detail="Analysis failed")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
