"""
NIFTY-50 Stock Price Fetcher
Simple tool to get latest price for any NIFTY-50 stock by ticker
"""

import logging
from typing import Optional
import yfinance as yf

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
class NIFTY50StockPrice:
    """Fetches latest stock price for NIFTY-50 companies""" 
    def __init__(self):
        """Initialize the price fetcher"""
        pass
    
    def get_price(self, ticker: str) -> Optional[float]:
        """
        Get the latest stock price for a given ticker.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'RELIANCE', 'TCS', 'INFY')
                   Can be with or without .NS suffix
        
        Returns:
            Current stock price in INR, or None if fetch fails
        
        Example:
            >>> fetcher = NIFTY50StockPrice()
            >>> price = fetcher.get_price('RELIANCE')
            >>> print(f"₹{price:,.2f}")
        """
        try:
            # Ensure ticker has .NS suffix for NSE
            if not ticker.endswith('.NS'):
                ticker = f"{ticker}.NS"
            
            logger.info(f"Fetching price for {ticker}")
            
            # Create ticker object
            stock = yf.Ticker(ticker)
            
            # Get latest price using fast_info (faster than full history)
            price = stock.fast_info.get('lastPrice')
            
            if price is None or price == 0:
                # Fallback: try getting from history
                hist = stock.history(period='1d')
                if not hist.empty:
                    price = hist['Close'].iloc[-1]
            
            if price is None or price == 0:
                logger.error(f"Could not fetch price for {ticker}")
                return None
            
            logger.info(f"Successfully fetched {ticker}: ₹{price:,.2f}")
            return float(price)
            
        except Exception as e:
            logger.error(f"Error fetching price for {ticker}: {e}")
            return None
    
    def get_multiple_prices(self, tickers: list[str]) -> dict[str, float]:
        """
        Get prices for multiple tickers at once.
        
        Args:
            tickers: List of ticker symbols
        
        Returns:
            Dictionary mapping ticker to price
        """
        prices = {}
        for ticker in tickers:
            price = self.get_price(ticker)
            if price is not None:
                # Store with clean ticker name (without .NS)
                clean_ticker = ticker.replace('.NS', '')
                prices[clean_ticker] = price
        
        return prices
    
    def get_stock_info(self, ticker: str) -> dict:
        """
        Get detailed information including price for a stock.
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            Dictionary with price and other key metrics
        """
        try:
            if not ticker.endswith('.NS'):
                ticker = f"{ticker}.NS"
            
            stock = yf.Ticker(ticker)
            info = stock.fast_info
            
            return {
                'ticker': ticker.replace('.NS', ''),
                'current_price': info.get('lastPrice'),
                'previous_close': info.get('previousClose'),
                'open': info.get('open'),
                'day_high': info.get('dayHigh'),
                'day_low': info.get('dayLow'),
                'currency': info.get('currency', 'INR')
            }
            
        except Exception as e:
            logger.error(f"Error fetching info for {ticker}: {e}")
            return {}


# Common NIFTY-50 tickers for reference
NIFTY50_TICKERS = [
    'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK',
    'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'KOTAKBANK',
    'LT', 'AXISBANK', 'ASIANPAINT', 'MARUTI', 'TITAN',
    'BAJFINANCE', 'HCLTECH', 'SUNPHARMA', 'ULTRACEMCO', 'ONGC',
    'NESTLEIND', 'WIPRO', 'NTPC', 'TATAMOTORS', 'POWERGRID',
    'M&M', 'ADANIENT', 'COALINDIA', 'JSWSTEEL', 'TATASTEEL',
    'INDUSINDBK', 'BAJAJFINSV', 'HINDALCO', 'GRASIM', 'CIPLA',
    'TECHM', 'DRREDDY', 'EICHERMOT', 'BPCL', 'APOLLOHOSP',
    'DIVISLAB', 'TATACONSUM', 'SBILIFE', 'HDFCLIFE', 'HEROMOTOCO',
    'BRITANNIA', 'ADANIPORTS', 'SHRIRAMFIN', 'BAJAJ-AUTO', 'LTIM'
]


# Example usage
if __name__ == "__main__":
    fetcher = NIFTY50StockPrice()
    
    print("=" * 60)
    print("NIFTY-50 STOCK PRICE FETCHER")
    print("=" * 60)
    
    # Example 1: Get single stock price
    print("\n[1] Fetching single stock price:")
    print("-" * 60)
    
    ticker = "RELIANCE"
    price = fetcher.get_price(ticker)
    
    if price:
        print(f"✓ {ticker}: ₹{price:,.2f}")
    else:
        print(f"✗ Failed to fetch price for {ticker}")
    
    # Example 2: Get detailed info
    print("\n[2] Fetching detailed stock info:")
    print("-" * 60)
    
    info = fetcher.get_stock_info("TCS")
    if info:
        print(f"Ticker: {info['ticker']}")
        print(f"Current Price: ₹{info['current_price']:,.2f}")
        print(f"Previous Close: ₹{info['previous_close']:,.2f}")
        print(f"Day Range: ₹{info['day_low']:,.2f} - ₹{info['day_high']:,.2f}")
    
    # Example 3: Get multiple prices
    print("\n[3] Fetching multiple stock prices:")
    print("-" * 60)
    
    tickers = ['INFY', 'TCS', 'HDFCBANK', 'ICICIBANK', 'SBIN']
    prices = fetcher.get_multiple_prices(tickers)
    
    for ticker, price in prices.items():
        print(f"{ticker:15s} ₹{price:>12,.2f}")
    
    # Interactive mode
    print("\n" + "=" * 60)
    print("INTERACTIVE MODE - Enter stock tickers")
    print("=" * 60)
    print("\nExample tickers: RELIANCE, TCS, INFY, HDFCBANK, ITC")
    print("Type 'quit' or 'exit' to stop\n")
    
    while True:
        try:
            ticker = input("Enter stock ticker: ").strip().upper()
            
            if ticker in ['QUIT', 'EXIT', 'Q', '']:
                print("\n👋 Goodbye!")
                break
            
            price = fetcher.get_price(ticker)
            
            if price:
                print(f"✓ {ticker}: ₹{price:,.2f}\n")
            else:
                print(f"✗ Could not fetch price for {ticker}")
                print("   Make sure it's a valid NSE ticker\n")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"✗ Error: {e}\n")
