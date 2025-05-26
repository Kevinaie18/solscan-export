"""
CSV export functionality for DeFi transactions with enhanced swap type support
"""

import pandas as pd
import io
import streamlit as st
from typing import Union, Dict
from datetime import datetime

# Constants for export limits
MAX_ROWS = 5000  # Maximum rows for export (aligned with API client limit)
BATCH_SIZE = 100  # Helius API limit

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


def create_download_link(csv_data: Union[str, io.StringIO], filename: str = None) -> None:
    """Create Streamlit download button for CSV
    
    Args:
        csv_data: CSV data as string or StringIO
        filename: Name for the downloaded file (optional)
    """
    # Convert StringIO to string if needed
    if isinstance(csv_data, io.StringIO):
        csv_string = csv_data.getvalue()
    else:
        csv_string = csv_data
    
    # Generate filename with timestamp if not provided
    if not filename or not filename.endswith('.csv'):
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


def validate_export_size(df: pd.DataFrame) -> tuple[bool, str]:
    """Validate that export size is reasonable
    
    Args:
        df: DataFrame to validate
        
    Returns:
        Tuple of (is_valid, message)
    """
    if df is None or df.empty:
        return False, "No data to export"
    
    row_count = len(df)
    
    if row_count > MAX_ROWS:
        return False, f"Export too large: {row_count} rows (max: {MAX_ROWS})"
    
    if row_count == 0:
        return False, "No transactions match your filters"
    
    return True, f"Export ready: {row_count} transactions"


def get_export_summary(df: pd.DataFrame) -> Dict:
    """Get enhanced summary statistics for the export
    
    Args:
        df: DataFrame to summarize
        
    Returns:
        Dictionary with summary statistics
    """
    if df is None or df.empty:
        return {
            'total_transactions': 0,
            'swap_transactions': 0,
            'agg_swap_transactions': 0,
            'total_value_usd': 0,
            'unique_protocols': 0,
            'date_range': 'No data',
            'batch_size': BATCH_SIZE,
            'max_transactions': MAX_ROWS
        }
    
    # Count swap types based on protocol/activity_type (aligned with data processor logic)
    swap_count = 0
    agg_swap_count = 0
    
    if 'protocol' in df.columns and 'activity_type' in df.columns:
        for _, row in df.iterrows():
            protocol = str(row.get('protocol', '')).upper()
            activity_type = str(row.get('activity_type', '')).upper()
            
            # Aggregated swaps (Jupiter is the main aggregator)
            if protocol == 'JUPITER':
                agg_swap_count += 1
            # Regular swaps (direct DEX protocols or swap activity types)
            elif (protocol in ['RAYDIUM', 'ORCA', 'SERUM', 'SABER', 'MERCURIAL', 'ALDRIN', 'CREMA', 'LIFINITY'] or
                  activity_type in ['SWAP', 'SWAP_EXACT_OUT']):
                swap_count += 1
    
    # Calculate total value safely
    total_value = 0
    if 'value_usd' in df.columns:
        total_value = df['value_usd'].fillna(0).sum()
        if pd.isna(total_value):
            total_value = 0
    
    # Get unique protocols count
    unique_protocols = 0
    if 'protocol' in df.columns:
        unique_protocols = df['protocol'].fillna('UNKNOWN').nunique()
    
    # Get date range (aligned with data processor timestamp format)
    date_range = 'Unknown'
    if 'timestamp' in df.columns and len(df) > 0:
        try:
            # Handle ISO format timestamps from data processor
            timestamps = pd.to_datetime(df['timestamp'])
            start_date = timestamps.min().strftime('%Y-%m-%d')
            end_date = timestamps.max().strftime('%Y-%m-%d')
            
            if start_date == end_date:
                date_range = start_date
            else:
                date_range = f"{start_date} to {end_date}"
        except Exception as e:
            print(f"Error processing date range: {e}")
            date_range = 'Date processing error'
    
    summary = {
        'total_transactions': len(df),
        'swap_transactions': swap_count,
        'agg_swap_transactions': agg_swap_count,
        'total_value_usd': round(total_value, 2),
        'unique_protocols': unique_protocols,
        'date_range': date_range,
        'batch_size': BATCH_SIZE,
        'max_transactions': MAX_ROWS
    }
    
    return summary


def format_export_filename(filters: Dict = None) -> str:
    """Generate a descriptive filename based on filters
    
    Args:
        filters: Dictionary containing filter parameters
        
    Returns:
        Formatted filename string
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if not filters:
        return f"defi_transactions_{timestamp}.csv"
    
    # Build filename components
    components = ["defi_transactions"]
    
    # Add date range if available
    if filters.get('start_date') and filters.get('end_date'):
        start = filters['start_date'].strftime('%Y%m%d')
        end = filters['end_date'].strftime('%Y%m%d')
        components.append(f"{start}_to_{end}")
    
    # Add transaction types
    if filters.get('transaction_types'):
        types_str = "_".join(filters['transaction_types'])
        components.append(types_str)
    
    # Add value range if specified
    if filters.get('min_value', 0) > 0 or filters.get('max_value', float('inf')) < float('inf'):
        min_val = filters.get('min_value', 0)
        max_val = filters.get('max_value', float('inf'))
        if max_val == float('inf'):
            components.append(f"min_{min_val}usd")
        else:
            components.append(f"{min_val}_to_{max_val}usd")
    
    components.append(timestamp)
    
    filename = "_".join(components) + ".csv"
    return filename


def display_export_preview(df: pd.DataFrame, max_rows: int = 5) -> None:
    """Display a preview of the export data
    
    Args:
        df: DataFrame to preview
        max_rows: Maximum number of rows to show in preview
    """
    if df is None or df.empty:
        st.warning("No data to preview")
        return
    
    st.subheader("📊 Export Preview")
    
    # Show summary stats
    summary = get_export_summary(df)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Transactions", summary['total_transactions'])
    with col2:
        st.metric("Regular Swaps", summary['swap_transactions'])
    with col3:
        st.metric("Aggregated Swaps", summary['agg_swap_transactions'])
    with col4:
        st.metric("Total Value (USD)", f"${summary['total_value_usd']:,.2f}")
    
    # Show data preview
    st.write(f"**Date Range:** {summary['date_range']}")
    st.write(f"**Unique Protocols:** {summary['unique_protocols']}")
    
    st.write(f"**First {min(max_rows, len(df))} rows:**")
    st.dataframe(df.head(max_rows), use_container_width=True)
    
    if len(df) > max_rows:
        st.info(f"Showing {max_rows} of {len(df)} total transactions. Download CSV to see all data.")


def create_export_interface(df: pd.DataFrame, filters: Dict = None) -> None:
    """Create a complete export interface with preview and download
    
    Args:
        df: DataFrame to export
        filters: Filter parameters used to generate the data
    """
    if df is None or df.empty:
        st.error("❌ No data available for export")
        return
    
    # Validate export size
    is_valid, message = validate_export_size(df)
    
    if not is_valid:
        st.error(f"❌ {message}")
        return
    
    # Show success message
    st.success(f"✅ {message}")
    
    # Display preview
    display_export_preview(df)
    
    # Generate CSV
    csv_buffer = generate_csv(df)
    
    # Generate filename
    filename = format_export_filename(filters)
    
    # Create download interface
    st.subheader("📥 Download Export")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        create_download_link(csv_buffer, filename)
    
    with col2:
        st.info(f"File: {filename}")
    
    # Show file info
    csv_size = len(csv_buffer.getvalue().encode('utf-8'))
    st.caption(f"File size: {csv_size / 1024:.1f} KB | Format: CSV | Encoding: UTF-8")