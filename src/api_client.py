"""
Helius API Client for DeFi transaction data
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
        self.headers = {
            "User-Agent": "DeFi-Export-Tool/1.0"
        }
    
    def get_transactions(self, address: str, before: Optional[str] = None, 
                        limit: int = 1000) -> List[Dict]:
        """Get transactions for an address
        
        Args:
            address: Wallet address
            before: Optional timestamp to fetch transactions before
            limit: Number of transactions to fetch (max 1000)
            
        Returns:
            List of transactions
        """
        url = f"{self.base_url}/addresses/{address}/transactions"
        
        params = {
            "api-key": self.api_key,
            "limit": min(limit, 1000)  # Helius max is 1000
        }
        
        if before:
            params["before"] = before
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def get_all_transactions(self, address: str, start_date: datetime, 
                           end_date: datetime, max_transactions: int = 30000) -> List[Dict]:
        """Get all transactions using pagination
        
        Args:
            address: Wallet address
            start_date: Start date filter
            end_date: End date filter
            max_transactions: Maximum number of transactions to fetch
            
        Returns:
            List of all transactions
        """
        all_transactions = []
        before = None
        start_timestamp = int(start_date.timestamp())
        
        while len(all_transactions) < max_transactions:
            # Make API request
            transactions = self.get_transactions(
                address=address,
                before=before,
                limit=1000
            )
            
            # Check if we have data
            if not transactions:
                break
            
            # Filter by date
            filtered_tx = [
                tx for tx in transactions 
                if start_timestamp <= tx.get('timestamp', 0) <= int(end_date.timestamp())
            ]
            
            all_transactions.extend(filtered_tx)
            
            # Check if we've reached the start date
            if not filtered_tx or filtered_tx[-1].get('timestamp', 0) < start_timestamp:
                break
            
            # Set up for next iteration
            before = str(filtered_tx[-1].get('timestamp', 0))
            
            # Rate limiting (10 requests per second)
            time.sleep(0.1)  # 100ms delay
        
        return all_transactions
    
    def wait_for_rate_limit(self):
        """Enforce rate limiting"""
        time.sleep(0.1)  # 100ms delay for 10 RPS limit 