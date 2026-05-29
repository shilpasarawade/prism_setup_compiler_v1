from jsonschema import validate
from jsonschema.exceptions import ValidationError


# -------------------------
# Trade Schema
# -------------------------
trade_schema = {

    "type": "object",
    "properties": {
        "timestamp": {
            "type": "string"
        },

        "symbol": {
            "type": "string"
        },

        "setup_type": {
            "type": "string",
            "enum": [
                "BREAKOUT",
                "REVERSAL",
                "TREND_FOLLOWING"
            ]
        },

        "entry_type": {
            "type": "string",
            "enum": [
                "RETEST",
                "MARKET",
                "LIMIT"
            ]
        },

        "entry_price": {
            "type": "number",
            "exclusiveMinimum": 0
        },

        "stop_loss": {
            "type": "number"
        },

        "R": {
            "type": "number",
            "exclusiveMinimum": 0
        },

        "T1": {
            "type": "number"
        },

        "T2": {
            "type": "number"
        },

        "setup_score": {
            "type": "number",
            "minimum": 0,
            "maximum": 10
        },

        "tier": {
            "type": "string",
            "enum": [
                "IGNORE",
                "MINIMUM",
                "STRONG",
                "PREMIUM"
            ]
        },

        "ttl": {
            "type": "integer",
            "exclusiveMinimum": 0
        },

        "atr_14": {
            "type": "number"
        },

        "vwap": {
            "type": "number"
        }
    },

    "required": [
        "timestamp",
        "symbol",
        "setup_type",
        "entry_type",
        "entry_price",
        "stop_loss",
        "R",
        "T1",
        "T2",
        "setup_score",
        "tier",
        "ttl"
    ]
}

def validate_trade_schema(trade_data):

    try:
        validate(
            instance=trade_data,
            schema=trade_schema
        )

        print("✅ Schema validation passed")
        return True
    except ValidationError as e:
        print("❌ Schema validation failed")
        print("Error:", e.message)

        return False

def main():

    trade = {

        "timestamp": "2026-05-29 10:15:00",

        "symbol": "RELIANCE.NS",

        "setup_type": "BREAKOUT",

        "entry_type": "RETEST",

        "entry_price": 2950,

        "stop_loss": 2938,

        "R": 12,

        "T1": 2968,

        "T2": 2980,

        "setup_score": 7.8,

        "tier": "PREMIUM",

        "ttl": 300,

        "atr_14": 10.5,

        "vwap": 2945
    }

    validate_trade_schema(trade)


if __name__ == "__main__":
    main()