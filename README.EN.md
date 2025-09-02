<div align="center">

English | [中文](README.md)

</div>

# Data Collection API Service

A FastAPI-based multi-group data collection service that periodically collects JSON data from external APIs and provides circular playback functionality.

## Features

- 🚀 **Multi-Group Data Collection**: Support simultaneous collection of multiple data groups, each independently managed
- 🔄 **Circular Playback**: Each data group has an independent playback index for circular data retrieval
- 💾 **Data Persistence**: Local storage of all collected data using SQLite database
- ⚡ **Asynchronous Processing**: High-performance asynchronous processing based on FastAPI and asyncio
- 🎛️ **Flexible Control**: Support manual start/stop collection with real-time status monitoring
- 📊 **Detailed Statistics**: Complete data statistics and status information
- 🔌 **RESTful API**: Complete REST API interface, easy to integrate

## System Requirements

- **Python**: 3.7+ (Python 3.8 or higher recommended)
- **Dependencies**: See `requirements.txt`

## Installation and Setup

### 1. Clone or Download Project Files

Ensure you have the following files:
- `main.py` - Main program file
- `requirements.txt` - Dependencies list
- `README.md` - Documentation (Chinese)
- `README.EN.md` - Documentation (English)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install fastapi==0.104.1 uvicorn==0.24.0 aiohttp==3.9.1
```

### 3. Configuration

- Find the configuration lines at the top of `main.py`
- Make sure to modify `API_URL` to your data source API

### 4. Start the Service

```bash
python main.py
```

The service will start at `http://localhost:8000`.

## API Documentation

### Basic Information

- **Service URL**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Data Format**: JSON
- **Data Source**: https://www.example.com

### Core Endpoints

#### 1. Collection Control

| Method | Path | Description |
|--------|------|-------------|
| POST | `/start/{group_id}` | Start data collection for specified group |
| POST | `/start` | Start data collection for group 1 (default) |
| POST | `/stop/{group_id}` | Stop data collection for specified group |
| POST | `/stop` | Stop data collection for group 1 (default) |

#### 2. Data Playback

| Method | Path | Description |
|--------|------|-------------|
| GET | `/current/{group_id}` | Get current data for specified group (circular) |
| GET | `/current` | Get current data for group 1 (default) |

#### 3. Data Query

| Method | Path | Description |
|--------|------|-------------|
| GET | `/all/{group_id}` | Get all data for specified group |
| GET | `/all` | Get all data for all groups |

#### 4. Status Monitoring

| Method | Path | Description |
|--------|------|-------------|
| GET | `/status/{group_id}` | Get collection status for specified group |
| GET | `/status` | Get collection status for all groups |
| GET | `/groups` | Get list of groups with data |
| GET | `/stats` | Get global statistics |

#### 5. Other Functions

| Method | Path | Description |
|--------|------|-------------|
| POST | `/collect` | Manually trigger one data collection (for testing) |
| GET | `/` | Get API endpoint list |

## Usage Examples

### Basic Operation Flow

1. **Start the Service**
   ```bash
   python main.py
   ```

2. **Start Data Collection**
   ```bash
   # Start group 1 data collection
   curl -X POST http://localhost:8000/start/1
   
   # Start group 2 data collection
   curl -X POST http://localhost:8000/start/2
   ```

3. **Get Data (Circular Playback)**
   ```bash
   # Get current data for group 1
   curl http://localhost:8000/current/1
   
   # Call again to get the next data
   curl http://localhost:8000/current/1
   ```

4. **Check Status**
   ```bash
   # Check status of all groups
   curl http://localhost:8000/status
   
   # Check status of group 1
   curl http://localhost:8000/status/1
   ```

5. **Stop Collection**
   ```bash
   # Stop collection for group 1
   curl -X POST http://localhost:8000/stop/1
   ```

### Advanced Use Cases

#### Multi-Group Parallel Collection
```bash
# Start multiple group collections simultaneously
curl -X POST http://localhost:8000/start/1
curl -X POST http://localhost:8000/start/2
curl -X POST http://localhost:8000/start/3

# Get data from different groups in parallel
curl http://localhost:8000/current/1 &
curl http://localhost:8000/current/2 &
curl http://localhost:8000/current/3 &
```

#### Data Statistics and Monitoring
```bash
# Get detailed statistics
curl http://localhost:8000/stats

# Get group list and details
curl http://localhost:8000/groups

# Get all historical data for a specific group
curl http://localhost:8000/all/1
```

## Configuration

### Configurable Parameters

You can modify the following configurations at the top of `main.py`:

```python
# Configuration
API_URL = "https://www.example.com"  # Data source API URL
DB_PATH = "data_collection.db"       # Database file path
COLLECT_INTERVAL = 1                 # Collection interval (seconds)
```

### Service Configuration

```python
# Modify in if __name__ == "__main__":
uvicorn.run(
    "main:app",
    host="0.0.0.0",    # Listen address
    port=8000,         # Listen port
    reload=False,      # Hot reload
    log_level="info"   # Log level
)
```

## Data Storage

### Database Structure

Uses SQLite database to store collected data with the following table structure:

```sql
CREATE TABLE collected_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL DEFAULT 1,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    data TEXT NOT NULL
);
```

### Data Files

- **Database File**: `data_collection.db`
- **Location**: Same directory as main program
- **Format**: SQLite 3

## Response Format

### Success Response Examples

#### Get Current Data
```json
{
  "group_id": 1,
  "current_data": {
    "id": 1,
    "group_id": 1,
    "timestamp": "2025-09-02 10:30:00",
    "data": { /* Original API data */ }
  },
  "next_update": "Next call will return the next data"
}
```

#### Status Information
```json
{
  "group_id": 1,
  "is_collecting": true,
  "total_records": 150,
  "current_index": 5,
  "status": "collecting"
}
```

#### Group List
```json
{
  "available_groups": [1, 2, 3],
  "group_details": [
    {
      "group_id": 1,
      "total_records": 150,
      "current_index": 5,
      "is_collecting": true,
      "latest_record": "2025-09-02 10:30:00"
    }
  ]
}
```

### Error Response Example

```json
{
  "detail": "No collected data for group 1"
}
```

## FAQ

### Q: How to modify collection interval?
A: Modify the `COLLECT_INTERVAL` variable in `main.py`, unit is seconds.

### Q: Will data automatically loop playback?
A: Yes, when reaching the last data record, the next call will automatically start from the first record.

### Q: How many groups can be collected simultaneously?
A: Theoretically no limit, but it's recommended to decide based on system performance and target API load capacity.

### Q: How to backup data?
A: Simply copy the `data_collection.db` file.

### Q: How to clear data for a specific group?
A: You can directly operate the SQLite database:
```sql
DELETE FROM collected_data WHERE group_id = 1;
```

### Q: Will data be lost if the service exits abnormally?
A: No, all data is saved in the SQLite database and will still be available after restarting the service.

## Development and Extension

### Project Structure
```
dataCollect/
├── main.py              # Main program file
├── requirements.txt     # Dependencies list
├── README.md           # Documentation (Chinese)
├── README.EN.md        # Documentation (English)
└── data_collection.db  # Database file (generated after running)
```

## License

MIT License

---