"""
CSV export functionality for DeFi transactions
"""

import pandas as pd
import io
import streamlit as st
from typing import Union
from datetime import datetime


def generate_csv(df: pd.DataFrame) -> io.StringIO:
    """Generate CSV data from DataFrame
    
    Args:
        df: Pandas DataFrame to convert
        
    Returns:
        StringIO buffer containing CSV data
    """
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    return csv_buffer


def create_download_link(csv_data: Union[str, io.StringIO], filename: str) -> None:
    """Create Streamlit download button for CSV
    
    Args:
        csv_data: CSV data as string or StringIO
        filename: Name for the downloaded file
    """
    # Convert StringIO to string if needed
    if isinstance(csv_data, io.StringIO):
        csv_string = csv_data.getvalue()
    else:
        csv_string = csv_data
    
    # Generate filename with timestamp if not provided
    if not filename.endswith('.csv'):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"defi_transactions_{timestamp}.csv"
    
    # Create download button
    st.download_button(
        label="📥 Download CSV",
        data=csv_string,
        file_name=filename,
        mime="text/csv",
        help="Click to download your filtered DeFi transactions"
    )


def validate_export_size(df: pd.DataFrame) -> bool:
    """Validate that export size is reasonable
    
    Args:
        df: DataFrame to validate
        
    Returns:
        True if size is acceptable, False otherwise
    """
    # Basic size validation
    max_rows = 10000  # Maximum rows for export
    return len(df) <= max_rows


def get_export_summary(df: pd.DataFrame) -> dict:
    """Get summary statistics for the export
    
    Args:
        df: DataFrame to summarize
        
    Returns:
        Dictionary with summary statistics
    """
    summary = {
        'total_transactions': len(df),
        'total_value_usd': df['value_usd'].sum() if 'value_usd' in df.columns else 0,
        'unique_protocols': df['protocol'].nunique() if 'protocol' in df.columns else 0,
        'date_range': {
            'start': df['timestamp'].min() if 'timestamp' in df.columns and len(df) > 0 else None,
            'end': df['timestamp'].max() if 'timestamp' in df.columns and len(df) > 0 else None
        }
    }
    return summary 