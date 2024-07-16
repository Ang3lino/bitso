
# Bitso Data Engineering Challenges

Welcome to the Bitso repository where we discuss and provide solutions for each of the challenges presented.

## Challenge 1: Real-time Data Streaming

### Objective
The goal of this challenge is to monitor the bid-ask spread from the Bitso exchange's order books (MXN_BTC and USD_MXN). We need to perform custom analysis on the bid-ask spread and create alerts whenever the spread exceeds predefined thresholds.

### Implementation Details
To achieve this, we utilized functions defined in `dags/spread_functions.py`:
- **Fetch Data**: Fetches bid-ask spread data from the Bitso API.
- **Transform Data**: Computes the spread percentage and prepares it for storage.
- **Prepare Partitioned Directory**: Organizes data into a directory structure suitable for storage in S3.

### Testing
Unit tests for these functions are available in `tests/bid_ask_dag.py` and can be executed using `pytest`.

### Orchestration Logic
Every 10 minutes, the `etl_ticker` DAG is triggered. During each run:
- Data is fetched and transformed from the `get_ticker` API endpoint.
- Transformed data is stored in the `bucket/get_ticker` directory.

### Running the Orchestration
To run the orchestration, execute the following commands:

```bash
docker-compose -f compose.yml up -d
docker-compose -f compose.yml up -d
```

Access Airflow in your web browser at `localhost:8080`. Navigate to the `etl_ticker` DAG. Refer to `compose.yml` for credentials. Security can be improved.
