import os
import yfinance as yf
from fredapi import Fred
import feedparser
import requests
import requests_cache
import pandas_ta as ta
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta
import logging

# SILENCE NOISE: Stop yfinance from printing 404 errors for ETFs
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

# Load environment variables
load_dotenv()

# OPTIMIZATION: Cache API calls for 15 minutes
requests_cache.install_cache('market_cache', expire_after=900)

class MarketDataFetcher:
    def __init__(self):
        self.fred_key = os.getenv('FRED_API_KEY')
        self.finnhub_key = os.getenv('FINNHUB_KEY')
        self.congress_key = os.getenv('CONGRESS_KEY')
        
        if self.fred_key:
            self.fred = Fred(api_key=self.fred_key)
            
        # YOUR WATCHLIST
        self.watchlist = ['CRM', 'NOW', 'PLTR', 'AMZN', 'OKLO', 'BWXT', 'VST', 'BEPC', 'DLR', 'IEI', 'LQD', 'GLD', 'SCCO', 'RNMBY', 'HXSCL', 'EWY', 'INDA']

    # --- SECTION 1: POLITICS & POLICY (NEW) ---
    def get_committee_hearings(self):
        """Fetches upcoming hearings in Finance/Banking committees."""
        print("   [+] Scanning Committee Schedule...")
        if not self.congress_key: return "No Congress Key"
        url = f"https://api.congress.gov/v3/committee-meeting?api_key={self.congress_key}&limit=5"
        try:
            data = requests.get(url).json()
            hearings = []
            if 'committeeMeetings' not in data: return "No hearings found."
            for meeting in data['committeeMeetings']:
                topic = meeting.get('title', '').lower()
                # Filter for impactful topics
                if any(x in topic for x in ['bank', 'finance', 'crypto', 'tech', 'china', 'tax']):
                    date_str = meeting.get('date', 'N/A')
                    title = meeting.get('title', 'No Title')
                    hearings.append(f"📅 {date_str}: {title[:80]}...")
            return "\n".join(hearings) if hearings else "No major financial hearings."
        except: return "Committee Data Unavailable"

    def get_recent_nominations(self):
        """Fetches recent nominations for regulators (SEC, Fed, etc)."""
        print("   [+] Fetching Nominations...")
        if not self.congress_key: return "No Congress Key"
        url = f"https://api.congress.gov/v3/nomination?api_key={self.congress_key}&limit=10&sort=receivedDate"
        try:
            data = requests.get(url).json()
            noms = []
            if 'nominations' not in data: return "No nominations."
            for nom in data['nominations']:
                desc = nom.get('description', '').lower()
                if any(x in desc for x in ['secretary', 'governor', 'commissioner']):
                    clean = nom.get('description', '').split("vice")[0].strip()
                    noms.append(f"- {clean[:90]}...")
            return "\n".join(noms[:3]) if noms else "No major nominations."
        except: return "Nomination Data Unavailable"

    def get_legislation_radar(self):
        """Fetches bills that are actually moving."""
        print("   [+] Fetching Active Legislation...")
        if not self.congress_key: return "No Congress Key"
        url = f"https://api.congress.gov/v3/bill?api_key={self.congress_key}&limit=5&sort=latestAction"
        try:
            data = requests.get(url).json()
            bills = []
            if 'bills' not in data: return "No bills found."
            for bill in data['bills']:
                title = bill.get('title', 'No Title')
                action = bill.get('latestAction', {}).get('text', '')
                if "Referred" not in action and "Introduced" not in action:
                     bills.append(f"📜 {title[:60]}... \n   STATUS: {action[:50]}")
            return "\n".join(bills[:3]) if bills else "No major bills moving."
        except: return "Legislation Data Unavailable"

    # --- SECTION 2: MACRO & MARKETS ---
    def get_macro_economics(self):
        print("   [+] Fetching Expanded Macro Data (FRED)...")
        try:
            if not self.fred_key: return {}
            series_ids = {
                '10Y Yield': 'DGS10', 'Fed Funds Rate': 'FEDFUNDS', 
                'CPI': 'CPIAUCSL', 'PCE': 'PCE', 'Unemployment': 'UNRATE', 
                'Real GDP': 'GDPC1', 'M2 Supply': 'M2SL'
            }
            data = {}
            for name, sid in series_ids.items():
                try:
                    val = self.fred.get_series_latest_release(sid).iloc[-1]
                    data[name] = f"${val:,.0f}B" if 'GDP' in name or 'M2' in name else f"{val:.2f}%"
                except: data[name] = "N/A"
            return data
        except: return {}

    def get_fear_and_greed(self):
        print("   [+] Fetching Fear & Greed...")
        try:
            url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            data = r.json()['fear_and_greed']
            return f"{int(data['score'])}/100 ({data['rating'].upper()})"
        except: return "Unavailable"

    def get_market_performance(self):
        print("   [+] Fetching Indices...")
        tickers = {'S&P 500': '^GSPC', 'Nasdaq': '^IXIC', 'Bitcoin': 'BTC-USD'}
        snapshot = {}
        for name, sym in tickers.items():
            try:
                hist = yf.Ticker(sym).history(period="5d")
                if not hist.empty:
                    last = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2]
                    pct = ((last - prev) / prev) * 100
                    snapshot[name] = f"{last:,.2f} ({pct:+.2f}%)"
            except: snapshot[name] = "N/A"
        return snapshot

    def get_global_markets(self):
        print("   [+] Fetching Global Indices...")
        indices = {'Nikkei (Japan)': '^N225', 'FTSE (UK)': '^FTSE', 'DAX (Germany)': '^GDAXI'}
        lines = []
        for name, ticker in indices.items():
            try:
                df = yf.Ticker(ticker).history(period="2d")
                if not df.empty:
                    pct = ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                    lines.append(f"{name}: {pct:+.2f}%")
            except: continue
        return " | ".join(lines)

    # --- SECTION 3: PORTFOLIO INTELLIGENCE ---
    def get_earnings_radar(self):
        print("   [+] Scanning Earnings Calendar...")
        warnings = []
        today = datetime.now()
        for symbol in self.watchlist:
            try:
                cal = yf.Ticker(symbol).calendar
                e_date = None
                if isinstance(cal, dict) and 'Earnings Date' in cal: e_date = cal['Earnings Date'][0]
                elif isinstance(cal, pd.DataFrame) and not cal.empty: e_date = cal.iloc[0, 0]
                
                if e_date and isinstance(e_date, (datetime, pd.Timestamp)):
                    days = (e_date.replace(tzinfo=None) - today).days
                    if 0 <= days <= 7: warnings.append(f"⚠️ {symbol}: In {days} days")
            except: continue
        return "\n".join(warnings) if warnings else "No earnings this week."

    def get_portfolio_data(self):
        print(f"   [+] Analyzing Portfolio ({len(self.watchlist)} assets)...")
        lines = []
        for sym in self.watchlist:
            try:
                df = yf.Ticker(sym).history(period="3mo")
                if df.empty: continue
                price = df['Close'].iloc[-1]
                pct = ((price - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                rsi = df.ta.rsi(length=14).iloc[-1]
                status = "HOT" if rsi > 70 else "COLD" if rsi < 30 else "OK"
                sma = df['Close'].rolling(50).mean().iloc[-1]
                trend = "UP" if price > sma else "DOWN"
                lines.append(f"{sym.ljust(5)}: ${price:<7.2f} ({pct:+.1f}%) | RSI:{int(rsi)}({status}) | {trend}")
            except: continue
        return "\n".join(lines)

    # --- SECTION 4: SENTIMENT & NEWS ---
    def get_crypto_onchain(self):
        print("   [+] Fetching Crypto...")
        try:
            data = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=solana,cardano&vs_currencies=usd&include_24hr_change=true").json()
            return " | ".join([f"{k.title()}:${v['usd']} ({v['usd_24h_change']:+.1f}%)" for k,v in data.items()])
        except: return "Unavailable"

    def get_tech_sentiment(self):
        print("   [+] Fetching Hacker News...")
        try:
            ids = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json").json()[:5]
            stories = [requests.get(f"https://hacker-news.firebaseio.com/v0/item/{i}.json").json().get('title') for i in ids]
            return "\n".join([f"- {s}" for s in stories])
        except: return "Unavailable"

    def get_insider_sentiment(self):
        print("   [+] Fetching Insider (Finnhub)...")
        if not self.finnhub_key: return "No Key"
        try:
            d = requests.get(f"https://finnhub.io/api/v1/stock/insider-sentiment?symbol=NVDA&from=2024-01-01&token={self.finnhub_key}").json()
            return f"Nvidia Insiders: MSPR {d['data'][0]['mspr']} (Positive=Buy)" if d['data'] else "No data"
        except: return "Unavailable"

    def get_news_headlines(self):
        print("   [+] Fetching Headlines...")
        urls = ['https://finance.yahoo.com/news/rssindex', 'http://feeds.marketwatch.com/marketwatch/topstories/']
        headlines = []
        for u in urls:
            try: 
                for e in feedparser.parse(u).entries[:2]: headlines.append(f"- {e.title}")
            except: continue
        return list(set(headlines))

    # --- COMPILE REPORT ---
    def compile_report(self):
        t = datetime.now().strftime("%Y-%m-%d")
        return f"""
=== INTELLIGENCE BRIEFING: {t} ===

[1] DC RADAR (Policy Risks)
---------------------------
> HEARINGS:
{self.get_committee_hearings()}
> NOMINATIONS:
{self.get_recent_nominations()}
> LEGISLATION:
{self.get_legislation_radar()}

[2] EARNINGS & GLOBAL
---------------------
{self.get_earnings_radar()}
Global: {self.get_global_markets()}

[3] PORTFOLIO HEALTH
--------------------
{self.get_portfolio_data()}

[4] MACRO DASHBOARD
-------------------
{chr(10).join([f"- {k}: {v}" for k,v in self.get_macro_economics().items()])}

[5] SENTIMENT SCANNERS
----------------------
Fear/Greed: {self.get_fear_and_greed()}
Insiders: {self.get_insider_sentiment()}
Crypto: {self.get_crypto_onchain()}

[6] TECH PULSE
--------------
{self.get_tech_sentiment()}

[7] HEADLINES
-------------
{chr(10).join(self.get_news_headlines())}
==================================
"""

if __name__ == "__main__":
    print(MarketDataFetcher().compile_report())
