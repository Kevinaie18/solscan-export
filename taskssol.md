
# Tasks: Replace Solscan CSV Logic with Helius API in Streamlit App

## 1. Remove Existing CSV Parsing
- [ ] Delete or comment out all logic using `st.file_uploader()` and `pandas.read_csv()`
- [ ] Remove CSV sample file and related test logic if any

## 2. Create `fetch_transactions_from_helius()` Function
- [ ] Define function with parameters: `wallet_address`, `start_date`, `end_date`, `min_usd_value`, `transaction_types`, `token_mint`
- [ ] Use `requests` to call `https://api.helius.xyz/v0/addresses/{address}/transactions`
- [ ] Implement pagination using `before` parameter (max 30,000 transactions or until start_date)
- [ ] Respect 10 RPS limit (add delay if needed)
- [ ] Return transactions as a cleaned pandas DataFrame

## 3. Implement USD Value Filtering
- [ ] From each transaction, extract relevant `tokenTransfers` or `nativeTransfers`
- [ ] Multiply amount by `usdTokenPrice` **if and only if it exists**
- [ ] Exclude transactions without `usdTokenPrice`
- [ ] Exclude transactions below `min_usd_value`

## 4. Update Streamlit UI
- [ ] Add inputs: `wallet address`, `start date`, `end date`, `min USD value`, `transaction types`, `token mint` (optional)
- [ ] Add "Analyze transactions" button
- [ ] Display resulting DataFrame in the UI
- [ ] Add CSV export button

## 5. Test and Debug
- [ ] Test with a known wallet and sample token
- [ ] Ensure pagination works across large datasets
- [ ] Validate filtering logic and edge cases
- [ ] Confirm app respects API rate limits

## 6. Optional Enhancements
- [ ] Add progress bar for large downloads
- [ ] Handle API errors and rate limiting gracefully
