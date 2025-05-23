# DeFi Transaction Export Tool - Architecture Documentation

## 1. System Overview

### High-Level Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│                 │    │                  │    │                 │
│   Streamlit     │───▶│  Data Processing │───▶│  Solscan API    │
│   Frontend      │    │     Engine       │    │   Integration   │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│                 │    │                  │    │                 │
│  CSV Export     │    │  Rate Limiting   │    │  Error Handling │
│   Generator     │    │   & Pagination   │    │   & Retry Logic │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Core Components
1. **Streamlit Frontend** - User interface and interaction
2. **API Integration Layer** - Solscan API communication
3. **Data Processing Engine** - Transaction filtering and formatting
4. **Export Manager** - CSV generation and download handling
5. **Rate Limiter** - API call management and throttling

---

## 2. Component Architecture

### 2.1 Streamlit Frontend (`app.py`)
```python
# Main application structure
├── Page Configuration
├── Secrets Management
├── User Input Components
│   ├── Wallet Address Input
│   ├── Date Range Picker
│   ├── Value Range Sliders
│   └── Transaction Type Selector
├── Export Trigger
├── Progress Display
└── Download Interface
```

**Responsibilities:**
- User interface rendering
- Input validation
- Progress tracking display
- File download handling
- Error message display

### 2.2 API Integration Layer (`api_client.py`)
```python
class SolscanClient:
    def __init__(self, api_key: str)
    def get_defi_activities(self, params: dict) -> dict
    def paginate_requests(self, base_params: dict) -> list
    def handle_rate_limit(self) -> None
    def retry_request(self, request_func, max_retries=3) -> dict
```

**Responsibilities:**
- Solscan API communication
- Request pagination handling
- Rate limiting enforcement
- Error handling and retries
- Response data validation

### 2.3 Data Processing Engine (`data_processor.py`)
```python
class TransactionProcessor:
    def filter_transactions(self, transactions: list, filters: dict) -> list
    def format_for_csv(self, transactions: list) -> pandas.DataFrame
    def calculate_usd_values(self, transactions: list) -> list
    def validate_data_quality(self, transactions: list) -> bool
```

**Responsibilities:**
- Transaction filtering by criteria
- Data format standardization
- USD value calculations
- Data quality validation
- Duplicate removal

### 2.4 Export Manager (`export_handler.py`)
```python
class CSVExporter:
    def generate_csv(self, data: pandas.DataFrame) -> io.StringIO
    def create_download_link(self, csv_data: str, filename: str) -> str
    def validate_export_size(self, data: pandas.DataFrame) -> bool
```

**Responsibilities:**
- CSV file generation
- Download link creation
- File size validation
- Temporary file management

---

## 3. Data Flow Architecture

### 3.1 Request Flow
```
User Input → Validation → API Requests → Data Processing → CSV Export → Download
```

### 3.2 Detailed Data Flow
1. **User Input Collection**
   - Wallet address validation
   - Date range verification
   - Value range bounds checking
   - Transaction type selection

2. **API Request Pipeline**
   - Build request parameters
   - Execute paginated requests
   - Handle rate limiting delays
   - Collect all response data

3. **Data Processing Pipeline**
   - Apply user filters
   - Calculate USD values
   - Format data structure
   - Validate data quality

4. **Export Generation**
   - Convert to pandas DataFrame
   - Generate CSV format
   - Create download interface
   - Handle file cleanup

---

## 4. File Structure

```
defi-export-tool/
├── app.py                 # Main Streamlit application
├── src/
│   ├── __init__.py
│   ├── api_client.py      # Solscan API integration
│   ├── data_processor.py  # Data filtering and processing
│   ├── export_handler.py  # CSV export functionality
│   └── utils.py           # Utility functions
├── .streamlit/
│   └── secrets.toml       # API keys and configuration
├── requirements.txt       # Python dependencies
├── README.md             # Setup and usage instructions
└── tests/
    ├── test_api_client.py
    ├── test_data_processor.py
    └── test_export_handler.py
```

---

## 5. Data Models

### 5.1 Input Models
```python
@dataclass
class FilterCriteria:
    wallet_address: str
    start_date: datetime
    end_date: datetime
    min_value_usd: float
    max_value_usd: float
    transaction_types: List[str]  # ['swap', 'agg_swap']

@dataclass
class ApiRequestParams:
    account: str
    fromTime: int
    toTime: int
    limit: int = 50
    before: Optional[str] = None
```

### 5.2 Data Models
```python
@dataclass
class DeFiTransaction:
    signature: str
    timestamp: datetime
    activity_type: str  # 'swap' or 'agg_swap'
    token_in_symbol: str
    token_out_symbol: str
    amount_in: float
    amount_out: float
    value_usd: float
    protocol: str
    wallet_address: str
```

### 5.3 Output Models
```python
# CSV Export Columns
CSV_COLUMNS = [
    'signature',
    'timestamp',
    'activity_type',
    'token_in',
    'token_out', 
    'amount_in',
    'amount_out',
    'value_usd',
    'protocol'
]
```

---

## 6. API Integration Design

### 6.1 Solscan API Endpoints
```python
BASE_URL = "https://public-api.solscan.io"

ENDPOINTS = {
    'defi_activities': '/account/defi/activities',
    'token_meta': '/token/meta'
}
```

### 6.2 Rate Limiting Strategy
```python
class RateLimiter:
    MAX_REQUESTS_PER_SECOND = 5
    RETRY_DELAYS = [1, 2, 4, 8]  # Exponential backoff
    
    def enforce_rate_limit(self):
        time.sleep(0.2)  # 200ms between requests
    
    def handle_429_error(self, retry_count):
        delay = self.RETRY_DELAYS[min(retry_count, len(self.RETRY_DELAYS)-1)]
        time.sleep(delay)
```

### 6.3 Pagination Logic
```python
def paginate_all_transactions(self, base_params):
    all_transactions = []
    before_signature = None
    
    while True:
        params = base_params.copy()
        if before_signature:
            params['before'] = before_signature
            
        response = self.make_request(params)
        
        if not response.get('data'):
            break
            
        transactions = response['data']
        all_transactions.extend(transactions)
        
        if len(transactions) < params['limit']:
            break
            
        before_signature = transactions[-1]['signature']
        self.rate_limiter.enforce_rate_limit()
    
    return all_transactions
```

---

## 7. Error Handling Architecture

### 7.1 Error Categories
```python
class APIError(Exception):
    """Base API error"""
    pass

class RateLimitError(APIError):
    """API rate limit exceeded"""
    pass

class ValidationError(Exception):
    """Input validation error"""
    pass

class ExportError(Exception):
    """CSV export generation error"""
    pass
```

### 7.2 Error Handling Strategy
```python
def robust_api_call(self, request_func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return request_func()
        except RateLimitError:
            self.handle_rate_limit_error(attempt)
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise APIError(f"API call failed after {max_retries} attempts: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
```

---

## 8. Security Architecture

### 8.1 API Key Management
```toml
# .streamlit/secrets.toml
[api]
solscan_key = "your_api_key_here"

[config]
max_export_size = 10000
rate_limit_per_second = 5
```

### 8.2 Input Validation
```python
def validate_wallet_address(address: str) -> bool:
    # Solana address validation (32-44 characters, base58)
    return len(address) >= 32 and len(address) <= 44

def validate_date_range(start_date: datetime, end_date: datetime) -> bool:
    # Max 90 days range for MVP
    max_range = timedelta(days=90)
    return (end_date - start_date) <= max_range

def validate_value_range(min_val: float, max_val: float) -> bool:
    return min_val >= 0 and max_val > min_val
```

---

## 9. Performance Considerations

### 9.1 Memory Management
```python
# Process data in chunks to avoid memory issues
CHUNK_SIZE = 1000

def process_large_dataset(transactions):
    for i in range(0, len(transactions), CHUNK_SIZE):
        chunk = transactions[i:i + CHUNK_SIZE]
        yield process_chunk(chunk)
```

### 9.2 Caching Strategy
```python
# Simple in-memory caching for token metadata
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_token_metadata(token_address):
    return fetch_token_metadata(token_address)
```

### 9.3 Progress Tracking
```python
def export_with_progress(self, total_requests):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, batch in enumerate(self.paginated_requests):
        # Process batch
        progress = (i + 1) / total_requests
        progress_bar.progress(progress)
        status_text.text(f'Processing batch {i+1}/{total_requests}')
```

---

## 10. Deployment Architecture

### 10.1 Streamlit Cloud Configuration
```python
# Streamlit configuration
st.set_page_config(
    page_title="DeFi Transaction Export",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)
```

### 10.2 Dependencies Management
```txt
# requirements.txt
streamlit==1.28.0
pandas==2.0.3
requests==2.31.0
python-dateutil==2.8.2
```

### 10.3 Health Monitoring
```python
def health_check():
    """Basic health check for the application"""
    try:
        # Test API connectivity
        test_response = requests.get(f"{BASE_URL}/health", timeout=5)
        return test_response.status_code == 200
    except:
        return False
```

---

## 11. Scalability Considerations

### 11.1 Current Limitations
- Single-user session processing
- In-memory data processing
- No persistent storage
- Basic error recovery

### 11.2 Future Scalability
- Implement background job processing
- Add Redis for caching
- Database for user sessions
- Kubernetes deployment for scaling

This architecture provides a solid foundation for the MVP while maintaining simplicity and clear separation of concerns. Each component can be developed and tested independently, making the development process more manageable.