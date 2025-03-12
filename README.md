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
Call Started URL: http://your-server-ip:8000/log?phone={mac}&event=call-start&number={number}&callid={callid}&type={sipaccount}
```
- Triggers when a call begins (outbound or incoming)

```
Incoming Call URL: http://your-server-ip:8000/log?phone={mac}&event=incoming-call&number={remotenumber}&callid={callid}&type={sipaccount}
```
- Triggers specifically when an incoming call is received

```
Call Established URL: http://your-server-ip:8000/log?phone={mac}&event=call-established&number={number}&callid={callid}&type={sipaccount}
```
- Triggers when the call is answered (by either party)

```
Call Ended URL: http://your-server-ip:8000/log?phone={mac}&event=call-end&number={number}&callid={callid}&type={sipaccount}
```
- Triggers when the call finishes

```
Missed Call URL: http://your-server-ip:8000/log?phone={mac}&event=missed-call&number={remotenumber}&callid={callid}&type={sipaccount}
```
- Triggers when an incoming call is not answered

```
Hold URL: http://your-server-ip:8000/log?phone={mac}&event=hold&number={number}&callid={callid}&type={sipaccount}
```
- Triggers when a call is placed on hold

```
Resume URL: http://your-server-ip:8000/log?phone={mac}&event=resume&number={number}&callid={callid}&type={sipaccount}
```
- Triggers when a call is resumed from hold

```
Transfer URL: http://your-server-ip:8000/log?phone={mac}&event=transfer&number={number}&callid={callid}&type={sipaccount}&transfer_to={outgoingnumber}
```
- Triggers when a call is transferred to another extension

```
Attended Transfer URL: http://your-server-ip:8000/log?phone={mac}&event=attended-transfer&number={number}&callid={callid}&type={sipaccount}&transfer_to={outgoingnumber}
```
- Triggers when an attended transfer is completed

```
Transfer Failed URL: http://your-server-ip:8000/log?phone={mac}&event=transfer-failed&number={number}&callid={callid}&type={sipaccount}
```
- Triggers when a transfer attempt fails

### Configuring Cisco Phones

Configure these HTTP Client URLs on each Cisco phone:

```
Call Start URL: http://your-server-ip:8000/log?mac=$MA&event=call-start&number=$CN&callid=$CI
```
- Triggers when a call is initiated

```
Call Connected URL: http://your-server-ip:8000/log?mac=$MA&event=call-connected&number=$CN&callid=$CI
```
- Triggers when the call is answered

```
Call End URL: http://your-server-ip:8000/log?mac=$MA&event=call-end&number=$CN&duration=$CD&callid=$CI
```
- Triggers when the call terminates

```
Call Hold URL: http://your-server-ip:8000/log?mac=$MA&event=call-hold&number=$CN&callid=$CI
```
- Triggers when a call is placed on hold

```
Call Resume URL: http://your-server-ip:8000/log?mac=$MA&event=call-resume&number=$CN&callid=$CI
```
- Triggers when a call is resumed from hold

```
Call Transfer URL: http://your-server-ip:8000/log?mac=$MA&event=call-transfer&number=$CN&callid=$CI&transfer=$TX
```
- Triggers when a call is transferred

### Accessing Reports

- Call Reports: `http://your-server-ip:8000/reports/calls`
- Call Statistics: `http://your-server-ip:8000/reports/stats`

## API Documentation

FastAPI provides automatic API documentation at:
- Swagger UI: `http://your-server-ip:8000/docs`
- ReDoc: `http://your-server-ip:8000/redoc`

## Database Access

You can access the SQLite database directly for advanced queries:

### Using the SQLite CLI

```bash
# If running directly on the host
sqlite3 data/phone_calls.db

# If running in Docker
docker exec -it call-logger sqlite3 /app/data/phone_calls.db
```

Common SQLite commands:
```sql
-- Show all tables
.tables

-- Show schema for calls table
.schema calls

-- Set output format
.mode column
.headers on

-- List recent calls
SELECT * FROM calls ORDER BY started DESC LIMIT 10;

-- Get call statistics
SELECT direction, COUNT(*) as count, AVG(total_duration) as avg_duration
FROM calls
GROUP BY direction;
```

### Testing Syslog (if configured)

To test if syslog is properly receiving events:

```bash
# Send a test message to syslog
logger -n your-server-ip -P 5514 -t TEST "This is a test message"

# Or simulate a phone message
echo '<6>Jan 12 10:15:23 yealink-phone-00:15:65:12:34:56 PHONE: Call established with 1234, call-id: 4d8f62a3@10.0.0.100' | nc -u your-server-ip 5514
```

Check logs to verify receipt:
```bash
docker exec -it syslog-server tail -f /var/log/messages
```

## Performance Considerations

- SQLite can comfortably handle millions of call records
- For optimal performance, consider archiving data older than 6-12 months
- Database queries remain fast up to ~1 million records with proper indexing