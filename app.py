"""
DeFi Transaction Export Tool - Updated Streamlit Application
Aligned with data processor and export handler
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time

# Import our modules - Fixed import paths
try:
    from src.api_client import HeliusClient
    from src.data_processor import (
        filter_by_date, filter_by_value, filter_by_type, format_for_csv, 
        validate_transactions, get_transaction_summary, BATCH_SIZE, MAX_TRANSACTIONS
    )
    from src.export_handler import create_export_interface
except ImportError:
    # Fallback imports if src folder structure doesn't work
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from api_client import HeliusClient
        from data_processor import (
            filter_by_date, filter_by_value, filter_by_type, format_for_csv, 
            validate_transactions, get_transaction_summary, BATCH_SIZE, MAX_TRANSACTIONS
        )
        from export_handler import create_export_interface
    except ImportError as e:
        st.error(f"Import Error: {e}")
        st.error("Please check that all required files are in the correct location")
        st.stop()

# Page configuration
st.set_page_config(
    page_title="DeFi Transaction Export",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def validate_solana_address(address: str) -> bool:
    """Basic Solana address validation"""
    if not address:
        return False
    # Solana addresses are base58 encoded and typically 32-44 characters
    return len(address) >= 32 and len(address) <= 44 and address.isalnum()

def format_currency(amount: float) -> str:
    """Format currency with proper commas and decimals"""
    return f"${amount:,.2f}"

def main():
    """Main application function"""
    st.title("📊 DeFi Transaction Export Tool")
    st.markdown("Export Solana DeFi transactions with advanced filtering capabilities")
    
    # Check for API key
    try:
        api_key = st.secrets["api"]["helius_key"]
        if not api_key or api_key == "your_key_here":
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
        
        # Transaction type selection - FIXED TO MATCH DATA PROCESSOR
        st.markdown("**Transaction Types**")
        
        # User-friendly interface with proper mapping
        transaction_options = {
            "Regular Swaps": "swap",           # Maps to lowercase "swap"
            "Aggregated Swaps": "agg_swap"     # Maps to lowercase "agg_swap"
        }
        
        selected_labels = st.multiselect(
            "Select transaction types:",
            options=list(transaction_options.keys()),
            default=list(transaction_options.keys()),  # Select both by default
            help="• **Regular Swaps**: Direct trades on DEXs like Raydium, Orca, Serum\n• **Aggregated Swaps**: Jupiter routes through multiple DEXs for best price"
        )
        
        # Convert to values expected by data processor
        tx_types = [transaction_options[label] for label in selected_labels]
        
        # Show what's selected
        if tx_types:
            st.info(f"✅ Selected: {', '.join(selected_labels)}")
        else:
            st.warning("⚠️ No transaction types selected")
    
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
        
        # Date validation
        if start_date and end_date:
            if start_date <= end_date:
                days_diff = (end_date - start_date).days
                if days_diff > 90:
                    st.warning(f"⚠️ Large date range: {days_diff} days (may take longer)")
                else:
                    st.info(f"📅 Date range: {days_diff} days")
            else:
                st.error("❌ Start date must be before end date")
        
        # Value range validation
        if not use_max_value:
            st.info(f"💰 Value range: {format_currency(min_value)} and above")
        elif min_value <= max_value:
            st.info(f"💰 Value range: {format_currency(min_value)} - {format_currency(max_value)}")
        else:
            st.error("❌ Min value must be less than max value")
        
        # Transaction types display
        if selected_labels:
            st.info(f"🔄 Types: {', '.join(selected_labels)}")
        else:
            st.warning("⚠️ No transaction types selected")
        
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
        tx_types  # Check that we have transaction types
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
            
            # Convert dates to datetime objects for API client
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            # Fetch all transactions
            all_transactions = client.get_all_transactions(
                address=wallet,
                start_date=start_datetime,
                end_date=end_datetime,
                max_transactions=MAX_TRANSACTIONS
            )
            progress_bar.progress(40)
            
            status_text.text(f"🔍 Validating {len(all_transactions)} transactions...")
            
            # Validate transactions first (removes malformed data)
            valid_transactions = validate_transactions(all_transactions)
            progress_bar.progress(50)
            
            status_text.text(f"🔍 Processing {len(valid_transactions)} valid transactions...")
            
            # Apply filters using data processor functions
            filtered_transactions = valid_transactions
            
            # Filter by date (additional filter on top of API params)
            filtered_transactions = filter_by_date(
                filtered_transactions, 
                start_datetime,
                end_datetime
            )
            progress_bar.progress(60)
            
            # Filter by value
            filtered_transactions = filter_by_value(
                filtered_transactions, min_value, max_value
            )
            progress_bar.progress(70)
            
            # Filter by transaction type (using corrected values)
            filtered_transactions = filter_by_type(filtered_transactions, tx_types)
            progress_bar.progress(80)
            
            status_text.text("📊 Formatting data for export...")
            
            # Format for CSV using data processor
            df = format_for_csv(filtered_transactions)
            progress_bar.progress(90)
            
            # Get summary using data processor
            summary = get_transaction_summary(filtered_transactions)
            
            # Display results
            st.success(f"✅ Successfully processed {summary['total_count']} transactions")
            
            # Show breakdown of transaction types
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Transactions", summary['total_count'])
            with col2:
                st.metric("Regular Swaps", summary.get('swap_count', 0))
            with col3:
                st.metric("Aggregated Swaps", summary.get('agg_swap_count', 0))
            
            st.info(f"💰 Total value: {format_currency(summary['total_value_usd'])}")
            st.info(f"🏢 Unique protocols: {summary['unique_protocols']}")
            st.info(f"📅 Date range: {summary['date_range']}")
            
            # Create filter dictionary for export handler
            filters = {
                'wallet_address': wallet,
                'start_date': start_datetime,
                'end_date': end_datetime,
                'min_value': min_value,
                'max_value': max_value if use_max_value else float('inf'),
                'transaction_types': tx_types
            }
            
            # Use export handler for complete interface
            progress_bar.progress(95)
            status_text.text("📥 Preparing download...")
            
            create_export_interface(df, filters)
            
            progress_bar.progress(100)
            status_text.text("✅ Export complete!")
            
        except Exception as e:
            st.error(f"❌ Error during export: {str(e)}")
            
            # Show detailed error info in expander for debugging
            with st.expander("🔍 Error Details (for debugging)"):
                st.code(str(e))
                import traceback
                st.code(traceback.format_exc())
            
            progress_bar.progress(0)
            status_text.text("❌ Export failed")
    
    # Information section
    st.markdown("---")
    with st.expander("ℹ️ About Transaction Types"):
        st.markdown("""
        ### Transaction Types Explained
        
        **Regular Swaps**
        - Direct trades on individual DEXs
        - Sources: Raydium, Orca, Serum, Saber, Mercurial, etc.
        - Simple token-to-token exchanges
        
        **Aggregated Swaps**  
        - Jupiter aggregated swaps
        - Routes through multiple DEXs for best price
        - May include multiple hops and protocols
        - Optimized for price efficiency
        
        ### Supported Protocols
        - **Jupiter**: Aggregator routing through multiple DEXs
        - **Raydium**: Automated market maker (AMM)
        - **Orca**: User-friendly DEX with concentrated liquidity
        - **Serum**: Central limit order book DEX
        - **Saber**: Stablecoin-focused AMM
        - And more...
        """)

if __name__ == "__main__":
    main()