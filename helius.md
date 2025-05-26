
# Prompt: Replace Solscan CSV with Helius API in Streamlit App

I’m building a Streamlit app available at: [https://github.com/Kevinaie18/solscan-export](https://github.com/Kevinaie18/solscan-export), which currently analyzes Solana DeFi transactions from CSV files exported via Solscan.  
I want to fully replace this logic by calling the live **Helius Enhanced Transactions API**:

```python
import requests
url = "https://api.helius.xyz/v0/addresses/{address}/transactions"
response = requests.request("GET", url)
print(response.text)
```

---

## Implementation Objectives

### 1. Replace CSV with `fetch_transactions_from_helius()` function
- This function should accept the following inputs:
  - `wallet_address` (required)
  - `start_date` and `end_date` (as timestamps)
  - `min_usd_value`
  - `transaction_types` (e.g. `["SWAP", "AGGREGATOR_SWAP"]`)
  - `token_mint` (optional; if empty, fetch all swaps regardless of token)
- The function should:
  - Call the Helius endpoint and handle **pagination** via the `before` parameter
  - Return a DataFrame that matches the previous CSV-based structure
  - Apply filters:
    - On transaction type
    - On timeframe
    - On token mint (if specified)
    - On **USD value**, only including transactions above `min_usd_value`

---

### 2. USD Value Calculation
- Extract the transferred amount from `tokenTransfers` or `nativeTransfers`
- Multiply by `usdTokenPrice` (only if it is present in the Helius response)
- Exclude any transaction below the minimum USD threshold
- **Do not use any external pricing API if `usdTokenPrice` is missing** — just skip those transactions

---

### 3. Pagination Handling
- The Helius API returns max 1,000 transactions per request
- Implement a loop using the `before` timestamp of the last transaction in each batch
- Stop fetching when:
  - The `start_date` is reached
  - No more results
  - Or a maximum of 30,000 transactions has been fetched
- Respect the **10 requests per second** limit of the Free Plan

---

### 4. Streamlit Integration
- Remove all CSV upload logic using `st.file_uploader()`
- Update the UI with:
  - Text input: `wallet address`
  - Date selectors: `start date` / `end date`
  - Numeric input: `min USD value`
  - Multiselect: `transaction types` (SWAP, AGGREGATOR_SWAP)
  - Optional text input: `token mint` (leave blank to fetch all)
  - Button: "Analyze transactions"
- Display results using `st.dataframe()` and allow **CSV export**

---

Would you like me to now implement the `fetch_transactions_from_helius()` function and show how to plug it into your Streamlit app?
