import re


# --------------------------------------------------
# Risk keywords
# --------------------------------------------------

HIGH_RISK_KEYWORDS = {
    "attack",
    "breach",
    "threat",
    "critical",
    "casualty",
    "intrusion",
    "explosion",
    "fire",
    "failure",
    "emergency",
    "unauthorized",
    "incident",
    "compromise",
}

MEDIUM_RISK_KEYWORDS = {
    "delay",
    "damage",
    "inspection",
    "warning",
    "issue",
    "disruption",
    "malfunction",
    "response",
    "affected",
}


# --------------------------------------------------
# Category risk weights
# --------------------------------------------------

CATEGORY_RISK = {
    "Emergency": 30,
    "Public Safety": 25,
    "Technical": 20,
    "Infrastructure": 20,
    "Logistics": 15,
    "Administrative": 5,
}


def calculate_risk(
    text: str,
    category: str,
    classification_confidence: float,
    is_anomaly: bool,
    anomaly_score: float,
    entities: dict,
) -> dict:

    score = 0
    reasons = []

    text_lower = text.lower()

    # --------------------------------------------------
    # 1. Category risk
    # --------------------------------------------------

    category_score = CATEGORY_RISK.get(
        category,
        10
    )

    score += category_score

    if category_score >= 25:

        reasons.append(
            f"{category} documents receive elevated priority"
        )

    elif category_score >= 15:

        reasons.append(
            f"{category} classification indicates operational relevance"
        )

    # --------------------------------------------------
    # 2. Anomaly
    # --------------------------------------------------

    if is_anomaly:

        score += 25

        reasons.append(
            "Document was flagged as anomalous"
        )

    # --------------------------------------------------
    # 3. High-risk keywords
    # --------------------------------------------------

    found_high_risk = []

    for keyword in HIGH_RISK_KEYWORDS:

        if re.search(
            rf"\b{re.escape(keyword)}\b",
            text_lower
        ):

            found_high_risk.append(keyword)

    if found_high_risk:

        score += min(
            len(found_high_risk) * 5,
            20
        )

        reasons.append(
            "High-risk indicators detected: "
            + ", ".join(sorted(found_high_risk))
        )

    # --------------------------------------------------
    # 4. Medium-risk keywords
    # --------------------------------------------------

    found_medium_risk = []

    for keyword in MEDIUM_RISK_KEYWORDS:

        if re.search(
            rf"\b{re.escape(keyword)}\b",
            text_lower
        ):

            found_medium_risk.append(keyword)

    if found_medium_risk:

        score += min(
            len(found_medium_risk) * 2,
            10
        )

        reasons.append(
            "Operational indicators detected: "
            + ", ".join(sorted(found_medium_risk))
        )

    # --------------------------------------------------
    # 5. Personnel involvement
    # --------------------------------------------------

    personnel = entities.get(
        "quantities",
        []
    )

    personnel_mentions = [
        item
        for item in personnel
        if re.search(
            r"\b(personnel|officers|staff|members|people)\b",
            item,
            re.IGNORECASE
        )
    ]

    if personnel_mentions:

        score += 5

        reasons.append(
            "Personnel involvement detected"
        )

    # --------------------------------------------------
    # 6. Location
    # --------------------------------------------------

    locations = entities.get(
        "locations",
        []
    )

    if locations:

        score += 5

        reasons.append(
            "Operational location detected"
        )

    # --------------------------------------------------
    # Keep score between 0 and 100
    # --------------------------------------------------

    score = min(
        max(score, 0),
        100
    )

    # --------------------------------------------------
    # Priority
    # --------------------------------------------------

    if score >= 70:

        priority = "CRITICAL"

    elif score >= 50:

        priority = "HIGH"

    elif score >= 30:

        priority = "MEDIUM"

    else:

        priority = "LOW"

    return {
        "risk_score": score,
        "priority": priority,
        "reasons": reasons,
        "high_risk_indicators": sorted(
            found_high_risk
        ),
        "operational_indicators": sorted(
            found_medium_risk
        ),
    }