"""
Aligned Helius API Client - Fixed to work with data processor and export handler
"""

import requests
import time
from typing import Optional, Dict, List
from datetime import datetime


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
                        until: Optional[str] = None, limit: int = 100, 
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
        limit = min(max(limit, 1), 100)  # Enforce 1-100 range
        
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
        
        try:
            print(f"Making request to: {url}")
            print(f"With parameters: {params}")
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            actual_url = response.url if response else url
            print(f"Request failed with URL: {actual_url}")
            raise Exception(f"Helius API error: {str(e)}")
    
    def get_all_transactions(self, address: str, start_date: datetime, 
                           end_date: datetime, max_transactions: int = 5000) -> List[Dict]:
        """Get all transactions using pagination (respecting 100 limit per call)
        
        Args:
            address: Wallet address
            start_date: Start date filter
            end_date: End date filter
            max_transactions: Maximum number of transactions to fetch
            
        Returns:
            List of all transactions (raw, unfiltered)
        """
        all_transactions = []
        before_signature = None
        start_timestamp = int(start_date.timestamp())
        end_timestamp = int(end_date.timestamp())
        
        print(f"Starting transaction fetch with max_transactions={max_transactions}")
        
        while len(all_transactions) < max_transactions:
            try:
                print(f"Fetching batch with before_signature={before_signature}")
                transactions = self.get_transactions(
                    address=address,
                    before=before_signature,
                    limit=100
                )
                
                if not transactions:
                    print("No more transactions found")
                    break
                
                # Filter by date range
                filtered_tx = []
                for tx in transactions:
                    tx_timestamp = tx.get('timestamp', 0)
                    if start_timestamp <= tx_timestamp <= end_timestamp:
                        filtered_tx.append(tx)
                
                all_transactions.extend(filtered_tx)
                print(f"Fetched {len(filtered_tx)} transactions (total: {len(all_transactions)})")
                
                # Check if we've reached the start date
                if transactions and transactions[-1].get('timestamp', 0) < start_timestamp:
                    print("Reached start date, stopping pagination")
                    break
                
                # Check if we got less than 100 (last page)
                if len(transactions) < 100:
                    print("Reached last page")
                    break
                
                # Set up for next iteration
                before_signature = transactions[-1].get('signature')
                
                if not before_signature:
                    print("No signature found for pagination")
                    break
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error fetching batch: {e}")
                break
        
        return all_transactions
    
    def wait_for_rate_limit(self):
        """Enforce rate limiting"""
        time.sleep(0.1)  # 100ms delay for 10 RPS