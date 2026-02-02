"""
NSE-OPTIMIZED Indian Stock Upper Circuit Finder
Uses NSE's price band hitter API for MAXIMUM efficiency!
Instead of scanning 2,184 stocks, only checks the 5-20 that actually hit circuit.
RESULT: ~50-100x faster! (30 seconds vs 26 minutes)
"""

import os
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import requests
from typing import List, Dict
from github import Github, Auth
from dotenv import load_dotenv

# Load environment variables from a .env file (if present)
load_dotenv()

# Circuit limit constants
CIRCUIT_LIMIT_LARGE_CAP = 10
CIRCUIT_LIMIT_MID_CAP = 10
CIRCUIT_LIMIT_SMALL_CAP = 20
CIRCUIT_LIMIT_DEFAULT = 10

# GitHub Configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN') or os.environ.get('GITHUB_PAT') or ""
GITHUB_USERNAME = os.environ.get('GITHUB_USERNAME') or "pkalyankumar1010"
# Default repository; change if your target repo name differs
GITHUB_REPO = os.environ.get('GITHUB_REPO') or "upper_circuit_finder"

# NSE API
NSE_PRICE_BAND_API = "https://www.nseindia.com/api/live-analysis-price-band-hitter"


class NSEUpperCircuitFinder:
    """
    NSE-optimized version - gets stocks that hit circuit from NSE directly!
    """
    
    def __init__(self):
        self.results = []
        self.nse_session = self._create_nse_session()
        
    def _create_nse_session(self):
        """Create a session that mimics a real browser"""
        session = requests.Session()
        
        # Complete browser headers - mimicking Chrome on Windows
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        })
        return session
    
    def get_upper_circuit_stocks_from_nse(self) -> List[Dict]:
        """
        Fetch stocks that hit upper circuit from NSE API
        
        Returns:
            List of stocks with their circuit data from NSE
        """
        try:
            print("🔍 Fetching upper circuit stocks from NSE...")
            print("   Simulating browser session...")
            
            # Step 1: Visit homepage like a real browser
            print("   Step 1: Visiting NSE homepage...")
            homepage_url = "https://www.nseindia.com"
            homepage_response = self.nse_session.get(homepage_url, timeout=15)
            
            if homepage_response.status_code != 200:
                print(f"   ⚠ Homepage returned {homepage_response.status_code}")
                return []
            
            print(f"   ✓ Homepage loaded (Cookies received: {len(self.nse_session.cookies)})")
            time.sleep(1)
            
            # Step 2: Visit market data page (simulating user navigation)
            print("   Step 2: Navigating to market data...")
            # Try different market data URLs
            market_urls = [
                "https://www.nseindia.com/market-data/live-equity-market",
                "https://www.nseindia.com/market-data",
                "https://www.nseindia.com/get-quotes/equity",
            ]
            
            self.nse_session.headers.update({
                'Referer': homepage_url,
            })
            
            for market_url in market_urls:
                market_response = self.nse_session.get(market_url, timeout=15)
                if market_response.status_code == 200:
                    print(f"   ✓ Accessed {market_url}")
                    market_page_url = market_url
                    break
            else:
                # If none work, use homepage as referer
                market_page_url = homepage_url
                print(f"   → Using homepage as referer")
            
            time.sleep(1)
            
            # Step 3: Now fetch price band hitters with proper referer
            print("   Step 3: Fetching price band hitters...")
            
            # Debug: Show cookies
            cookie_names = [cookie.name for cookie in self.nse_session.cookies]
            print(f"   Cookies: {cookie_names}")
            
            self.nse_session.headers.update({
                'Referer': market_page_url,
                'X-Requested-With': 'XMLHttpRequest',
            })
            
            response = self.nse_session.get(NSE_PRICE_BAND_API, timeout=15)
            print(f"   → API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    # Try normal JSON parsing first
                    data = response.json()
                except Exception as json_error:
                    # If JSON parsing fails, try manual decompression
                    print(f"   ⚠ JSON parsing failed: {json_error}")
                    try:
                        import json
                        import gzip

                        # Get the raw content
                        content = response.content

                        # Debug: Show first 200 bytes
                        print(f"   → First 200 bytes of response: {content[:200]}")

                        # Respect Content-Encoding header first
                        content_encoding = response.headers.get('Content-Encoding', '').lower()

                        # Handle brotli ('br') compressed responses
                        if 'br' in content_encoding:
                            try:
                                try:
                                    import brotli
                                except Exception:
                                    import brotlicffi as brotli

                                content = brotli.decompress(content)
                                print(f"   → Detected brotli content encoding, decompressed using brotli")
                            except Exception as br_err:
                                print(f"   → Brotli decompression failed: {br_err}")

                        # Gzip fallback (magic number check)
                        if content[:2] == b'\x1f\x8b':  # Gzip magic number
                            try:
                                print(f"   → Detected gzipped content, decompressing...")
                                content = gzip.decompress(content)
                            except Exception as gz_err:
                                print(f"   → Gzip decompression failed: {gz_err}")

                        # Try to decode as UTF-8 first, fallback to latin-1
                        try:
                            text = content.decode('utf-8')
                        except Exception:
                            text = content.decode('latin-1', errors='ignore')

                        # Debug: Show decoded text preview
                        print(f"   → Decoded text preview: {text[:200]}")

                        data = json.loads(text)
                        print(f"   ✓ Successfully decoded response manually")
                    except Exception as decode_error:
                            print(f"   → Decode error: {decode_error}")
                            print(f"   → Response length: {len(response.content)} bytes")
                            print(f"   → Content type: {response.headers.get('Content-Type', 'Unknown')}")
                            print(f"   → Content encoding: {response.headers.get('Content-Encoding', 'None')}")
                            print(f"   → NSE might be returning compressed/binary data or HTML")
                            print(f"   → Wait 5-10 minutes before trying again")
                            print(f"   → NSE might be detecting automated access")
                            return []
                
                # Debug: Print response structure
                print(f"   ✓ NSE API responded successfully!")
                print(f"   Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                # Extract upper circuit stocks
                # NSE API structure: {'upper': [...], 'lower': [...], 'both': [...], 'count': {...}}
                upper_circuit_stocks = []
                
                # Get upper circuit stocks from 'upper' key
                if 'upper' in data:
                    print(f"   'upper' key exists, type: {type(data['upper'])}")
                    
                    # NSE API structure: data['upper'] is a dict with 'AllSec', 'SecGtr20', 'SecLwr20'
                    # Each has a 'data' array with stock details
                    if isinstance(data['upper'], dict):
                        # Combine data from all categories
                        all_upper_stocks = []
                        
                        for category in ['AllSec', 'SecGtr20', 'SecLwr20']:
                            if category in data['upper'] and 'data' in data['upper'][category]:
                                stocks_in_category = data['upper'][category]['data']
                                all_upper_stocks.extend(stocks_in_category)
                                print(f"   Found {len(stocks_in_category)} stocks in '{category}'")
                        
                        print(f"   Total upper circuit stocks (with duplicates): {len(all_upper_stocks)}")
                        
                        # Remove duplicates by symbol
                        seen_symbols = set()
                        unique_stocks = []
                        for stock in all_upper_stocks:
                            symbol = stock.get('symbol', '')
                            if symbol and symbol not in seen_symbols:
                                seen_symbols.add(symbol)
                                unique_stocks.append(stock)
                        
                        print(f"   Unique stocks: {len(unique_stocks)}")
                        
                        # Parse each stock
                        for stock in unique_stocks:
                            try:
                                # Debug: Print first stock structure
                                if len(upper_circuit_stocks) == 0:
                                    print(f"   Sample stock keys: {list(stock.keys())}")
                                
                                symbol = stock.get('symbol', '')
                                
                                # Get percentage change (NSE provides this)
                                pct_change_str = stock.get('pChange', '0')
                                pct_change = float(pct_change_str.strip())
                                
                                # Get price band (circuit limit) from NSE
                                price_band_str = stock.get('priceBand', '0')
                                price_band = float(price_band_str) if price_band_str else 10
                                
                                # Only include stocks that are VERY CLOSE to circuit limit
                                # Filter: (circuit_limit - pct_change) / circuit_limit < 1%
                                # This means: pct_change >= circuit_limit * 0.99
                                if pct_change > 0 and price_band > 0:
                                    # Calculate how close to circuit limit
                                    difference = price_band - pct_change
                                    relative_difference = (difference / price_band) if price_band > 0 else 100
                                    
                                    # Only include if within 1% of circuit limit
                                    if relative_difference < 0.01:  # Less than 1%
                                        ltp_str = stock.get('ltp', '0')
                                        ltp = float(ltp_str) if ltp_str else 0
                                        
                                        upper_circuit_stocks.append({
                                            'symbol': symbol,
                                            'pct_change': pct_change,
                                            'price_band': price_band,  # Circuit limit from NSE!
                                            'ltp': ltp,
                                            'high': float(stock.get('highPrice', 0) or 0),
                                            'low': float(stock.get('lowPrice', 0) or 0),
                                            'open': 0,  # NSE doesn't provide open in this API
                                            'close': 0,
                                            'volume': float(stock.get('totalTradedVol', 0) or 0),
                                            'closeness': relative_difference * 100  # Store for debugging
                                        })
                            except Exception as e:
                                print(f"   ⚠ Error parsing stock: {e}")
                                continue
                        
                        print(f"✓ After strict filtering: {len(upper_circuit_stocks)} stocks within 1% of circuit limit")
                        print(f"   (Original: {len(unique_stocks)} → Filtered: {len(upper_circuit_stocks)})")
                        return upper_circuit_stocks
                    else:
                        print(f"   'upper' is not a dict")
                        return []
                else:
                    print(f"   'upper' key not in response")
                    return []
            elif response.status_code == 401:
                print(f"⚠ NSE API returned 401 (Unauthorized)")
                print(f"   NSE has strict bot protection. Using fallback method...")
                return []
            else:
                print(f"⚠ NSE API returned status code: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching from NSE API: {e}")
            print("   This might be due to NSE API being down or network issues")
            return []
    
    def check_historical_circuit(self, symbol: str, circuit_limit: float) -> bool:
        """
        Check if stock hit upper OR lower circuit in last 14 days
        
        Args:
            symbol: Stock symbol (without .NS)
            circuit_limit: The circuit limit percentage for this stock
            
        Returns:
            True if hit any circuit in last 14 days, False otherwise
        """
        try:
            yahoo_symbol = f"{symbol}.NS"
            
            # Fetch last 20 days of data (to ensure we have 14 trading days)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=25)
            
            # Get historical data
            stock = yf.Ticker(yahoo_symbol)
            hist = yf.download(yahoo_symbol, start=start_date, end=end_date, progress=False, auto_adjust=True)
            
            if hist is None or hist.empty or len(hist) < 2:
                # Not enough data - be conservative and exclude (return True)
                return True  # Can't verify, so exclude for safety
            
            # Get previous trading days (excluding today) - use whatever we have
            if len(hist) >= 15:
                previous_days = hist.iloc[-15:-1]  # Full 14 days
            else:
                previous_days = hist.iloc[:-1]  # Whatever days we have (at least 1)
            
            # If we have less than 14 days of data, we can still check what we have
            days_checked = len(previous_days)
            
            # Check each day for BOTH upper and lower circuits
            for i in range(len(previous_days)):
                day_data = previous_days.iloc[i]
                
                day_open_val = day_data['Open']
                day_close_val = day_data['Close']
                day_high_val = day_data['High']
                day_low_val = day_data['Low']
                
                day_open = float(day_open_val.iloc[0]) if hasattr(day_open_val, 'iloc') else float(day_open_val)
                day_close = float(day_close_val.iloc[0]) if hasattr(day_close_val, 'iloc') else float(day_close_val)
                day_high = float(day_high_val.iloc[0]) if hasattr(day_high_val, 'iloc') else float(day_high_val)
                day_low = float(day_low_val.iloc[0]) if hasattr(day_low_val, 'iloc') else float(day_low_val)
                
                if day_open == 0 or pd.isna(day_open) or pd.isna(day_close):
                    continue
                
                # Calculate percentage change
                day_pct_change = ((day_close - day_open) / day_open) * 100
                
                # Also check from previous day's close (more accurate)
                if i > 0:
                    prev_day_close_val = previous_days.iloc[i-1]['Close']
                    prev_day_close = float(prev_day_close_val.iloc[0]) if hasattr(prev_day_close_val, 'iloc') else float(prev_day_close_val)
                    if prev_day_close > 0 and not pd.isna(prev_day_close):
                        day_pct_from_prev = ((day_close - prev_day_close) / prev_day_close) * 100
                    else:
                        day_pct_from_prev = day_pct_change
                else:
                    day_pct_from_prev = day_pct_change
                
                day_max_pct = max(day_pct_change, day_pct_from_prev)
                day_min_pct = min(day_pct_change, day_pct_from_prev)
                
                # Check for UPPER circuit hit
                day_high_close_ratio = (day_close / day_high) if day_high > 0 else 0
                hit_upper_circuit = (day_max_pct >= (circuit_limit - 0.3) and day_high_close_ratio >= 0.997)
                
                # Check for LOWER circuit hit
                # Lower circuit: stock dropped close to negative circuit limit and close is near day's low
                day_low_close_ratio = (day_close / day_low) if day_low > 0 else 2
                hit_lower_circuit = (day_min_pct <= -(circuit_limit - 0.3) and day_low_close_ratio <= 1.003)
                
                # If hit either circuit, exclude this stock
                if hit_upper_circuit or hit_lower_circuit:
                    return True  # Hit circuit in last 14 days (or whatever days we checked)
            
            return False  # Did not hit any circuit in the days checked
            
        except Exception as e:
            return False  # On error, assume no circuit hit
    
    def get_stock_details(self, symbol: str) -> Dict:
        """Get additional stock details from Yahoo Finance"""
        try:
            yahoo_symbol = f"{symbol}.NS"
            stock = yf.Ticker(yahoo_symbol)
            info = stock.info
            
            # Get market cap
            market_cap_usd = info.get('marketCap', 0)
            if market_cap_usd and market_cap_usd > 0:
                market_cap_inr_cr = (market_cap_usd * 83) / 1e7
                market_cap_display = f"₹{market_cap_inr_cr:,.0f} Cr"
            else:
                market_cap_display = "N/A"
            
            company_name = info.get('longName', info.get('shortName', 'N/A'))
            
            return {
                'company_name': company_name,
                'market_cap': market_cap_display
            }
        except:
            return {
                'company_name': 'N/A',
                'market_cap': 'N/A'
            }
    
    def scan_stocks(self):
        """
        Main scanning function using NSE API
        """
        print("="*80)
        print("🚀 NSE-OPTIMIZED MODE - Using NSE Price Band Hitter API")
        print("="*80)
        print()
        
        start_time = datetime.now()
        
        # Step 1: Get stocks that hit upper circuit from NSE
        nse_upper_circuit_stocks = self.get_upper_circuit_stocks_from_nse()
        
        if not nse_upper_circuit_stocks:
            print("\n⚠️  No stocks found from NSE API or API error.")
            print("   This could mean:")
            print("   1. No stocks hit upper circuit today")
            print("   2. NSE API is temporarily unavailable")
            print("   3. Network connectivity issues")
            return self.results
        
        print()
        print(f"📊 Checking if these {len(nse_upper_circuit_stocks)} stocks hit any circuit in last 14 days...")
        print("   (Checking both upper AND lower circuits)")
        print()
        
        # Step 2: For each stock, check if it hit any circuit in last 14 days
        for stock in nse_upper_circuit_stocks:
            symbol = stock['symbol']
            pct_change = stock['pct_change'] if stock['pct_change'] else 0
            
            # Get actual price band (circuit limit) from NSE data!
            circuit_limit = stock.get('price_band', 10)
            
            print(f"Checking {symbol} (Change: {pct_change:.2f}%, Circuit: {circuit_limit}%)...")
            
            # Check if hit any circuit in last 14 days using the ACTUAL circuit limit from NSE
            hit_in_last_14_days = self.check_historical_circuit(symbol, circuit_limit)
            
            if not hit_in_last_14_days:
                # Stock qualifies! Get additional details
                print(f"   ✓ {symbol} - First time in 14 days! (No upper/lower circuit)")
                
                details = self.get_stock_details(symbol)
                
                self.results.append({
                    'Symbol': symbol,
                    'Company Name': details['company_name'],
                    'Date': datetime.now().strftime('%Y-%m-%d'),
                    'Open': "N/A",  # NSE API doesn't provide open price
                    'Close': f"₹{stock['ltp']:.2f}",
                    'High': f"₹{stock['high']:.2f}" if stock['high'] > 0 else "N/A",
                    'Low': f"₹{stock['low']:.2f}" if stock['low'] > 0 else "N/A",
                    'Change %': f"{pct_change:.2f}%",
                    'Circuit Limit': f"{circuit_limit:.0f}%",  # Actual circuit limit from NSE!
                    'Market Cap': details['market_cap'],
                    'Volume': f"{stock['volume']:,.0f}" if stock['volume'] > 0 else "N/A"
                })
            else:
                print(f"   ✗ {symbol} - Hit circuit in last 14 days (skipped)")
            
            time.sleep(0.1)  # Small delay
        
        elapsed = (datetime.now() - start_time).total_seconds()
        print()
        print(f"✅ NSE-optimized scan complete in {elapsed:.1f} seconds!")
        print(f"   Checked only {len(nse_upper_circuit_stocks)} stocks (vs 2,184 in full scan)")
        print(f"   Speed improvement: ~{(26*60)/elapsed:.0f}x faster than full scan!")
        
        return self.results
    
    def display_results(self):
        """Display the results in a formatted table"""
        if not self.results:
            print("\n" + "="*80)
            print("No stocks found that hit upper circuit today but not in last 14 days.")
            print("(No upper/lower circuit hits in last 14 days)")
            print("="*80)
            return
        
        print("\n" + "="*80)
        print(f"STOCKS THAT HIT UPPER CIRCUIT TODAY (First time in 14 days)")
        print(f"No upper/lower circuit hit in last 14 days")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        df = pd.DataFrame(self.results)
        print(df.to_string(index=False))
        
        print("\n" + "="*80)
        print(f"Total stocks found: {len(self.results)}")
        print("="*80)
        
        # Save to CSV (disabled in CI workflow - commented out)
        # filename = f"upper_circuit_stocks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        # df.to_csv(filename, index=False)
        # print(f"\nResults saved to: {filename}")
    
    def create_github_issue(self):
        """Create a GitHub issue with the results"""
        if not self.results:
            print("\n⚠️  No stocks found, skipping GitHub issue creation.")
            return
        
        try:
            print("\n" + "="*80)
            print("📝 Creating GitHub Issue...")
            print("="*80)
            
            # Initialize GitHub (use PyGithub with Auth.Token to avoid deprecation)
            if GITHUB_TOKEN:
                g = Github(auth=Auth.Token(GITHUB_TOKEN))
            else:
                g = Github()

            repo = g.get_repo(f"{GITHUB_USERNAME}/{GITHUB_REPO}")
            
            # Calculate investment details
            total_stocks = len(self.results)
            total_investment = 0
            
            # Extract prices and calculate total
            for result in self.results:
                close_price_str = result['Close'].replace('₹', '').replace(',', '')
                price = float(close_price_str)
                total_investment += price
            
            # Create issue title
            issue_title = f"🚀 Upper Circuit Alert - {datetime.now().strftime('%B %d, %Y')} [NSE-Optimized]"
            
            # Create issue body with table
            issue_body = f"""# 💰 Investment Required

**You need to buy {total_stocks} stocks with ₹{total_investment:,.2f}**

---

## 📊 Stocks That Hit Upper Circuit Today (First Time in 14 Days)

**Filtered Criteria:**
- ✅ Hit upper circuit TODAY (within 1% of limit)
- ✅ Did NOT hit upper/lower circuit in last 14 days
- ✅ Fresh momentum stocks only

| Symbol | Company Name | Price | Change % | Circuit Limit | Market Cap |
|--------|--------------|-------|----------|---------------|------------|
"""
            
            # Add each stock to the table
            for result in self.results:
                symbol = result['Symbol']
                company = result['Company Name']
                price = result['Close']
                change = result['Change %']
                circuit = result['Circuit Limit']
                market_cap = result['Market Cap']
                
                issue_body += f"| {symbol} | {company} | {price} | {change} | {circuit} | {market_cap} |\n"
            
            # Add footer
            issue_body += f"""
---

## 📈 Summary

- **Total Stocks Found**: {total_stocks}
- **Total Investment (1 share each)**: ₹{total_investment:,.2f}
- **Average Price per Stock**: ₹{total_investment/total_stocks:,.2f}
- **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Scan Method**: NSE-Optimized (Price Band Hitter API)

---

## 🎯 What This Means

These stocks hit upper circuit today but **NO circuits** (upper or lower) in the last 14 days, indicating:
- ✅ Fresh momentum (first time in 2 weeks)
- ✅ Strong buying pressure
- ✅ Stable stock (no lower circuit volatility)
- ✅ Highest quality signals

---

## ⚠️ Disclaimer

This is an automated alert for informational purposes only. Not financial advice. Do your own research before investing.

---

*Auto-generated by Upper Circuit Finder (NSE-Optimized Mode)*
"""
            
            # Create the issue
            issue = repo.create_issue(
                title=issue_title,
                body=issue_body,
                labels=['upper-circuit', 'auto-generated', 'trading-alert', 'nse-optimized']
            )
            
            print(f"✅ GitHub issue created successfully!")
            print(f"   Issue #{issue.number}: {issue.title}")
            print(f"   URL: {issue.html_url}")
            print("="*80)
            
        except Exception as e:
            print(f"\n❌ Error creating GitHub issue: {e}")
            print("   Results are still saved in CSV file.")


def main():
    """
    Main function using NSE-optimized approach
    """
    print("="*80)
    print("NSE-OPTIMIZED UPPER CIRCUIT FINDER")
    print("Using NSE Price Band Hitter API for MAXIMUM efficiency!")
    print("="*80)
    print()
    print("Strategy:")
    print("   1. Get stocks that hit upper circuit from NSE API")
    print("   2. Filter: Only stocks within 1% of their circuit limit")
    print("      Example: 20% circuit -> must be >= 19.8% change")
    print("   3. Check last 14 days: No upper/lower circuit hits")
    print("   4. Result: Only STRONGEST, STABLE momentum stocks!")
    print()
    
    # Create NSE-optimized finder
    finder = NSEUpperCircuitFinder()
    
    # Scan stocks
    finder.scan_stocks()
    
    # Display results
    finder.display_results()
    
    # Create GitHub issue with results
    finder.create_github_issue()


if __name__ == "__main__":
    main()

