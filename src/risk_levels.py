def calculate_risk_level(setup_score, R_multiple):

    # -------------------------
    # PREMIUM
    # -------------------------
    if (
        setup_score >= 7.5 and
        R_multiple >= 2.5
    ):

        return {
            "risk_level": "PREMIUM",
            "position_size_pct": 100
        }

    # -------------------------
    # STRONG
    # -------------------------
    elif (
        setup_score >= 6.5 and
        R_multiple >= 2.0
    ):

        return {
            "risk_level": "STRONG",
            "position_size_pct": 75
        }

    # -------------------------
    # MINIMUM
    # -------------------------
    elif (
        setup_score >= 5.5 and
        R_multiple >= 1.5
    ):

        return {
            "risk_level": "MINIMUM",
            "position_size_pct": 40
        }

    # -------------------------
    # IGNORE
    # -------------------------
    else:

        return {
            "risk_level": "IGNORE",
            "position_size_pct": 0
        }
