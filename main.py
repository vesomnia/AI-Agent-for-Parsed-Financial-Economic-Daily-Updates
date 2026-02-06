from brain import MarketAnalyst
from notify import Notifier
from datetime import datetime

def run_mission():
    print(f"--- Mission Start: {datetime.now()} ---")
    
    # 1. Initialize
    analyst = MarketAnalyst()
    notifier = Notifier()

    # 2. Generate Intelligence
    # The analyst will fetch data internally and return the text
    report = analyst.generate_briefing()

    # 3. Dispatch
    if report:
        notifier.send_report(report)
    else:
        print("   [!] Report generation failed. Aborting dispatch.")

    print("--- Mission Complete ---")

if __name__ == "__main__":
    run_mission()
