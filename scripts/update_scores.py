import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from safety.risk_engine import update_risk_scores

if __name__ == "__main__":
    print("Updating risk scores...")
    update_risk_scores()
    print("Risk scores update complete.")
