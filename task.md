# DeFi Transaction Export Tool - One Day Tasks

## Overview
**Target**: Complete MVP in 1 day using Cursor AI  
**Strategy**: Small, specific tasks to minimize hallucination

---

## Task 1: Project Setup

### 1.1 Create File Structure
```
defi-export-tool/
├── app.py
├── src/
│   ├── __init__.py
│   ├── api_client.py
│   ├── data_processor.py
│   └── export_handler.py
├── .streamlit/
│   └── secrets.toml
└── requirements.txt
```

### 1.2 Requirements.txt
```
streamlit==1.28.0
pandas==2.0.3
requests==2.31.0
python-dateutil==2.8.2
```

### 1.3 Secrets Template
```toml
[api]
solscan_key = "your_key_here"
```

---

## Task 2: API Client

### 2.1 Basic SolscanClient Class
```python
# src/api_client.py
import requests
import time

class SolscanClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://public-api.solscan.io"
    
    def get_defi_activities(self, account, from_time, to_time, limit=50, before=None):
        # Return requests.get() response
        pass
```

### 2.2 Rate Limiting Function
```python
def wait_for_rate_limit(self):
    time.sleep(0.2)  # 200ms delay
```

### 2.3 Simple Pagination
```python
def get_all_transactions(self, account, from_time, to_time):
    # Loop through pages using 'before' parameter
    # Return list of all transactions
    pass
```

---

## Task 3: Data Processing

### 3.1 Filter Functions
```python
# src/data_processor.py
def filter_by_date(transactions, start_date, end_date):
    # Filter list by timestamp
    pass

def filter_by_value(transactions, min_usd, max_usd):
    # Filter by value_usd field
    pass

def filter_by_type(transactions, types):
    # Filter by activity_type in ['swap', 'agg_swap']
    pass
```

### 3.2 Data Formatter
```python
def format_for_csv(transactions):
    # Convert to pandas DataFrame with specific columns
    # Return DataFrame
    pass
```

---

## Task 4: CSV Export

### 4.1 CSV Generator
```python
# src/export_handler.py
import pandas as pd
import io

def generate_csv(df):
    # Convert DataFrame to CSV string
    # Return StringIO buffer
    pass
```

### 4.2 Download Function
```python
def create_download_link(csv_data, filename):
    # Create Streamlit download button
    pass
```

---

## Task 5: Streamlit UI

### 5.1 Basic Layout
```python
# app.py
import streamlit as st

st.title("DeFi Transaction Export")

# Wallet input
wallet = st.text_input("Wallet Address")

# Date inputs
start_date = st.date_input("Start Date")
end_date = st.date_input("End Date")
```

### 5.2 Value Filters
```python
col1, col2 = st.columns(2)
with col1:
    min_value = st.number_input("Min USD Value", min_value=0.0)
with col2:
    max_value = st.number_input("Max USD Value", min_value=0.0)
```

### 5.3 Transaction Type
```python
tx_types = st.multiselect(
    "Transaction Types",
    ["swap", "agg_swap"],
    default=["swap", "agg_swap"]
)
```

### 5.4 Export Button
```python
if st.button("Export Transactions"):
    # Call API, process data, generate CSV
    # Show download button
    pass
```

---

## Task 6: Integration

### 6.1 Connect All Components
```python
# In app.py export button handler:
# 1. Create SolscanClient
# 2. Get transactions
# 3. Apply filters
# 4. Generate CSV
# 5. Show download
```

### 6.2 Error Handling
```python
try:
    # API calls
except Exception as e:
    st.error(f"Error: {e}")
```

### 6.3 Progress Bar
```python
progress = st.progress(0)
status = st.empty()
# Update during processing
```

---

## Task 7: Testing & Deploy

### 7.1 Local Test
- Test with real wallet address
- Verify CSV download works
- Check error handling

### 7.2 Deploy to Streamlit Cloud
- Push to GitHub
- Connect to Streamlit Cloud
- Add secrets
- Test live app

---

## Cursor Prompts for Each Task

### For Task 2 (API Client):
```
Create a Python class SolscanClient in src/api_client.py that:
1. Takes api_key in __init__
2. Has get_defi_activities method with params: account, from_time, to_time, limit, before
3. Makes GET request to https://public-api.solscan.io/account/defi/activities
4. Has get_all_transactions method that paginates using 'before' parameter
5. Include 200ms delay between requests
```

### For Task 3 (Data Processing):
```
Create functions in src/data_processor.py:
1. filter_by_date(transactions, start_date, end_date) - filter by timestamp
2. filter_by_value(transactions, min_usd, max_usd) - filter by value_usd
3. filter_by_type(transactions, types) - filter activity_type in types list
4. format_for_csv(transactions) - return pandas DataFrame with columns: signature, timestamp, activity_type, token_in, token_out, amount_in, amount_out, value_usd
```

### For Task 5 (Streamlit UI):
```
Create Streamlit app in app.py with:
1. Title "DeFi Transaction Export"
2. Text input for wallet address
3. Date inputs for start/end date
4. Number inputs for min/max USD value
5. Multiselect for transaction types (swap, agg_swap)
6. Export button that processes and shows download
7. Progress bar and status messages
8. Error handling with st.error()
```

---

## Critical Success Criteria

✅ **API calls work** - Can fetch transactions from Solscan  
✅ **Filtering works** - Date, value, type filters apply correctly  
✅ **CSV exports** - Downloads working CSV file  
✅ **UI functional** - All inputs work, no crashes  
✅ **Deploys** - Works on Streamlit Cloud  

Keep each task focused and test immediately after completion.