"""
NIFTY-50 Stock Price Scraper from Screener.in
Scrapes live stock prices for NIFTY-50 companies
"""

import time
import logging
from typing import Optional, Dict

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ScreenerPriceScraper:
    """Scrapes NIFTY-50 stock prices from Screener.in"""
    
    SCREENER_URL = "https://www.screener.in/company/NIFTY/"
    
    def __init__(self, headless: bool = True):
        """
        Initialize the scraper with Selenium WebDriver.
        
        Args:
            headless: Run browser in headless mode (no GUI)
        """
        self.headless = headless
        self.driver = None
        self.stock_data = {}
    
    def _setup_driver(self):
        """Setup Chrome WebDriver with options"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        logger.info("Chrome WebDriver initialized")
    
    def scrape_all_prices(self) -> Dict[str, float]:
        """
        Scrape all NIFTY-50 stock prices from Screener.in
        
        Returns:
            Dictionary mapping company name to current price
            Example: {"Reliance Industries": 1531.75, "HDFC Bank": 1004.00, ...}
        """
        try:
            self._setup_driver()
            logger.info(f"Loading {self.SCREENER_URL}")
            
            self.driver.get(self.SCREENER_URL)
            
            # Wait for the table to load
            wait = WebDriverWait(self.driver, 15)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            
            # Give extra time for dynamic content
            time.sleep(2)
            
            # Get page source and parse
            page_source = self.driver.page_source
            self.stock_data = self._parse_table(page_source)
            
            # Check if there's a second page
            if self._has_next_page():
                logger.info("Found second page, loading...")
                self._click_next_page()
                time.sleep(2)
                
                page_source = self.driver.page_source
                page2_data = self._parse_table(page_source)
                self.stock_data.update(page2_data)
            
            logger.info(f"Successfully scraped {len(self.stock_data)} stocks")
            return self.stock_data
            
        except Exception as e:
            logger.error(f"Error scraping prices: {e}")
            return {}
        
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("Browser closed")
    
    def _parse_table(self, html: str) -> Dict[str, float]:
        """Parse the HTML table to extract stock names and prices"""
        soup = BeautifulSoup(html, 'html.parser')
        prices = {}
        
        # Find all table rows
        table = soup.find('table')
        if not table:
            logger.warning("Table not found in HTML")
            return prices
        
        rows = table.find_all('tr')[1:]  # Skip header row
        
        for row in rows:
            try:
                cols = row.find_all('td')
                if len(cols) < 3:
                    continue
                
                # Extract company name (2nd column)
                name_cell = cols[1]
                company_link = name_cell.find('a')
                if company_link:
                    company_name = company_link.text.strip()
                else:
                    continue
                
                # Extract current price (3rd column - CMP)
                price_cell = cols[2]
                price_text = price_cell.text.strip().replace(',', '')
                
                try:
                    price = float(price_text)
                    prices[company_name] = price
                except ValueError:
                    logger.debug(f"Could not parse price for {company_name}: {price_text}")
                    continue
                    
            except Exception as e:
                logger.debug(f"Error parsing row: {e}")
                continue
        
        return prices
    
    def _has_next_page(self) -> bool:
        """Check if there's a next page button"""
        try:
            next_button = self.driver.find_element(By.LINK_TEXT, "Next")
            return True
        except:
            return False
    
    def _click_next_page(self):
        """Click the next page button"""
        try:
            next_button = self.driver.find_element(By.LINK_TEXT, "Next")
            next_button.click()
            time.sleep(2)
        except Exception as e:
            logger.error(f"Could not click next page: {e}")
    
    def get_price(self, company_name: str) -> Optional[float]:
        """
        Get price for a specific company.
        
        Args:
            company_name: Full or partial company name (case-insensitive)
        
        Returns:
            Stock price or None if not found
        """
        if not self.stock_data:
            self.scrape_all_prices()
        
        # Try exact match first
        if company_name in self.stock_data:
            return self.stock_data[company_name]
        
        # Try case-insensitive partial match
        company_lower = company_name.lower()
        for name, price in self.stock_data.items():
            if company_lower in name.lower():
                return price
        
        return None


class InteractiveStockFetcher:
    """Interactive CLI for fetching stock prices"""
    
    def __init__(self):
        self.scraper = ScreenerPriceScraper(headless=True)
        self.prices_loaded = False
    
    def load_prices(self):
        """Load all NIFTY-50 prices (one-time operation)"""
        if not self.prices_loaded:
            print("\n⏳ Loading NIFTY-50 stock prices from Screener.in...")
            self.scraper.scrape_all_prices()
            self.prices_loaded = True
            print(f"✓ Loaded {len(self.scraper.stock_data)} stocks\n")
    
    def search_stock(self, query: str):
        """Search for a stock by name or partial match"""
        if not self.prices_loaded:
            self.load_prices()
        
        query_lower = query.lower()
        matches = []
        
        for name, price in self.scraper.stock_data.items():
            if query_lower in name.lower():
                matches.append((name, price))
        
        return matches
    
    def run(self):
        """Run the interactive CLI"""
        print("=" * 60)
        print("NIFTY-50 STOCK PRICE FETCHER (Screener.in)")
        print("=" * 60)
        
        # Load prices at startup
        self.load_prices()
        
        print("\nEnter company name or ticker (partial match works)")
        print("Type 'list' to see all stocks")
        print("Type 'quit' or 'exit' to stop\n")
        
        while True:
            try:
                query = input("Search stock: ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                if query.lower() == 'list':
                    print("\n" + "=" * 60)
                    print("ALL NIFTY-50 STOCKS")
                    print("=" * 60)
                    for name, price in sorted(self.scraper.stock_data.items()):
                        print(f"{name:30s} ₹{price:>10,.2f}")
                    print("=" * 60 + "\n")
                    continue
                
                # Search for stock
                matches = self.search_stock(query)
                
                if not matches:
                    print(f"✗ No stocks found matching '{query}'\n")
                elif len(matches) == 1:
                    name, price = matches[0]
                    print(f"✓ {name}: ₹{price:,.2f}\n")
                else:
                    print(f"\n📊 Found {len(matches)} matches:")
                    for i, (name, price) in enumerate(matches, 1):
                        print(f"  {i}. {name:30s} ₹{price:>10,.2f}")
                    print()
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"✗ Error: {e}\n")


# Example usage
if __name__ == "__main__":
    # Method 1: Interactive mode (recommended)
    fetcher = InteractiveStockFetcher()
    fetcher.run()
    
    # Method 2: Direct scraping (for programmatic use)
    # scraper = ScreenerPriceScraper(headless=True)
    # prices = scraper.scrape_all_prices()
    # 
    # print("\nAll NIFTY-50 Prices:")
    # for company, price in prices.items():
    #     print(f"{company:30s} ₹{price:>10,.2f}")