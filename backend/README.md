# FSOC Coarse Alignment Simulator — Backend

**Team PHARO — SIH26169**

This service is the core API and orchestration layer for the Free-Space Optical Communication (FSOC) Coarse Alignment Simulator.

## Architecture

```
backend/
├── app/
│   ├── main.py              # FastAPI server, CORS middleware, API routing
│   ├── core/
│   │   └── state.py         # Thread-safe simulator state manager & lifecycle
│   ├── scenario/
│   │   ├── models.py        # Typed Pydantic configuration models
│   │   ├── presets.py       # 7 Predefined scenario presets
│   │   ├── validator.py     # Scenario domain validator
│   │   ├── service.py       # Scenario business logic
│   │   └── factory.py       # Simulation module initialization factory
│   └── api/
│       └── scenario.py      # REST endpoints (/scenario, /scenario/presets, etc.)
└── tests/
    └── test_scenario.py     # Comprehensive test suite (34+ test cases)
```

## Setup & Running

### Requirements
- Python 3.11+
- Dependencies listed in `requirements.txt`

### Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### Start Development Server
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Interactive OpenAPI docs: `http://127.0.0.1:8000/docs`

### Run Test Suite
```bash
pytest tests/ -v
```
