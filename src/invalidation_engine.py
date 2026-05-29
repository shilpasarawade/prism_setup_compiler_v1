import json
from datetime import datetime


def validate_setup(config):

    errors = []
   
    # -------------------------
    # Required fields
    # -------------------------
    required_fields = [
        "setup_type",
        "entry_type",
        "weights",
        "atr_multiplier",
        "ttl",
        "target_r"
    ]

    for field in required_fields:
        if field not in config:
            errors.append(
                f"Missing field: {field}"
            )

    # -------------------------
    # Weight validation
    # -------------------------
    if "weights" in config:

        total_weight = sum(
            config["weights"].values()
        )

        if total_weight != 100:

            errors.append(
                f"Weight total is "
                f"{total_weight}, expected 100"
            )

    # -------------------------
    # Setup type validation
    # -------------------------
    valid_setup_types = [
        "BREAKOUT",
        "REVERSAL",
        "TREND_FOLLOWING"
    ]

    if (
        "setup_type" in config
        and
        config["setup_type"]
        not in valid_setup_types
    ):

        errors.append(
            "Invalid setup type"
        )

    # -------------------------
    # Entry type validation
    # -------------------------
    valid_entry_types = [
        "RETEST",
        "MARKET",
        "LIMIT"
    ]

    if (
        "entry_type" in config
        and
        config["entry_type"]
        not in valid_entry_types
    ):

        errors.append(
            "Invalid entry type"
        )
    # -------------------------
    # ATR validation
    # -------------------------
    if (
        "atr_multiplier" in config
        and
        config["atr_multiplier"] <= 0
    ):

        errors.append(
            "ATR multiplier must be positive"
        )
        
    # -------------------------
    # TTL validation
    # -------------------------
    if (
        "ttl" in config
        and
        config["ttl"]["bars"] <= 0
    ):

        errors.append(
            "TTL must be positive"
        )

    # -------------------------
    # Target R validation
    # -------------------------
    if "target_r" in config:

        target_r = config["target_r"]

        if any(r <= 0 for r in target_r):

            errors.append(
                "Invalid target R values"
            )
 
    # -------------------------
    # Final report
    # -------------------------
    report = {

        "report_timestamp":
        str(datetime.now()),

        "validation_status":

        "PASSED"
        if len(errors) == 0
        else "FAILED",

        "total_errors":
        len(errors),

        "errors":
        errors,

        "config_checked":
        config
    }

    save_setup_validation_report_log(report)
    print("Validation report saved" )
  

def save_setup_validation_report_log(report):

    filename = "outputs/setup_validation_report.json"

    try:
        with open(filename, "r") as f:
            logs = json.load(f)
    except:
        logs = []
      
   
    logs.append(report)

    with open(filename, "w") as f:

        json.dump(
            logs,
            f,
            indent=4,
            default=str
        )

