"""
Utility functions for the DeFi Transaction Export Tool
"""

import re
from datetime import datetime, timedelta
from typing import Optional


def validate_solana_address(address: str) -> bool:
    """
    Validate Solana wallet address format
    
    Args:
        address: Wallet address to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not address:
        return False
    
    # Solana addresses are base58 encoded and typically 32-44 characters
    # Check length and character set
    if not (32 <= len(address) <= 44):
        return False
    
    # Base58 character set (no 0, O, I, l)
    base58_pattern = r'^[1-9A-HJ-NP-Za-km-z]+$'
    return bool(re.match(base58_pattern, address))


def format_currency(amount: float, decimals: int = 2) -> str:
    """
    Format currency amount with proper separators
    
    Args:
        amount: Amount to format
        decimals: Number of decimal places
        
    Returns:
        Formatted currency string
    """
    return f"${amount:,.{decimals}f}"


def validate_date_range(start_date: datetime, end_date: datetime, max_days: int = 90) -> dict:
    """
    Validate date range and return validation results
    
    Args:
        start_date: Start date
        end_date: End date
        max_days: Maximum allowed days in range
        
    Returns:
        Dictionary with validation results
    """
    result = {
        'valid': True,
        'message': '',
        'days': 0,
        'warning': False
    }
    
    if start_date > end_date:
        result['valid'] = False
        result['message'] = 'Start date must be before end date'
        return result
    
    days_diff = (end_date - start_date).days
    result['days'] = days_diff
    
    if days_diff > max_days:
        result['warning'] = True
        result['message'] = f'Date range is {days_diff} days (recommended max: {max_days} days)'
    elif days_diff == 0:
        result['warning'] = True
        result['message'] = 'Single day selected - may have limited results'
    
    return result


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate string to specified length with suffix
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def estimate_processing_time(transaction_count: int) -> str:
    """
    Estimate processing time based on transaction count
    
    Args:
        transaction_count: Number of transactions to process
        
    Returns:
        Estimated time string
    """
    # Rough estimate: 1000 transactions per minute
    if transaction_count <= 100:
        return "< 1 minute"
    elif transaction_count <= 1000:
        return f"~{transaction_count // 100} minutes"
    else:
        return f"~{transaction_count // 1000} minutes"


def safe_get(data: dict, path: str, default=None):
    """
    Safely get nested dictionary value using dot notation
    
    Args:
        data: Dictionary to search
        path: Dot-separated path (e.g., 'data.amount_info.amount_in')
        default: Default value if path not found
        
    Returns:
        Value at path or default
    """
    try:
        keys = path.split('.')
        result = data
        for key in keys:
            result = result[key]
        return result
    except (KeyError, TypeError):
        return default


def get_file_size_mb(content: str) -> float:
    """
    Calculate file size in MB for content
    
    Args:
        content: String content
        
    Returns:
        Size in MB
    """
    return len(content.encode('utf-8')) / (1024 * 1024)


def generate_export_filename(wallet_address: str, 
                           start_date: datetime, 
                           end_date: datetime, 
                           extension: str = 'csv') -> str:
    """
    Generate a descriptive filename for exports
    
    Args:
        wallet_address: Wallet address
        start_date: Start date
        end_date: End date
        extension: File extension
        
    Returns:
        Generated filename
    """
    # Truncate wallet address for filename
    wallet_short = wallet_address[:8] if len(wallet_address) >= 8 else wallet_address
    
    # Format dates
    start_str = start_date.strftime('%Y%m%d')
    end_str = end_date.strftime('%Y%m%d')
    
    # Generate timestamp
    timestamp = datetime.now().strftime('%H%M%S')
    
    return f"defi_export_{wallet_short}_{start_str}_{end_str}_{timestamp}.{extension}" 