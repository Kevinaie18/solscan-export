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
    print(f"\n=== DEBUGGING TRANSACTION STRUCTURE ===")
    print(f"Transactions type: {type(transactions)}")
    print(f"Transactions length: {len(transactions) if hasattr(transactions, '__len__') else 'No length'}")
    
    if transactions and len(transactions) > 0:
        first_tx = transactions[0]
        print(f"First transaction type: {type(first_tx)}")
        print(f"First transaction content: {first_tx}")
        
        if isinstance(first_tx, dict):
            print(f"First transaction keys: {list(first_tx.keys())}")
            print(f"First transaction type: {first_tx.get('type', 'NO_TYPE')}")
            print(f"First transaction source: {first_tx.get('source', 'NO_SOURCE')}")
            print(f"First transaction description: {first_tx.get('description', 'NO_DESCRIPTION')}")
            
            # Debug token transfers
            token_transfers = first_tx.get('tokenTransfers', [])
            print(f"Token transfers count: {len(token_transfers)}")
            if token_transfers:
                print(f"First token transfer: {token_transfers[0]}")
            
            # Debug native transfers
            native_transfers = first_tx.get('nativeTransfers', [])
            print(f"Native transfers count: {len(native_transfers)}")
            if native_transfers:
                print(f"First native transfer: {native_transfers[0]}")
        
        # Check a few more transactions
        for i, tx in enumerate(transactions[:3]):
            print(f"\nTransaction {i}:")
            print(f"  Type: {type(tx)}")
            print(f"  Is dict: {isinstance(tx, dict)}")
            if isinstance(tx, dict):
                print(f"  Keys: {list(tx.keys())}")
                print(f"  Type: {tx.get('type', 'NO_TYPE')}")
                print(f"  Source: {tx.get('source', 'NO_SOURCE')}")
    print("\n=== END DEBUG ===")

def validate_transactions(transactions: Any) -> List[Dict]:
    """Validate and clean transaction data with enhanced debugging"""
    print(f"\n=== VALIDATING TRANSACTIONS ===")
    print(f"Input type: {type(transactions)}")
    print(f"Input content: {transactions}")
    
    # Handle different input types
    if transactions is None:
        print("❌ Transactions is None")
        return []
    
    if isinstance(transactions, str):
        print(f"❌ Transactions is a string: {transactions[:100]}...")
        return []
    
    if not isinstance(transactions, list):
        print(f"❌ Transactions is not a list, trying to convert: {type(transactions)}")
        try:
            transactions = list(transactions)
        except:
            print("❌ Could not convert to list")
            return []
    
    if not transactions:
        print("❌ Transactions list is empty")
        return []
    
    print(f"\nProcessing {len(transactions)} transactions")
    debug_transaction_structure(transactions)
    
    valid_transactions = []
    
    for i, tx in enumerate(transactions):
        print(f"\nValidating transaction {i}:")
        
        if tx is None:
            print(f"  ❌ Transaction {i} is None, skipping")
            continue
            
        if not isinstance(tx, dict):
            print(f"  ❌ Transaction {i} is not a dict: {type(tx)}, content: {tx}")
            continue
            
        # Check for required fields in Helius Enhanced API response
        signature = safe_get(tx, 'signature')
        timestamp = safe_get(tx, 'timestamp')
        tx_type = safe_get(tx, 'type')
        source = safe_get(tx, 'source')
        description = safe_get(tx, 'description')
        
        print(f"  Signature: {signature}")
        print(f"  Timestamp: {timestamp}")
        print(f"  Type: {tx_type}")
        print(f"  Source: {source}")
        print(f"  Description: {description}")
        
        # Check for token transfers
        token_transfers = safe_get(tx, 'tokenTransfers', [])
        print(f"  Token transfers: {len(token_transfers)}")
        if token_transfers:
            print(f"  First token transfer: {token_transfers[0]}")
        
        # Check for native transfers
        native_transfers = safe_get(tx, 'nativeTransfers', [])
        print(f"  Native transfers: {len(native_transfers)}")
        if native_transfers:
            print(f"  First native transfer: {native_transfers[0]}")
        
        if signature and timestamp:
            print(f"  ✅ Transaction {i} is valid")
            valid_transactions.append(tx)
        else:
            print(f"  ❌ Transaction {i} missing required fields:")
            if not signature:
                print("    - Missing signature")
            if not timestamp:
                print("    - Missing timestamp")
    
    print(f"\nValidation complete:")
    print(f"  Total transactions: {len(transactions)}")
    print(f"  Valid transactions: {len(valid_transactions)}")
    print(f"  Invalid transactions: {len(transactions) - len(valid_transactions)}")
    
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
            print(f"Processing {len(token_transfers)} token transfers")
            for transfer in token_transfers:
                if not isinstance(transfer, dict):
                    continue
                
                token_amount = safe_get(transfer, 'tokenAmount', 0)
                if token_amount:
                    try:
                        transfer_value = float(token_amount) * 0.01
                        value_usd += transfer_value
                        print(f"  Token transfer value: ${transfer_value}")
                    except (ValueError, TypeError):
                        continue
        
        # Method 2: Check nativeTransfers
        if value_usd == 0:
            native_transfers = safe_get(tx, 'nativeTransfers', [])
            if native_transfers and isinstance(native_transfers, list):
                print(f"Processing {len(native_transfers)} native transfers")
                for transfer in native_transfers:
                    if not isinstance(transfer, dict):
                        continue
                    
                    amount = safe_get(transfer, 'amount', 0)
                    if amount:
                        try:
                            sol_amount = float(amount) / 1e9
                            transfer_value = sol_amount * 100
                            value_usd += transfer_value
                            print(f"  Native transfer value: ${transfer_value}")
                        except (ValueError, TypeError):
                            continue
        
        # Method 3: Fallback to fee
        if value_usd == 0:
            fee = safe_get(tx, 'fee', 0)
            if fee:
                try:
                    sol_fee = float(fee) / 1e9
                    value_usd = sol_fee * 100
                    print(f"  Fee-based value: ${value_usd}")
                except (ValueError, TypeError):
                    pass
    
    except Exception as e:
        print(f"Error calculating transaction value: {e}")
        return 0.0
    
    print(f"Total transaction value: ${value_usd}")
    return value_usd

def filter_by_value(transactions: List[Dict], min_usd: float, max_usd: float) -> List[Dict]:
    """Filter transactions by USD value range with enhanced error handling"""
    print(f"\n=== FILTERING BY VALUE ===")
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
            print(f"\nTransaction {i}:")
            print(f"  Calculated value: ${value_usd}")
            
            if min_usd <= value_usd <= max_usd:
                print(f"  INCLUDED: Value within range")
                filtered.append(tx)
            else:
                print(f"  EXCLUDED: Value outside range")
                
        except Exception as e:
            print(f"Error processing transaction {i} in value filter: {e}")
            continue
    
    print(f"\nFiltered by value: {len(filtered)} transactions")
    return filtered

def filter_by_type(transactions: List[Dict], types: List[str]) -> List[Dict]:
    """Filter transactions by activity type with enhanced error handling"""
    print(f"\n=== FILTERING BY TYPE ===")
    print(f"Input transactions: {len(transactions) if transactions else 0}")
    print(f"Requested types: {types}")
    
    if not transactions or not types:
        print("❌ No transactions or types to filter")
        return []
    
    filtered = []
    normalized_types = [t.lower() for t in types]
    print(f"Normalized types: {normalized_types}")
    
    for i, tx in enumerate(transactions):
        try:
            if not isinstance(tx, dict):
                print(f"❌ Transaction {i} is not a dict in type filter: {type(tx)}")
                continue
            
            tx_type = safe_get(tx, 'type', '').lower()
            tx_source = safe_get(tx, 'source', '').lower()
            description = safe_get(tx, 'description', '').lower()
            
            print(f"\nTransaction {i}:")
            print(f"  Type: {tx_type}")
            print(f"  Source: {tx_source}")
            print(f"  Description: {description}")
            
            is_match = False
            
            # Check for regular swaps
            if 'swap' in normalized_types:
                is_match = (
                    'swap' in tx_type or
                    'swap' in description or
                    (tx_source in ['raydium', 'orca', 'serum', 'saber', 'mercurial'] and 
                     tx_type in ['transfer', 'unknown'])
                )
                print(f"  Regular swap match: {is_match}")
            
            # Check for aggregated swaps
            if 'agg_swap' in normalized_types or 'aggregated_swap' in normalized_types:
                agg_match = (
                    tx_source == 'jupiter' or
                    'jupiter' in description or
                    'aggregate' in description or
                    'route' in description
                )
                is_match = is_match or agg_match
                print(f"  Aggregated swap match: {agg_match}")
            
            # Include any DEX/AMM transaction
            if any(t in ['swap', 'agg_swap', 'aggregated_swap'] for t in normalized_types):
                dex_sources = ['jupiter', 'raydium', 'orca', 'serum', 'saber', 'mercurial']
                dex_match = tx_source in dex_sources
                is_match = is_match or dex_match
                print(f"  DEX match: {dex_match}")
            
            if is_match:
                print(f"  ✅ INCLUDED: Matched type filter")
                filtered.append(tx)
            else:
                print(f"  ❌ EXCLUDED: No type match")
                
        except Exception as e:
            print(f"❌ Error processing transaction {i} in type filter: {e}")
            continue
    
    print(f"\nFiltered by type: {len(filtered)} transactions")
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

def get_transaction_summary(transactions: List[Dict]) -> Dict:
    """Get summary statistics for transactions
    
    Args:
        transactions: List of transaction dictionaries
        
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
        source = tx.get('source', 'UNKNOWN')
        tx_type = tx.get('type', 'UNKNOWN')
        description = tx.get('description', '').lower()
        
        if source:
            protocols.add(source)
        if tx_type:
            tx_types.add(tx_type)
        
        # Count swap types
        if source == 'JUPITER' or 'jupiter' in description or 'aggregate' in description:
            agg_swap_count += 1
        elif tx_type in ['SWAP', 'SWAP_EXACT_OUT'] or source in ['RAYDIUM', 'ORCA', 'SERUM']:
            swap_count += 1
        
        # Calculate value
        value_usd = 0
        if 'tokenTransfers' in tx:
            for transfer in tx['tokenTransfers']:
                if 'usdTokenPrice' in transfer:
                    amount = float(transfer.get('amount', 0))
                    price = float(transfer.get('usdTokenPrice', 0))
                    value_usd += amount * price
        
        if 'nativeTransfers' in tx:
            for transfer in tx['nativeTransfers']:
                if 'usdTokenPrice' in transfer:
                    amount = float(transfer.get('amount', 0))
                    price = float(transfer.get('usdTokenPrice', 0))
                    value_usd += amount * price
        
        total_value += value_usd
        
        timestamp = tx.get('timestamp', 0)
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