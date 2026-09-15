"""
FSOC Coarse Alignment Simulator — FastAPI Backend Server.
Team PHARO — SIH26169
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.scenario import router as scenario_router
from .api.world import router as world_router
from .api.camera import router as camera_router
from .api.disturbance import router as disturbance_router
from .api.detection import router as detection_router
from .api.tracking import router as tracking_router
from .api.error import router as error_router
from .core.state import simulator_state

app = FastAPI(
    title="FSOC Coarse Alignment Simulator API",
    description="Software-only Free-Space Optical Communication Coarse Alignment Simulator — Team PHARO (SIH26169)",
    version="0.7.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration for React Frontend (Vite runs on port 5173 / localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits local React dev servers on any port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include scenario, world, camera, disturbance, detection, tracking, and error routes directly at root and under /api/v1 for maximum client compatibility
app.include_router(scenario_router, prefix="")
app.include_router(scenario_router, prefix="/api/v1")
app.include_router(world_router, prefix="")
app.include_router(world_router, prefix="/api/v1")
app.include_router(camera_router, prefix="")
app.include_router(camera_router, prefix="/api/v1")
app.include_router(disturbance_router, prefix="")
app.include_router(disturbance_router, prefix="/api/v1")
app.include_router(detection_router, prefix="")
app.include_router(detection_router, prefix="/api/v1")
app.include_router(tracking_router, prefix="")
app.include_router(tracking_router, prefix="/api/v1")
app.include_router(error_router, prefix="")
app.include_router(error_router, prefix="/api/v1")


@app.get("/", tags=["System"])
def root():
    """Simulator API Root & Status."""
    return {
        "project": "FSOC Coarse Alignment Simulator",
        "team": "Team PHARO — SIH26169",
        "modules": [
            "Module 1: Scenario Configuration",
            "Module 2: Virtual World & Platform Simulation",
            "Module 3: Virtual Camera & Image Generation",
            "Module 4: Disturbance & Noise Simulation",
            "Module 5: Beacon Detection & Centroiding",
            "Module 6: Beacon Tracking & Motion Prediction",
            "Module 7: Error Calculation & Alignment",
        ],
        "version": "0.7.0",
        "status": "ONLINE",
        "docs_url": "/docs",
    }



@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint for container / orchestrator probes."""
    return {
        "status": "healthy",
        "simulator_lifecycle": simulator_state.get_status()["status"],
    }
