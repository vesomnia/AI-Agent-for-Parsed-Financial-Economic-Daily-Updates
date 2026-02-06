import os
import google.generativeai as genai
from dotenv import load_dotenv
from fetcher import MarketDataFetcher

load_dotenv()

class MarketAnalyst:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file.")
        
        genai.configure(api_key=api_key)
        # Using the latest Flash model
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.fetcher = MarketDataFetcher()

    def generate_briefing(self):
        print("   [+] Gathering raw data...")
        raw_data = self.fetcher.compile_report()
        
        print("   [+] Synthesizing analysis (Consulting Gemini)...")
        
        # === THE PERSONALITY UPGRADE ===
        prompt = f"""
        You are an elite financial educator and strategist. Your client is a smart investor who wants clarity, not jargon.
        
        I will provide raw data (Macro, Portfolio RSI, Congress Hearings, News).
        Your Job: Convert this into a "Daily Strategy Note."
        
        GUIDELINES FOR SIMPLICITY & DEPTH:
        1. **Explain the "So What?":** If the 10-Year Yield is up, don't just say it's up. Explain: "Rising yields make borrowing expensive, which often hurts growth stocks like Nvidia."
        2. **Use Analogies:** If discussing Inflation or Liquidity, use brief analogies (e.g., "The Fed is tightening the tap") to make it stick.
        3. **Connect the Dots:** If Congress is holding a crypto hearing AND Bitcoin is dropping, mention the connection.
        4. **Plain English:** Avoid "financialese." Use active verbs.
        5. **Portfolio Focus:** specifically mention risks to the user's watchlist (PLTR, AMZN, OKLO, etc.) if the data warrants it.
        
        RAW DATA:
        {raw_data}
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating analysis: {str(e)}"

if __name__ == "__main__":
    analyst = MarketAnalyst()
    print(analyst.generate_briefing())
