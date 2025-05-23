"""
Solscan API Client for DeFi transaction data
"""

import requests
import time
from typing import Optional, Dict, List


class SolscanClient:
    """Client for interacting with Solscan public API"""
    
    def __init__(self, api_key: str):
        """Initialize the Solscan client
        
        Args:
            api_key: Solscan API key
        """
        self.api_key = api_key
        self.base_url = "https://pro-api.solscan.io/v2.0"
        self.headers = {
            "token": api_key,
            "User-Agent": "DeFi-Export-Tool/1.0"
        }
    
    def get_defi_activities(self, account: str, from_time: int, to_time: int, 
                           page: int = 1, page_size: int = 100) -> Dict:
        """Get DeFi activities for an account
        
        Args:
            account: Wallet address
            from_time: Start timestamp (Unix)
            to_time: End timestamp (Unix)
            page: Page number for pagination
            page_size: Number of transactions per page
            
        Returns:
            API response data
        """
        url = f"{self.base_url}/token/defi/activities"
        
        params = {
            "address": account,
            "activity_type[]": ["ACTIVITY_TOKEN_SWAP", "ACTIVITY_AGG_TOKEN_SWAP"],
            "page": page,
            "page_size": page_size,
            "sort_by": "block_time",
            "sort_order": "desc"
        }
        
        # Add time range if specified
        if from_time:
            params["from_time"] = from_time
        if to_time:
            params["to_time"] = to_time
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def get_all_transactions(self, account: str, from_time: int, to_time: int) -> List[Dict]:
        """Get all transactions using pagination
        
        Args:
            account: Wallet address
            from_time: Start timestamp (Unix)
            to_time: End timestamp (Unix)
            
        Returns:
            List of all transactions
        """
        all_transactions = []
        page = 1
        
        while True:
            # Make API request
            response = self.get_defi_activities(
                account=account,
                from_time=from_time,
                to_time=to_time,
                page=page,
                page_size=100
            )
            
            # Check if we have data
            if not response.get('data'):
                break
            
            transactions = response['data']
            all_transactions.extend(transactions)
            
            # Check if we've reached the end
            if len(transactions) < 100:
                break
            
            # Set up for next iteration
            page += 1
            
            # Rate limiting
            self.wait_for_rate_limit()
            
            # Safety break to prevent infinite loops
            if len(all_transactions) > 10000:
                break
        
        return all_transactions
    
    def wait_for_rate_limit(self):
        """Enforce rate limiting"""
        time.sleep(0.2)  # 200ms delay 