"""
Aligned Helius API Client - Fixed to work with data processor and export handler
"""

import requests
import time
from typing import Optional, Dict, List
from datetime import datetime

# Constants
BATCH_SIZE = 100  # Helius API limit per request
MAX_RETRIES = 3   # Maximum number of retries for failed requests

class HeliusClient:
    """Client for interacting with Helius Enhanced Transactions API"""
    
    def __init__(self, api_key: str):
        """Initialize the Helius client
        
        Args:
            api_key: Helius API key
        """
        self.api_key = api_key
        self.base_url = "https://api.helius.xyz/v0"
    
    def get_transactions(self, address: str, before: Optional[str] = None, 
                        until: Optional[str] = None, limit: int = BATCH_SIZE, 
                        commitment: str = "confirmed") -> List[Dict]:
        """Get enhanced transactions for an address (GET method as documented)
        
        Args:
            address: Wallet address (path parameter)
            before: Optional transaction signature to start searching backwards from
            until: Optional transaction signature to search until
            limit: Number of transactions to fetch (1-100, default 100)
            commitment: Transaction commitment level (confirmed/finalized)
            
        Returns:
            List of enhanced transactions
        """
        url = f"{self.base_url}/addresses/{address}/transactions"
        limit = min(max(limit, 1), BATCH_SIZE)  # Enforce 1-100 range
        
        params = {
            "api-key": self.api_key,
            "limit": limit,
            "commitment": commitment
        }
        
        if before:
            params["before"] = before
        if until:
            params["until"] = until
        
        response = None  # Initialize response variable
        retry_count = 0
        
        while retry_count < MAX_RETRIES:
            try:
                print(f"\nMaking request to: {url}")
                print(f"With parameters: {params}")
                
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                if not isinstance(data, list):
                    print(f"Warning: API response is not a list: {type(data)}")
                    print(f"Response content: {data}")
                    return []
                
                print(f"Successfully fetched {len(data)} transactions")
                return data
                
            except requests.exceptions.RequestException as e:
                retry_count += 1
                actual_url = response.url if response else url
                print(f"Request failed (attempt {retry_count}/{MAX_RETRIES})")
                print(f"URL: {actual_url}")
                print(f"Error: {str(e)}")
                
                if retry_count < MAX_RETRIES:
                    wait_time = 2 ** retry_count  # Exponential backoff
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Helius API error after {MAX_RETRIES} attempts: {str(e)}")
    
    def get_all_transactions(self, address: str, start_date: datetime, end_date: datetime, max_transactions: int = 5000) -> List[Dict]:
        """Get all transactions for an address with pagination
        
        Args:
            address: Wallet address
            start_date: Start date for filtering
            end_date: End date for filtering
            max_transactions: Maximum number of transactions to fetch
            
        Returns:
            List of transaction dictionaries
        """
        print(f"\n=== FETCHING ALL TRANSACTIONS ===")
        print(f"Address: {address}")
        print(f"Date range: {start_date} to {end_date}")
        print(f"Max transactions: {max_transactions}")
        
        all_transactions = []
        before = None
        total_fetched = 0
        batch_count = 0
        
        while total_fetched < max_transactions:
            try:
                batch_count += 1
                print(f"\nFetching batch {batch_count}")
                print(f"Using 'before' parameter: {before}")
                
                # Get transactions
                transactions = self.get_transactions(
                    address=address,
                    before=before,
                    limit=BATCH_SIZE
                )
                
                if not transactions:
                    print("No more transactions found")
                    break
                
                print(f"Fetched {len(transactions)} transactions in this batch")
                
                # Debug first transaction in batch
                if transactions:
                    first_tx = transactions[0]
                    print("\nFirst transaction in batch:")
                    print(f"  Signature: {first_tx.get('signature', 'NO_SIGNATURE')}")
                    print(f"  Timestamp: {first_tx.get('timestamp', 'NO_TIMESTAMP')}")
                    print(f"  Type: {first_tx.get('type', 'NO_TYPE')}")
                    print(f"  Source: {first_tx.get('source', 'NO_SOURCE')}")
                    print(f"  Description: {first_tx.get('description', 'NO_DESCRIPTION')}")
                
                # Filter by date
                filtered_transactions = []
                for tx in transactions:
                    timestamp = tx.get('timestamp', 0)
                    if not timestamp:
                        print(f"Warning: Transaction missing timestamp: {tx.get('signature', 'NO_SIGNATURE')}")
                        continue
                        
                    try:
                        tx_date = datetime.fromtimestamp(timestamp)
                        if start_date <= tx_date <= end_date:
                            filtered_transactions.append(tx)
                    except (ValueError, OSError) as e:
                        print(f"Error processing timestamp {timestamp}: {e}")
                        continue
                
                print(f"After date filtering: {len(filtered_transactions)} transactions")
                
                if not filtered_transactions:
                    print("No transactions in date range, stopping pagination")
                    break
                
                all_transactions.extend(filtered_transactions)
                total_fetched = len(all_transactions)
                
                print(f"Total transactions so far: {total_fetched}")
                
                # Update before parameter for next page
                if len(transactions) == BATCH_SIZE:
                    before = transactions[-1].get('signature')
                    if not before:
                        print("Warning: Last transaction missing signature")
                        break
                    print(f"Setting 'before' to: {before}")
                else:
                    print("Last batch received, stopping pagination")
                    break
                
                # Rate limiting
                time.sleep(0.1)  # 100ms delay
                
            except Exception as e:
                print(f"Error fetching transactions: {e}")
                break
        
        print(f"\n=== FETCH COMPLETE ===")
        print(f"Total batches processed: {batch_count}")
        print(f"Total transactions fetched: {len(all_transactions)}")
        
        if all_transactions:
            print("\nFirst transaction:")
            first_tx = all_transactions[0]
            print(f"  Signature: {first_tx.get('signature', 'NO_SIGNATURE')}")
            print(f"  Timestamp: {first_tx.get('timestamp', 'NO_TIMESTAMP')}")
            print(f"  Type: {first_tx.get('type', 'NO_TYPE')}")
            print(f"  Source: {first_tx.get('source', 'NO_SOURCE')}")
            print(f"  Description: {first_tx.get('description', 'NO_DESCRIPTION')}")
            
            print("\nLast transaction:")
            last_tx = all_transactions[-1]
            print(f"  Signature: {last_tx.get('signature', 'NO_SIGNATURE')}")
            print(f"  Timestamp: {last_tx.get('timestamp', 'NO_TIMESTAMP')}")
            print(f"  Type: {last_tx.get('type', 'NO_TYPE')}")
            print(f"  Source: {last_tx.get('source', 'NO_SOURCE')}")
            print(f"  Description: {last_tx.get('description', 'NO_DESCRIPTION')}")
        else:
            print("\nNo transactions were fetched")
        
        return all_transactions
    
    def wait_for_rate_limit(self):
        """Enforce rate limiting"""
        time.sleep(0.1)  # 100ms delay for 10 RPS