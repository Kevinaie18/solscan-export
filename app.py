"""
DeFi Transaction Export Tool - Main Streamlit Application
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time

# Import our modules
from src.api_client import HeliusClient
from src.data_processor import filter_by_date, filter_by_value, filter_by_type, format_for_csv, BATCH_SIZE, MAX_TRANSACTIONS
from src.export_handler import generate_csv, create_download_link, validate_export_size, get_export_summary
from src.utils import validate_solana_address, format_currency, validate_date_range, generate_export_filename

# Page configuration
st.set_page_config(
    page_title="DeFi Transaction Export",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def convert_to_timestamp(date_obj) -> int:
    """Convert date object to Unix timestamp"""
    if hasattr(date_obj, 'timestamp'):
        return int(date_obj.timestamp())
    return int(datetime.combine(date_obj, datetime.min.time()).timestamp())

def main():
    """Main application function"""
    st.title("📊 DeFi Transaction Export Tool")
    st.markdown("Export Solana DeFi transactions with advanced filtering capabilities")
    
    # Check for API key
    try:
        api_key = st.secrets["api"]["helius_key"]
        if api_key == "your_key_here":
            st.error("⚠️ Please configure your Helius API key in .streamlit/secrets.toml")
            st.info("Get your free API key at: https://dev.helius.xyz/")
            st.stop()
    except Exception:
        st.error("⚠️ Please configure your Helius API key in .streamlit/secrets.toml")
        st.info("Get your free API key at: https://dev.helius.xyz/")
        st.stop()
    
    # Create layout columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🔍 Filter Configuration")
        
        # Wallet address input
        wallet = st.text_input(
            "Wallet Address *", 
            placeholder="Enter Solana wallet address (e.g., 8EhB...w7X)",
            help="Enter the Solana wallet address to export transactions for"
        )
        
        # Date range inputs
        st.markdown("**Date Range**")
        col_start, col_end = st.columns(2)
        
        with col_start:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now().date() - timedelta(days=30),
                max_value=datetime.now().date(),
                help="Select the start date for transaction filtering"
            )
        
        with col_end:
            end_date = st.date_input(
                "End Date",
                value=datetime.now().date(),
                max_value=datetime.now().date(),
                help="Select the end date for transaction filtering"
            )
        
        # Value range filters
        st.markdown("**USD Value Range**")
        col_min, col_max = st.columns(2)
        
        with col_min:
            min_value = st.number_input(
                "Min USD Value", 
                min_value=0.0, 
                value=0.0,
                step=1.0,
                format="%.2f",
                help="Minimum transaction value in USD"
            )
        
        with col_max:
            use_max_value = st.checkbox("Set maximum value", value=False, help="Enable to set a maximum USD value filter")
            if use_max_value:
                max_value = st.number_input(
                    "Max USD Value", 
                    min_value=0.0, 
                    value=10000.0,
                    step=1.0,
                    format="%.2f",
                    help="Maximum transaction value in USD"
                )
            else:
                max_value = float('inf')  # No maximum value limit
        
        # Transaction type selection
        tx_types = st.multiselect(
            "Transaction Types",
            options=["SWAP", "AGGREGATOR_SWAP"],
            default=["SWAP", "AGGREGATOR_SWAP"],
            help="Select which types of DeFi transactions to include"
        )
        
        # Optional token mint filter
        token_mint = st.text_input(
            "Token Mint (Optional)",
            placeholder="Enter token mint address to filter by specific token",
            help="Filter transactions by a specific token mint address"
        )
    
    with col2:
        st.subheader("📋 Export Summary")
        
        # Validation status
        wallet_valid = validate_solana_address(wallet) if wallet else False
        if wallet and wallet_valid:
            st.success("✅ Valid wallet address")
        elif wallet:
            st.error("❌ Invalid wallet address format")
        else:
            st.info("ℹ️ Enter wallet address")
        
        # Date validation using utility function
        if start_date and end_date:
            date_validation = validate_date_range(
                datetime.combine(start_date, datetime.min.time()),
                datetime.combine(end_date, datetime.max.time())
            )
            
            if date_validation['valid']:
                if date_validation['warning']:
                    st.warning(f"⚠️ {date_validation['message']}")
                else:
                    st.info(f"📅 Date range: {date_validation['days']} days")
            else:
                st.error(f"❌ {date_validation['message']}")
        
        # Value range validation
        if not use_max_value:
            st.info(f"💰 Value range: {format_currency(min_value)} and above")
        elif min_value <= max_value:
            st.info(f"💰 Value range: {format_currency(min_value)} - {format_currency(max_value)}")
        else:
            st.error("❌ Min value must be less than max value")
        
        # Transaction types
        if tx_types:
            st.info(f"🔄 Types: {', '.join(tx_types)}")
        else:
            st.warning("⚠️ No transaction types selected")
        
        # Token mint filter
        if token_mint:
            st.info(f"🪙 Token: {token_mint}")
        
        # API limits info
        st.info(f"📊 API Limits:\n- Batch size: {BATCH_SIZE} transactions\n- Maximum: {MAX_TRANSACTIONS} transactions")
    
    # Export section
    st.markdown("---")
    st.subheader("🚀 Export Transactions")
    
    # Validation for export button
    can_export = (
        wallet and 
        wallet_valid and 
        start_date <= end_date and 
        (not use_max_value or min_value <= max_value) and 
        tx_types
    )
    
    # Export button
    export_button = st.button(
        "Export Transactions",
        type="primary",
        disabled=not can_export,
        help="Click to start exporting transactions with the selected filters"
    )
    
    if export_button:
        try:
            # Initialize progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("🔄 Initializing API client...")
            time.sleep(0.5)
            
            # Create API client
            client = HeliusClient(api_key)
            progress_bar.progress(10)
            
            status_text.text("📡 Fetching transactions from Helius API...")
            
            # Fetch all transactions
            all_transactions = client.get_all_transactions(
                address=wallet,
                start_date=datetime.combine(start_date, datetime.min.time()),
                end_date=datetime.combine(end_date, datetime.max.time())
            )
            progress_bar.progress(50)
            
            status_text.text(f"🔍 Processing {len(all_transactions)} transactions...")
            
            # Apply filters
            filtered_transactions = all_transactions
            
            # Filter by date (additional filter on top of API params)
            filtered_transactions = filter_by_date(
                filtered_transactions, 
                datetime.combine(start_date, datetime.min.time()),
                datetime.combine(end_date, datetime.max.time())
            )
            progress_bar.progress(60)
            
            # Filter by value
            if min_value > 0 or (use_max_value and max_value < float('inf')):
                filtered_transactions = filter_by_value(
                    filtered_transactions, min_value, max_value
                )
            progress_bar.progress(70)
            
            # Filter by transaction type
            filtered_transactions = filter_by_type(filtered_transactions, tx_types)
            progress_bar.progress(80)
            
            # Filter by token mint if specified
            if token_mint:
                filtered_transactions = [
                    tx for tx in filtered_transactions
                    if any(
                        transfer.get('mint') == token_mint
                        for transfer in tx.get('tokenTransfers', [])
                    )
                ]
            progress_bar.progress(85)
            
            status_text.text("📊 Formatting data for export...")
            
            # Format for CSV
            df = format_for_csv(filtered_transactions)
            
            # Validate export size
            if not validate_export_size(df):
                st.error(f"❌ Export size exceeds maximum limit of {MAX_TRANSACTIONS} transactions")
                st.stop()
            
            # Get export summary
            summary = get_export_summary(df)
            
            # Display summary
            st.success(f"✅ Successfully processed {summary['total_transactions']} transactions")
            st.info(f"💰 Total value: {format_currency(summary['total_value_usd'])}")
            st.info(f"🏢 Unique protocols: {summary['unique_protocols']}")
            
            if summary['date_range']['start'] and summary['date_range']['end']:
                st.info(f"📅 Date range: {summary['date_range']['start']} to {summary['date_range']['end']}")
            
            # Generate and provide download link
            csv_data = generate_csv(df)
            filename = generate_export_filename(wallet, start_date, end_date)
            create_download_link(csv_data, filename)
            
            progress_bar.progress(100)
            status_text.text("✅ Export complete!")
            
        except Exception as e:
            st.error(f"❌ Error during export: {str(e)}")
            progress_bar.progress(0)
            status_text.text("❌ Export failed")

if __name__ == "__main__":
    main() 