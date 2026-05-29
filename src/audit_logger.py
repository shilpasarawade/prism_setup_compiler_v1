import pandas as pd
import json
import uuid
from datetime import datetime
 
def create_audit_log(config, df):

    for i in range(len(df)):
        row = df.iloc[i]
        audit_log = {

            # -------------------------
            # Audit metadata
            # -------------------------
            "audit_id": str(uuid.uuid4()),
            "timestamp": str(datetime.now()),

            # -------------------------
            # Trade details
            # -------------------------
            "trade": {

                "symbol": config['symbol'],
                "setup_type": config['setup_type'],
                "entry_type": config['entry_type'],
                "entry_price": row["entry_price"],
                "stop_loss": row['stop_loss'],
                "target_1": row['T1'],
                "target_2": row['T2'],
                "trade_status": row['trade_status']
            },

            # -------------------------
            # Risk details
            # -------------------------
            "risk": {
                "R": round(row['entry_price'] - row['stop_loss'],2 ),
                "ttl": row['exit_time'] - row['entry_time'],
                "setup_score": row['setup_score']
            },

            # -------------------------
            # Market state
            # -------------------------
            "market_context": {"market_state": row['market_state']}
        }
        save_audit_log(audit_log)
    print("audit_log.json created successfully")


def save_audit_log(audit_log):

    filename = "outputs/audit_log.json"

    # -------------------------
    # Append JSON logs
    # -------------------------
    try:

        with open(filename, "r") as f:

            logs = json.load(f)

    except:

        logs = []
      
   
    logs.append(audit_log)

    with open(filename, "w") as f:

        json.dump(
            logs,
            f,
            indent=4,
            default=str
        )

    

