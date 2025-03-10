# Phone Call Logger

A FastAPI application for logging phone call events from Yealink and Cisco SIP phones.

## Features

- Captures call events via Action URLs and HTTP callbacks
- Tracks incoming and outgoing calls
- Records call duration, status, and other statistics
- Provides reporting endpoints
- Supports both Yealink and Cisco SIP phones

## Project Structure

```
call_logger/
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI application entry point
│   ├── config.py          # Configuration settings
│   ├── database.py        # Database connection setup
│   ├── models/            # Database models
│   ├── api/               # API endpoints
│   ├── services/          # Business logic
│   └── utils/             # Utility functions
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Requirements

- Python 3.11+
- FastAPI
- SQLAlchemy
- AIOSQLITE

## Installation

### Using Docker (recommended)

1. Clone the repository
2. Create a data directory: `mkdir -p data`
3. Start the application: `docker-compose up -d`

### Using Python directly

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: 
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a data directory: `mkdir -p data`
6. Run the application: `python -m app.main`

## Usage

### Configuring Yealink Phones

Configure these Action URLs on each Yealink phone:

```
Call Started: http://your-server:8000/log?phone={mac}&event=call-start&number={number}&callid={callid}
Incoming Call: http://your-server:8000/log?phone={mac}&event=incoming-call&number={remotenumber}&callid={callid}
Call Established: http://your-server:8000/log?phone={mac}&event=call-established&number={number}&callid={callid}
Call Ended: http://your-server:8000/log?phone={mac}&event=call-end&number={number}&callid={callid}
Hold: http://your-server:8000/log?phone={mac}&event=hold&number={number}&callid={callid}
Resume: http://your-server:8000/log?phone={mac}&event=resume&number={number}&callid={callid}
```

### Configuring Cisco Phones

Configure these HTTP Client URLs on each Cisco phone:

```
Call Start URL: http://your-server:8000/log?mac=$MA&event=call-start&number=$CN&callid=$CI
Call Connected URL: http://your-server:8000/log?mac=$MA&event=call-connected&number=$CN&callid=$CI
Call End URL: http://your-server:8000/log?mac=$MA&event=call-end&number=$CN&duration=$CD&callid=$CI
Call Hold URL: http://your-server:8000/log?mac=$MA&event=call-hold&number=$CN&callid=$CI
Call Resume URL: http://your-server:8000/log?mac=$MA&event=call-resume&number=$CN&callid=$CI
```

### Accessing Reports

- Call Reports: `http://your-server:8000/reports/calls`
- Call Statistics: `http://your-server:8000/reports/stats`

## API Documentation

FastAPI provides automatic API documentation at:
- Swagger UI: `http://your-server:8000/docs`
- ReDoc: `http://your-server:8000/redoc`
