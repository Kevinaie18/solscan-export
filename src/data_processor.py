"""
Debug version of data processor with enhanced error handling
"""

import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional, Any

# Constants for batch processing
BATCH_SIZE = 100  # Helius API limit
MAX_TRANSACTIONS = 5000  # Maximum transactions to process

def safe_get(obj: Any, key: str, default=None):
    """Safely get value from object that might be None or not a dict"""
    if obj is None:
        return default
    if not isinstance(obj, dict):
        print(f"Warning: Expected dict but got {type(obj)}: {obj}")
        return default
    return obj.get(key, default)

def debug_transaction_structure(transactions: List[Any]) -> None:
    """Debug function to inspect transaction structure"""
    print(f"=== DEBUGGING TRANSACTION STRUCTURE ===")
    print(f"Transactions type: {type(transactions)}")
    print(f"Transactions length: {len(transactions) if hasattr(transactions, '__len__') else 'No length'}")
    
    if transactions and len(transactions) > 0:
        first_tx = transactions[0]
        print(f"First transaction type: {type(first_tx)}")
        print(f"First transaction content: {first_tx}")
        
        if isinstance(first_tx, dict):
            print(f"First transaction keys: {list(first_tx.keys())}")
        
        # Check a few more transactions
        for i, tx in enumerate(transactions[:3]):
            print(f"Transaction {i}: type={type(tx)}, is_dict={isinstance(tx, dict)}")
    print("=== END DEBUG ===")

def validate_transactions(transactions: Any) -> List[Dict]:
    """Validate and clean transaction data with enhanced debugging
    
    Args:
        transactions: Raw transaction data
        
    Returns:
        Cleaned transaction list
    """
    print(f"=== VALIDATING TRANSACTIONS ===")
    print(f"Input type: {type(transactions)}")
    
    # Handle different input types
    if transactions is None:
        print("Transactions is None")
        return []
    
    if isinstance(transactions, str):
        print(f"Transactions is a string: {transactions[:100]}...")
        return []
    
    if not isinstance(transactions, list):
        print(f"Transactions is not a list, trying to convert: {type(transactions)}")
        try:
            transactions = list(transactions)
        except:
            print("Could not convert to list")
            return []
    
    if not transactions:
        print("Transactions list is empty")
        return []
    
    debug_transaction_structure(transactions)
    
    valid_transactions = []
    
    for i, tx in enumerate(transactions):
        print(f"Processing transaction {i}: type={type(tx)}")
        
        if tx is None:
            print(f"Transaction {i} is None, skipping")
            continue
            
        if not isinstance(tx, dict):
            print(f"Transaction {i} is not a dict: {type(tx)}, content: {tx}")
            continue
            
        # Check for required fields in Helius Enhanced API response
        signature = safe_get(tx, 'signature')
        timestamp = safe_get(tx, 'timestamp')
        tx_type = safe_get(tx, 'type')
        
        print(f"Transaction {i}: signature={signature}, timestamp={timestamp}, type={tx_type}")
        
        if signature and timestamp:
            valid_transactions.append(tx)
        else:
            print(f"Transaction {i} missing required fields: signature={signature}, timestamp={timestamp}")
    
    print(f"Valid transactions: {len(valid_transactions)} out of {len(transactions)}")
    return valid_transactions

def filter_by_date(transactions: List[Dict], start_date: datetime, end_date: datetime) -> List[Dict]:
    """Filter transactions by date range with enhanced error handling"""
    print(f"=== FILTERING BY DATE ===")
    print(f"Input transactions: {len(transactions) if transactions else 0}")
    print(f"Date range: {start_date} to {end_date}")
    
    if not transactions:
        return []
    
    filtered = []
    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())
    
    for i, tx in enumerate(transactions):
        try:
            if not isinstance(tx, dict):
                print(f"Transaction {i} is not a dict: {type(tx)}")
                continue
                
            tx_timestamp = safe_get(tx, 'timestamp', 0)
            
            if not isinstance(tx_timestamp, (int, float)):
                print(f"Transaction {i} has invalid timestamp: {tx_timestamp} (type: {type(tx_timestamp)})")
                continue
                
            if start_timestamp <= tx_timestamp <= end_timestamp:
                filtered.append(tx)
        except Exception as e:
            print(f"Error processing transaction {i} in date filter: {e}")
            continue
    
    print(f"Filtered by date: {len(filtered)} transactions")
    return filtered

def calculate_transaction_value(tx: Dict) -> float:
    """Calculate USD value with enhanced error handling"""
    if not isinstance(tx, dict):
        print(f"calculate_transaction_value: tx is not a dict: {type(tx)}")
        return 0.0
    
    value_usd = 0.0
    
    try:
        # Method 1: Check tokenTransfers
        token_transfers = safe_get(tx, 'tokenTransfers', [])
        if token_transfers and isinstance(token_transfers, list):
            for transfer in token_transfers:
                if not isinstance(transfer, dict):
                    continue
                
                token_amount = safe_get(transfer, 'tokenAmount', 0)
                if token_amount:
                    try:
                        value_usd += float(token_amount) * 0.01
                    except (ValueError, TypeError):
                        continue
        
        # Method 2: Check nativeTransfers
        if value_usd == 0:
            native_transfers = safe_get(tx, 'nativeTransfers', [])
            if native_transfers and isinstance(native_transfers, list):
                for transfer in native_transfers:
                    if not isinstance(transfer, dict):
                        continue
                    
                    amount = safe_get(transfer, 'amount', 0)
                    if amount:
                        try:
                            sol_amount = float(amount) / 1e9
                            value_usd += sol_amount * 100
                        except (ValueError, TypeError):
                            continue
        
        # Method 3: Fallback to fee
        if value_usd == 0:
            fee = safe_get(tx, 'fee', 0)
            if fee:
                try:
                    sol_fee = float(fee) / 1e9
                    value_usd = sol_fee * 100
                except (ValueError, TypeError):
                    pass
    
    except Exception as e:
        print(f"Error calculating transaction value: {e}")
        return 0.0
    
    return value_usd

def filter_by_value(transactions: List[Dict], min_usd: float, max_usd: float) -> List[Dict]:
    """Filter transactions by USD value range with enhanced error handling"""
    print(f"=== FILTERING BY VALUE ===")
    print(f"Input transactions: {len(transactions) if transactions else 0}")
    print(f"Value range: ${min_usd} to ${max_usd}")
    
    if not transactions:
        return []
    
    filtered = []
    
    for i, tx in enumerate(transactions):
        try:
            if not isinstance(tx, dict):
                print(f"Transaction {i} is not a dict in value filter: {type(tx)}")
                continue
                
            value_usd = calculate_transaction_value(tx)
            
            if min_usd <= value_usd <= max_usd:
                filtered.append(tx)
        except Exception as e:
            print(f"Error processing transaction {i} in value filter: {e}")
            continue
    
    print(f"Filtered by value: {len(filtered)} transactions")
    return filtered

def filter_by_type(transactions: List[Dict], types: List[str]) -> List[Dict]:
    """Filter transactions by activity type with enhanced error handling"""
    print(f"=== FILTERING BY TYPE ===")
    print(f"Input transactions: {len(transactions) if transactions else 0}")
    print(f"Requested types: {types}")
    
    if not transactions or not types:
        return []
    
    filtered = []
    normalized_types = [t.lower() for t in types]
    
    for i, tx in enumerate(transactions):
        try:
            if not isinstance(tx, dict):
                print(f"Transaction {i} is not a dict in type filter: {type(tx)}")
                continue
            
            tx_type = safe_get(tx, 'type', '').lower()
            tx_source = safe_get(tx, 'source', '').lower()
            description = safe_get(tx, 'description', '').lower()
            
            is_match = False
            
            # Check for regular swaps
            if 'swap' in normalized_types:
                is_match = (
                    'swap' in tx_type or
                    'swap' in description or
                    (tx_source in ['raydium', 'orca', 'serum', 'saber', 'mercurial'] and 
                     tx_type in ['transfer', 'unknown'])
                )
            
            # Check for aggregated swaps
            if 'agg_swap' in normalized_types or 'aggregated_swap' in normalized_types:
                is_match = is_match or (
                    tx_source == 'jupiter' or
                    'jupiter' in description or
                    'aggregate' in description or
                    'route' in description
                )
            
            # Include any DEX/AMM transaction
            if any(t in ['swap', 'agg_swap', 'aggregated_swap'] for t in normalized_types):
                dex_sources = ['jupiter', 'raydium', 'orca', 'serum', 'saber', 'mercurial']
                if tx_source in dex_sources:
                    is_match = True
            
            if is_match:
                filtered.append(tx)
                
        except Exception as e:
            print(f"Error processing transaction {i} in type filter: {e}")
            continue
    
    print(f"Filtered by type: {len(filtered)} transactions")
    return filtered

def format_for_csv(transactions: List[Dict]) -> pd.DataFrame:
    """Format transactions for CSV export with enhanced error handling"""
    print(f"=== FORMATTING FOR CSV ===")
    print(f"Input transactions: {len(transactions) if transactions else 0}")
    
    required_columns = [
        'signature', 'timestamp', 'activity_type', 'token_in', 
        'token_out', 'amount_in', 'amount_out', 'value_usd', 'protocol'
    ]
    
    if not transactions:
        return pd.DataFrame(columns=required_columns)
    
    formatted_data = []
    
    for i, tx in enumerate(transactions):
        try:
            if not isinstance(tx, dict):
                print(f"Transaction {i} is not a dict in CSV formatter: {type(tx)}")
                continue
            
            # Extract basic info with safe defaults
            signature = safe_get(tx, 'signature', f'unknown_{i}')
            timestamp_raw = safe_get(tx, 'timestamp', 0)
            
            # Convert timestamp safely
            try:
                if timestamp_raw:
                    timestamp = datetime.fromtimestamp(timestamp_raw).isoformat()
                else:
                    timestamp = datetime.now().isoformat()
            except (ValueError, OSError):
                timestamp = datetime.now().isoformat()
            
            activity_type = safe_get(tx, 'type', 'UNKNOWN')
            source = safe_get(tx, 'source', 'UNKNOWN')
            
            # Extract token info safely
            token_in, token_out, amount_in, amount_out, value_usd = extract_token_info_safe(tx)
            
            row = {
                'signature': str(signature),
                'timestamp': str(timestamp),
                'activity_type': str(activity_type),
                'token_in': str(token_in),
                'token_out': str(token_out),
                'amount_in': float(amount_in) if amount_in else 0.0,
                'amount_out': float(amount_out) if amount_out else 0.0,
                'value_usd': float(value_usd) if value_usd else 0.0,
                'protocol': str(source)
            }
            
            formatted_data.append(row)
            
        except Exception as e:
            print(f"Error processing transaction {i} in CSV formatter: {e}")
            print(f"Transaction data: {tx}")
            continue
    
    print(f"Successfully formatted {len(formatted_data)} transactions")
    
    # Create DataFrame
    df = pd.DataFrame(formatted_data)
    
    # Ensure all required columns exist
    for col in required_columns:
        if col not in df.columns:
            df[col] = ''
    
    return df[required_columns]

def extract_token_info_safe(tx: Dict) -> tuple:
    """Safely extract token information"""
    if not isinstance(tx, dict):
        return '', '', 0, 0, 0
    
    try:
        token_in = ''
        token_out = ''
        amount_in = 0
        amount_out = 0
        
        # Extract from tokenTransfers
        token_transfers = safe_get(tx, 'tokenTransfers', [])
        fee_payer = safe_get(tx, 'feePayer', '')
        
        if isinstance(token_transfers, list):
            for transfer in token_transfers:
                if not isinstance(transfer, dict):
                    continue
                    
                from_account = safe_get(transfer, 'fromUserAccount', '')
                to_account = safe_get(transfer, 'toUserAccount', '')
                mint = safe_get(transfer, 'mint', '')
                token_amount = safe_get(transfer, 'tokenAmount', 0)
                
                if from_account == fee_payer and not token_in:
                    token_in = str(mint)
                    amount_in = float(token_amount) if token_amount else 0
                elif to_account == fee_payer and not token_out:
                    token_out = str(mint)
                    amount_out = float(token_amount) if token_amount else 0
        
        # Extract from nativeTransfers
        native_transfers = safe_get(tx, 'nativeTransfers', [])
        if isinstance(native_transfers, list):
            for transfer in native_transfers:
                if not isinstance(transfer, dict):
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
        
        value_usd = calculate_transaction_value(tx)
        
        return token_in, token_out, amount_in, amount_out, value_usd
        
    except Exception as e:
        print(f"Error in extract_token_info_safe: {e}")
        return '', '', 0, 0, 0