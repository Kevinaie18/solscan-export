"""
Data processing functions for DeFi transactions
"""

import pandas as pd
from datetime import datetime
from typing import List, Dict


def filter_by_date(transactions: List[Dict], start_date: datetime, end_date: datetime) -> List[Dict]:
    """Filter transactions by date range
    
    Args:
        transactions: List of transaction dictionaries
        start_date: Start date filter
        end_date: End date filter
        
    Returns:
        Filtered list of transactions
    """
    filtered = []
    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())
    
    for tx in transactions:
        tx_timestamp = tx.get('blockTime', 0)
        if start_timestamp <= tx_timestamp <= end_timestamp:
            filtered.append(tx)
    
    return filtered


def filter_by_value(transactions: List[Dict], min_usd: float, max_usd: float) -> List[Dict]:
    """Filter transactions by USD value range
    
    Args:
        transactions: List of transaction dictionaries
        min_usd: Minimum USD value
        max_usd: Maximum USD value (can be float('inf'))
        
    Returns:
        Filtered list of transactions
    """
    filtered = []
    
    for tx in transactions:
        # Get USD value from transaction
        value_usd = 0
        if 'tokenTransfers' in tx:
            transfers = tx['tokenTransfers']
            for transfer in transfers:
                if transfer.get('type') == 'out':
                    value_usd = float(transfer.get('value', 0))
                    break
        
        # Check if value is within range
        if min_usd <= value_usd <= max_usd:
            filtered.append(tx)
    
    return filtered


def filter_by_type(transactions: List[Dict], types: List[str]) -> List[Dict]:
    """Filter transactions by activity type
    
    Args:
        transactions: List of transaction dictionaries
        types: List of activity types to include (e.g., ['swap', 'agg_swap'])
        
    Returns:
        Filtered list of transactions
    """
    filtered = []
    
    for tx in transactions:
        activity_type = tx.get('activity_type', '')
        if activity_type in types:
            filtered.append(tx)
    
    return filtered


def format_for_csv(transactions: List[Dict]) -> pd.DataFrame:
    """Format transactions for CSV export
    
    Args:
        transactions: List of transaction dictionaries
        
    Returns:
        Pandas DataFrame formatted for CSV export
    """
    formatted_data = []
    
    for tx in transactions:
        # Extract basic transaction info
        signature = tx.get('signature', '')
        timestamp = datetime.fromtimestamp(tx.get('blockTime', 0)).isoformat()
        activity_type = tx.get('activityType', '').replace('ACTIVITY_', '').lower()
        
        # Initialize default values
        token_in = ''
        token_out = ''
        amount_in = 0
        amount_out = 0
        value_usd = 0
        protocol = ''
        
        # Extract detailed transaction data
        if 'tokenTransfers' in tx:
            transfers = tx['tokenTransfers']
            
            # Find input and output tokens
            for transfer in transfers:
                if transfer.get('type') == 'in':
                    token_in = transfer.get('symbol', '')
                    amount_in = float(transfer.get('amount', 0))
                elif transfer.get('type') == 'out':
                    token_out = transfer.get('symbol', '')
                    amount_out = float(transfer.get('amount', 0))
                    value_usd = float(transfer.get('value', 0))  # USD value
            
            # Get protocol info
            protocol = tx.get('programName', '')
        
        # Create row for CSV
        row = {
            'signature': signature,
            'timestamp': timestamp,
            'activity_type': activity_type,
            'token_in': token_in,
            'token_out': token_out,
            'amount_in': amount_in,
            'amount_out': amount_out,
            'value_usd': value_usd,
            'protocol': protocol
        }
        
        formatted_data.append(row)
    
    # Create DataFrame with specified columns
    df = pd.DataFrame(formatted_data)
    
    # Ensure all required columns exist
    required_columns = [
        'signature', 'timestamp', 'activity_type', 'token_in', 
        'token_out', 'amount_in', 'amount_out', 'value_usd', 'protocol'
    ]
    
    for col in required_columns:
        if col not in df.columns:
            df[col] = ''
    
    return df[required_columns] 