# AI-Agent-for-Parsed-Financial-Economic-Daily-Updates
├── .env                # (Hidden) Keys and Passwords
├── venv/               # (Hidden) Python Libraries
├── main.py             # The coordinator script
├── modules/
│   ├── fetcher.py      # Gets the data
│   ├── brain.py        # Analyzes the data
│   └── notify.py       # Sends the email
└── requirements.txt    # List of libraries (yfinance, etc.)
Above section is the basc structure of this agent, this will be a step by step on how to create your own. I built mine within a Hostinger VPS server. 

Phase 1
Step 1: [ sudo apt update && sudo apt upgrade -y ] to update linux system. 
Step 2: [ sudo apt install python3-pip python3-venv -y ] to insatl python and python virtual environment. 
Step 3: [ mkdir market_agent ] create directory (you can name this whatever you like) 
Step 3.5: [ cd market_agent ] move to directory 
Step 4: [ python3 -m venv venv ] create environment, and [ source venv/bin/activate ] activate it
Step 5: [ pip install pandas_ta requests_cache user_agent ]
Step 6: [ pip install markdown ]
Step 7: [ pip install yfinance fredapi feedparser python-dotenv google-generativeai requests ] istall this set of python libraries. reasoning in following 6 lines 
yfinance: For market data (stocks, crypto, volume).
fredapi: For the Federal Reserve economic data.
feedparser: For reading RSS news feeds (Reuters, CNBC, etc.).
python-dotenv: For managing your security keys.
google-generativeai: For accessing the Gemini API (the brain).
requests: For general web requests.

Phase 2 
Step 1: Get FRED api key from: fred.stlouisfed.org get gemini API key from aistudio.google.com/app/apikey, get congressional API key from api.congress.gov get Finnhub key from finnhub.io/register
Step 2: [ nano .env ] create environment variable inside the market_agent folder 
Step 3: paste the following six lines into you .env file, put corresponding key after each "=" sign. after "EMAIL_USER" put your email, and after "EMAIL_PASSWORD" put your 16 letter "app password" from your google account, this is found in 2FA, just look it up. 

FRED_API_KEY=
GEMINI_API_KEY=
EMAIL_USER=
EMAIL_PASSWORD=
CONGRESS_KEY=
FINNHUB_KEY=

Step 4: [ nano fetcher.py ] paste the code titled fetcher.py into the file then Ctrl+X, then Y, then Enter. This is the main engine, it finds all the data from the APIs
Step 5: [ nano brain.py ] paste the code titled brain.py into the file then Ctrl+X, then Y, then Enter. This is the parser, it condenses and explains the raw data

Phase 3
Step 1: [ nano notify.py ] paste the code titled notify.py save/exit. This creates and sends the email with the info parsed by the brain 
Step 2: [ nano main.py ] paste the code titled main.py save/exit. This is the manager of the other components 
Step 3: Find the full path for your python executable. If you used the titles I provided the path will be [ /root/market_agent/venv/bin/python3 ] otherwise 
bash: [ which python3 ] and [ pwd ]
once in the absolute path bash: [ crontab -e ] when it asks for an editor choose 1 for nano, then scroll to the bottom and paste the following line 
0 6 * * 1-5 cd /root/market_agent && /root/market_agent/venv/bin/python3 main.py >> log.txt 2>&1

*NOTES* 
in your fetcher in line titled self.watchlist you can change this to be any stocks of your choosing, this is my list and the one in the file : 
self.watchlist = ['CRM', 'NOW', 'PLTR', 'AMZN', 'OKLO', 'BWXT', 'VST', 'BEPC', 'DLR', 'IEI', 'LQD', 'GLD', 'SCCO', 'RNMBY', 'HXSCL', 'EWY', 'INDA']
any and all files can be edited by bashing: nano "file name" then saving. 
you can edit the time when the email is sent by changing  the crontab (line 49) 
