import json
from entry_engine import entry_logic, create_entry_intent_log
from invalidation_engine import validate_setup
from risk_levels import calculate_risk_level
from market_state_gate import market_state_gateway
from setup_scorer import getSetupScore
from audit_logger import create_audit_log
from backtester import backtest_summary

def main():

    try:
         with open("config/setup_submission.json") as f:
            config = json.load(f)
            validate_setup(config)
    except FileNotFoundError:

        return {"error": "Config file not found"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON"}
    except Exception as e:
        return {"error": str(e)}

     # Enrty logic
    try: 
        create_entry_intent_log()
        final_df = entry_logic(config)
    except Exception as e:
        return f"Error: {e}"
    

    # calculate Risk level
    risk_level_result = calculate_risk_level( config["risk_management"]["stop_loss"]["setup_score"], config["risk_management"]["stop_loss"]["atr_multiplier"] )
   
    # Market Risk gateway
    df = market_state_gateway(final_df)

    setup_score_df = getSetupScore(df)

    create_audit_log(config, df)
    
    backtest_summary(df)

if __name__ == "__main__":
    main()