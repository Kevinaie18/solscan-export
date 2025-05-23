# 📊 DeFi Transaction Export Tool

A powerful Streamlit application that enables users to export large volumes of Solana DeFi transaction data with advanced filtering capabilities.

## 🚀 Features

- **Export 1000+ Transactions**: Bypass typical export limits through smart pagination
- **Advanced Filtering**: Filter by date range, USD value, and transaction type
- **DeFi Focus**: Specifically designed for swap and aggregated swap transactions
- **CSV Export**: Clean, formatted CSV downloads for analysis
- **Real-time Progress**: Live progress tracking during export
- **User-friendly Interface**: Clean, intuitive Streamlit interface

## 🏗️ Architecture

```
├── app.py                 # Main Streamlit application
├── src/
│   ├── api_client.py      # Solscan API integration
│   ├── data_processor.py  # Data filtering and processing
│   └── export_handler.py  # CSV export functionality
├── .streamlit/
│   └── secrets.toml       # API configuration
└── requirements.txt       # Dependencies
```

## 🛠️ Setup & Installation

### Prerequisites

- Python 3.8+
- Solscan API key (free at [solscan.io](https://pro.solscan.io/api-pro))

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd defi-export-tool
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API key**
   
   Edit `.streamlit/secrets.toml`:
   ```toml
   [api]
   solscan_key = "your_actual_solscan_api_key_here"
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

## ☁️ Streamlit Cloud Deployment

### Quick Deploy

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit - DeFi Export Tool"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Select `app.py` as the main file
   - Deploy

3. **Configure Secrets**
   
   In Streamlit Cloud app settings, add:
   ```toml
   [api]
   solscan_key = "your_actual_solscan_api_key_here"
   ```

### Environment Requirements

The app will automatically install these dependencies:
- `streamlit==1.28.0`
- `pandas==2.0.3`
- `requests==2.31.0`
- `python-dateutil==2.8.2`

## 📖 Usage Guide

### Basic Workflow

1. **Enter Wallet Address**
   - Input a valid Solana wallet address (32-44 characters)
   - Example: `8EhB7pLhP9s6Gd7X2vZxJ4Q5m3W8r1Y6N9...`

2. **Set Filters**
   - **Date Range**: Select start and end dates (max 90 days recommended)
   - **USD Value**: Set minimum and maximum transaction values
   - **Transaction Types**: Choose `swap` and/or `agg_swap`

3. **Export & Download**
   - Click "Export Transactions"
   - Monitor real-time progress
   - Download the generated CSV file

### Supported Transaction Types

- **swap**: Direct token swaps
- **agg_swap**: Aggregated swaps (e.g., Jupiter aggregator)

### Export Columns

The CSV export includes these columns:
- `signature`: Transaction signature
- `timestamp`: Transaction timestamp (ISO format)
- `activity_type`: Type of DeFi activity
- `token_in`: Input token symbol
- `token_out`: Output token symbol
- `amount_in`: Input amount
- `amount_out`: Output amount
- `value_usd`: Estimated USD value
- `protocol`: DeFi protocol used

## ⚙️ Configuration

### Rate Limiting

- **API Calls**: 5 requests per second (200ms delay)
- **Pagination**: 50 transactions per request
- **Safety Limit**: Maximum 10,000 transactions per export

### Performance

- **Export Speed**: ~1000 transactions per minute
- **Memory Usage**: Optimized for large datasets
- **Timeout**: 30 seconds per API request

## 🔧 API Integration

### Solscan API

The tool uses the Solscan public API:
- **Endpoint**: `/account/defi/activities`
- **Rate Limits**: Respects API rate limiting
- **Authentication**: Token-based authentication

### Error Handling

- **API Failures**: Automatic retry with exponential backoff
- **Network Issues**: Graceful error messages
- **Data Validation**: Input validation and sanitization

## 🛡️ Security

- **API Keys**: Stored securely in Streamlit secrets
- **No Data Storage**: No persistent storage of transaction data
- **Rate Limiting**: Built-in protection against API abuse

## 📊 Limitations & Considerations

### Current Limitations

- **Export Limit**: Maximum 10,000 transactions per session
- **Date Range**: Recommended maximum 90 days for performance
- **Transaction Types**: Limited to swap and agg_swap only
- **Real-time Data**: Not suitable for real-time monitoring

### Best Practices

1. **Start Small**: Test with shorter date ranges first
2. **API Key**: Keep your Solscan API key secure
3. **Network**: Ensure stable internet connection for large exports
4. **Browser**: Use modern browsers for best performance

## 🐛 Troubleshooting

### Common Issues

**"Invalid wallet address"**
- Ensure wallet address is 32-44 characters
- Use base58-encoded Solana addresses only

**"API request failed"**
- Check your Solscan API key
- Verify API key has sufficient quota
- Try reducing date range or value filters

**"No transactions found"**
- Adjust filter criteria (date range, value range)
- Verify the wallet has DeFi transaction history
- Check transaction types are selected

### Support

- **API Issues**: Check [Solscan API documentation](https://docs.solscan.io/)
- **App Issues**: Review error messages and adjust filters
- **Performance**: Reduce date range or value range for faster exports

## 🚧 Future Enhancements

### Planned Features

- **Additional Export Formats**: JSON and Excel support
- **More Transaction Types**: Add/remove liquidity, farming
- **Protocol Filtering**: Filter by specific DeFi protocols
- **Token Filtering**: Filter by specific token addresses
- **Advanced Analytics**: Built-in charts and analysis

### Roadmap

- **Phase 2**: Enhanced filtering and export formats
- **Phase 3**: Multi-chain support (Ethereum, BSC)
- **Phase 4**: Portfolio tracking and analytics

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **Solscan**: For providing comprehensive Solana blockchain data
- **Streamlit**: For the excellent web app framework
- **Solana**: For the innovative blockchain technology

---

**Built with ❤️ for the DeFi community** 