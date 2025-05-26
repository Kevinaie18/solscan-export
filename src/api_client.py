"""
Corrected Helius API Client based on official documentation
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
        # Correct URL structure from docs
        url = f"{self.base_url}/addresses/{address}/transactions"
        
        # Ensure limit is within valid range
        limit = min(max(limit, 1), 100)  # Enforce 1-100 range
        
        # Query parameters as documented
        params = {
            "api-key": self.api_key,
            "limit": limit,
            "commitment": commitment
        }
        
        # Add optional pagination parameters
        if before:
            params["before"] = before
        if until:
            params["until"] = until
        
        try:
            # Debug print the actual URL and parameters
            print(f"Making request to: {url}")
            print(f"With parameters: {params}")
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed with URL: {response.url if 'response' in locals() else url}")
            raise Exception(f"Helius API error: {str(e)}")
    
    def get_defi_transactions(self, address: str, before: Optional[str] = None,
                             limit: int = 100) -> List[Dict]:
        """Get DeFi-specific transactions using source filtering
        
        Args:
            address: Wallet address
            before: Optional signature for pagination
            limit: Number of transactions (1-100)
            
        Returns:
            List of DeFi transactions
        """
        # DeFi sources from the documentation
        defi_sources = [
            "JUPITER", "RAYDIUM", "ORCA", "SERUM", "SABER", 
            "MERCURIAL", "STEP_FINANCE", "ALDRIN", "CREMA", 
            "LIFINITY", "CYKURA", "MARINADE", "SENCHA", "SAROS"
        ]
        
        all_defi_transactions = []
        
        # Get transactions and filter for DeFi sources
        transactions = self.get_transactions(address, before, limit=limit)
        
        for tx in transactions:
            # Check if transaction has DeFi sources
            if 'source' in tx and tx['source'] in defi_sources:
                all_defi_transactions.append(tx)
        
        return all_defi_transactions
    
    def get_swap_transactions(self, address: str, before: Optional[str] = None,
                             limit: int = 100) -> List[Dict]:
        """Get swap transactions using type filtering
        
        Args:
            address: Wallet address
            before: Optional signature for pagination
            limit: Number of transactions (1-100)
            
        Returns:
            List of swap transactions
        """
        # Get all transactions
        transactions = self.get_transactions(address, before, limit=limit)
        
        swap_transactions = []
        for tx in transactions:
            # Check transaction type for swaps
            tx_type = tx.get('type', '').upper()
            if 'SWAP' in tx_type or tx_type in ['SWAP', 'SWAP_EXACT_OUT']:
                swap_transactions.append(tx)
        
        return swap_transactions
    
    def get_all_transactions(self, address: str, start_date: datetime, 
                           end_date: datetime, max_transactions: int = 5000) -> List[Dict]:
        """Get all transactions using pagination (respecting 100 limit per call)
        
        Args:
            address: Wallet address
            start_date: Start date filter
            end_date: End date filter
            max_transactions: Maximum number of transactions to fetch
            
        Returns:
            List of all transactions
        """
        all_transactions = []
        before_signature = None
        start_timestamp = int(start_date.timestamp())
        end_timestamp = int(end_date.timestamp())
        
        print(f"Starting transaction fetch with max_transactions={max_transactions}")
        
        while len(all_transactions) < max_transactions:
            try:
                # Get batch of transactions (max 100)
                print(f"Fetching batch with before_signature={before_signature}")
                transactions = self.get_transactions(
                    address=address,
                    before=before_signature,
                    limit=100  # Max allowed by Helius
                )
                
                # Check if we have data
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
                
                # Check if we've reached the start date (transactions are in reverse chronological order)
                if transactions and transactions[-1].get('timestamp', 0) < start_timestamp:
                    print("Reached start date, stopping pagination")
                    break
                
                # Check if we got less than 100 (last page)
                if len(transactions) < 100:
                    print("Reached last page")
                    break
                
                # Set up for next iteration using last transaction signature
                before_signature = transactions[-1].get('signature')
                
                if not before_signature:
                    print("No signature found for pagination")
                    break
                
                # Rate limiting (Helius allows 100 RPS, but being conservative)
                time.sleep(0.1)  # 100ms delay = 10 RPS
                
            except Exception as e:
                print(f"Error fetching batch: {e}")
                break
        
        return all_transactions
    
    def filter_transactions_by_type(self, transactions: List[Dict], 
                                   transaction_types: List[str]) -> List[Dict]:
        """Filter transactions by type
        
        Args:
            transactions: List of transactions
            transaction_types: List of transaction types to include
            
        Returns:
            Filtered transactions
        """
        filtered = []
        for tx in transactions:
            tx_type = tx.get('type', '').upper()
            if any(t.upper() in tx_type for t in transaction_types):
                filtered.append(tx)
        return filtered
    
    def filter_transactions_by_value(self, transactions: List[Dict], 
                                    min_value: float, max_value: float) -> List[Dict]:
        """Filter transactions by USD value
        
        Args:
            transactions: List of transactions
            min_value: Minimum USD value
            max_value: Maximum USD value
            
        Returns:
            Filtered transactions
        """
        filtered = []
        for tx in transactions:
            # Look for USD value in various possible fields
            usd_value = 0
            if 'nativeTransfers' in tx:
                for transfer in tx['nativeTransfers']:
                    usd_value += transfer.get('amount', 0) * 0.000000001  # Convert lamports to SOL
            
            if 'tokenTransfers' in tx:
                for transfer in tx['tokenTransfers']:
                    usd_value += transfer.get('usdValue', 0)
            
            if min_value <= usd_value <= max_value:
                filtered.append(tx)
        
        return filtered
    
    def wait_for_rate_limit(self):
        """Enforce rate limiting"""
        time.sleep(0.1)  # 100ms delay for 10 RPS