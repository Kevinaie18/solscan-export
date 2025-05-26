"""
Corrected data processing functions for Helius Enhanced Transactions API
Based on official Helius documentation
"""

import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional

# Constants for batch processing
BATCH_SIZE = 100  # Helius API limit
MAX_TRANSACTIONS = 5000  # Maximum transactions to process

def safe_get(obj: Optional[Dict], key: str, default=None):
    """Safely get value from dictionary that might be None"""
    if obj is None:
        return default
    return obj.get(key, default)

def filter_by_date(transactions: List[Dict], start_date: datetime, end_date: datetime) -> List[Dict]:
    """Filter transactions by date range
    
    Args:
        transactions: List of transaction dictionaries
        start_date: Start date filter
        end_date: End date filter
        
    Returns:
        Filtered list of transactions
    """
    if not transactions:
        return []
    
    filtered = []
    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())
    
    for tx in transactions:
        if tx is None:
            continue
            
        tx_timestamp = safe_get(tx, 'timestamp', 0)
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
    if not transactions:
        return []
    
    filtered = []
    
    for tx in transactions:
        if tx is None:
            continue
            
        value_usd = calculate_transaction_value(tx)
        
        # Check if value is within range
        if min_usd <= value_usd <= max_usd:
            filtered.append(tx)
    
    return filtered

def calculate_transaction_value(tx: Dict) -> float:
    """Calculate USD value of a transaction based on Helius API structure"""
    if tx is None:
        return 0.0
    
    value_usd = 0.0
    
    try:
        # Method 1: Check tokenTransfers for USD values
        token_transfers = safe_get(tx, 'tokenTransfers', [])
        if token_transfers:
            for transfer in token_transfers:
                if transfer is None:
                    continue
                
                # Get tokenAmount (this is the actual transferred amount)
                token_amount = safe_get(transfer, 'tokenAmount', 0)
                if token_amount:
                    value_usd += float(token_amount) * 0.1  # Rough estimate since no direct USD value
        
        # Method 2: Check nativeTransfers (SOL transfers)
        native_transfers = safe_get(tx, 'nativeTransfers', [])
        if native_transfers:
            for transfer in native_transfers:
                if transfer is None:
                    continue
                
                amount = safe_get(transfer, 'amount', 0)
                if amount:
                    # Convert lamports to SOL and estimate USD (rough estimate)
                    sol_amount = float(amount) / 1e9
                    value_usd += sol_amount * 100  # Rough SOL price estimate
        
        # Method 3: Fallback - use fee as minimum value indicator
        if value_usd == 0:
            fee = safe_get(tx, 'fee', 0)
            if fee:
                value_usd = float(fee) / 1e9 * 100  # Convert fee to rough USD
    
    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error calculating transaction value: {e}")
        return 0.0
    
    return value_usd

def filter_by_type(transactions: List[Dict], types: List[str]) -> List[Dict]:
    """Filter transactions by activity type
    
    Args:
        transactions: List of transaction dictionaries
        types: List of activity types to include (e.g., ['swap', 'agg_swap'])
        
    Returns:
        Filtered list of transactions
    """
    if not transactions or not types:
        return []
    
    filtered = []
    
    # Normalize input types to lowercase for comparison
    normalized_types = [t.lower() for t in types]
    
    for tx in transactions:
        if tx is None:
            continue
        
        # Get transaction type and source (Helius Enhanced API structure)
        tx_type = safe_get(tx, 'type', '').upper()
        tx_source = safe_get(tx, 'source', '').upper()
        description = safe_get(tx, 'description', '').lower()
        
        # Check if transaction matches requested types
        is_match = False
        
        # Check for regular swaps
        if 'swap' in normalized_types:
            is_match = (
                tx_type in ['SWAP', 'SWAP_EXACT_OUT'] or
                'swap' in description or
                (tx_source in ['RAYDIUM', 'ORCA', 'SERUM', 'SABER', 'MERCURIAL'] and tx_type in ['TRANSFER', 'UNKNOWN'])
            )
        
        # Check for aggregated swaps (Jupiter is the main aggregator)
        if 'agg_swap' in normalized_types or 'aggregated_swap' in normalized_types:
            is_match = is_match or (
                tx_source == 'JUPITER' or  # Jupiter is the main aggregator
                'jupiter' in description or
                'aggregate' in description or
                'route' in description  # Jupiter routes through multiple DEXs
            )
        
        # Also check if user requested both types generically
        if any(t in ['swap', 'agg_swap', 'aggregated_swap'] for t in normalized_types):
            # Include any DEX/AMM transaction that looks like a swap
            dex_sources = ['JUPITER', 'RAYDIUM', 'ORCA', 'SERUM', 'SABER', 'MERCURIAL', 'ALDRIN', 'CREMA', 'LIFINITY']
            if tx_source in dex_sources:
                is_match = True
        
        if is_match:
            filtered.append(tx)
    
    return filtered

def extract_token_info(tx: Dict) -> tuple:
    """Extract token information from Helius Enhanced Transaction
    
    Returns:
        tuple: (token_in, token_out, amount_in, amount_out, value_usd)
    """
    if tx is None:
        return '', '', 0, 0, 0
    
    token_in = ''
    token_out = ''
    amount_in = 0
    amount_out = 0
    value_usd = 0
    
    try:
        # Method 1: Extract from tokenTransfers (primary method for Helius)
        token_transfers = safe_get(tx, 'tokenTransfers', [])
        fee_payer = safe_get(tx, 'feePayer', '')
        
        for transfer in token_transfers:
            if transfer is None:
                continue
                
            from_account = safe_get(transfer, 'fromUserAccount', '')
            to_account = safe_get(transfer, 'toUserAccount', '')
            mint = safe_get(transfer, 'mint', '')
            token_amount = safe_get(transfer, 'tokenAmount', 0)
            
            # Determine if this is input (from fee payer) or output (to fee payer)
            if from_account == fee_payer and not token_in:
                token_in = mint
                amount_in = float(token_amount) if token_amount else 0
            elif to_account == fee_payer and not token_out:
                token_out = mint
                amount_out = float(token_amount) if token_amount else 0
        
        # Method 2: Extract from nativeTransfers (SOL transfers)
        native_transfers = safe_get(tx, 'nativeTransfers', [])
        for transfer in native_transfers:
            if transfer is None:
                continue
                
            from_account = safe_get(transfer, 'fromUserAccount', '')
            to_account = safe_get(transfer, 'toUserAccount', '')
            amount = safe_get(transfer, 'amount', 0)
            
            if from_account == fee_payer and not token_in:
                token_in = 'SOL'
                amount_in = float(amount) / 1e9 if amount else 0
            elif to_account == fee_payer and not token_out:
                token_out = 'SOL'
                amount_out = float(amount) / 1e9 if amount else 0
        
        # Calculate USD value
        value_usd = calculate_transaction_value(tx)
    
    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error extracting token info: {e}")
        return '', '', 0, 0, 0
    
    return token_in, token_out, amount_in, amount_out, value_usd

def format_for_csv(transactions: List[Dict]) -> pd.DataFrame:
    """Format transactions for CSV export using Helius Enhanced API structure
    
    Args:
        transactions: List of transaction dictionaries
        
    Returns:
        Pandas DataFrame formatted for CSV export
    """
    if not transactions:
        return pd.DataFrame(columns=[
            'signature', 'timestamp', 'activity_type', 'token_in', 
            'token_out', 'amount_in', 'amount_out', 'value_usd', 'protocol'
        ])
    
    formatted_data = []
    
    for tx in transactions:
        if tx is None:
            continue
            
        try:
            # Extract basic transaction info from Helius Enhanced API
            signature = safe_get(tx, 'signature', '')
            timestamp_raw = safe_get(tx, 'timestamp', 0)
            
            # Convert timestamp safely
            try:
                timestamp = datetime.fromtimestamp(timestamp_raw).isoformat()
            except (ValueError, OSError):
                timestamp = datetime.now().isoformat()
            
            # Get transaction type and source (Helius Enhanced API fields)
            activity_type = safe_get(tx, 'type', 'UNKNOWN')
            source = safe_get(tx, 'source', 'UNKNOWN')
            description = safe_get(tx, 'description', '')
            
            # Extract token information
            token_in, token_out, amount_in, amount_out, value_usd = extract_token_info(tx)
            
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
                'protocol': source,
                'description': description
            }
            
            formatted_data.append(row)
            
        except Exception as e:
            print(f"Error processing transaction {safe_get(tx, 'signature', 'unknown')}: {str(e)}")
            continue
    
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

def validate_transactions(transactions: List[Dict]) -> List[Dict]:
    """Validate and clean transaction data from Helius Enhanced API
    
    Args:
        transactions: Raw transaction list
        
    Returns:
        Cleaned transaction list
    """
    if not transactions:
        return []
    
    valid_transactions = []
    
    for tx in transactions:
        if tx is None:
            continue
            
        # Check for required fields in Helius Enhanced API response
        signature = safe_get(tx, 'signature')
        timestamp = safe_get(tx, 'timestamp')
        tx_type = safe_get(tx, 'type')
        
        if signature and timestamp and tx_type:
            valid_transactions.append(tx)
        else:
            print(f"Skipping invalid transaction: missing required fields")
    
    return valid_transactions

def get_transaction_summary(transactions: List[Dict]) -> Dict:
    """Get summary statistics for Helius Enhanced transactions
    
    Args:
        transactions: List of transactions
        
    Returns:
        Dictionary with summary statistics
    """
    if not transactions:
        return {
            'total_count': 0,
            'unique_protocols': 0,
            'swap_count': 0,
            'agg_swap_count': 0,
            'total_value_usd': 0,
            'date_range': 'No transactions',
            'transaction_types': []
        }
    
    valid_transactions = [tx for tx in transactions if tx is not None]
    
    if not valid_transactions:
        return {
            'total_count': 0,
            'unique_protocols': 0,
            'swap_count': 0,
            'agg_swap_count': 0,
            'total_value_usd': 0,
            'date_range': 'No valid transactions',
            'transaction_types': []
        }
    
    # Get unique protocols and types
    protocols = set()
    tx_types = set()
    total_value = 0
    timestamps = []
    swap_count = 0
    agg_swap_count = 0
    
    for tx in valid_transactions:
        source = safe_get(tx, 'source', 'UNKNOWN')
        tx_type = safe_get(tx, 'type', 'UNKNOWN')
        description = safe_get(tx, 'description', '').lower()
        
        if source:
            protocols.add(source)
        if tx_type:
            tx_types.add(tx_type)
        
        # Count swap types
        if source == 'JUPITER' or 'jupiter' in description or 'aggregate' in description:
            agg_swap_count += 1
        elif tx_type in ['SWAP', 'SWAP_EXACT_OUT'] or source in ['RAYDIUM', 'ORCA', 'SERUM']:
            swap_count += 1
        
        value = calculate_transaction_value(tx)
        total_value += value
        
        timestamp = safe_get(tx, 'timestamp', 0)
        if timestamp:
            timestamps.append(timestamp)
    
    # Get date range
    if timestamps:
        min_date = datetime.fromtimestamp(min(timestamps)).strftime('%Y-%m-%d')
        max_date = datetime.fromtimestamp(max(timestamps)).strftime('%Y-%m-%d')
        date_range = f"{min_date} to {max_date}"
    else:
        date_range = 'Unknown date range'
    
    return {
        'total_count': len(valid_transactions),
        'unique_protocols': len(protocols),
        'swap_count': swap_count,
        'agg_swap_count': agg_swap_count,
        'total_value_usd': round(total_value, 2),
        'date_range': date_range,
        'transaction_types': list(tx_types),
        'protocols': list(protocols)
    }