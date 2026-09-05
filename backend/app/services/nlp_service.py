import re

try:
    import spacy

    nlp = spacy.load("en_core_web_sm")

except Exception:
    nlp = None


# --------------------------------------------------
# Known locations for our synthetic DefenceDoc data
# --------------------------------------------------

KNOWN_LOCATIONS = {
    "Delhi",
    "Pune",
    "Jaipur",
    "Chandigarh",
    "Lucknow",
    "Bengaluru",
    "Hyderabad",
    "Ahmedabad",
}


# --------------------------------------------------
# Helper: remove duplicates while preserving order
# --------------------------------------------------

def unique(values):

    seen = set()
    result = []

    for value in values:

        value = value.strip()

        if not value:
            continue

        key = value.lower()

        if key not in seen:

            seen.add(key)
            result.append(value)

    return result


# --------------------------------------------------
# Domain-specific quantity extraction
# --------------------------------------------------

def extract_domain_quantities(text: str):

    quantities = []

    patterns = [

        # Example:
        # 120 personnel
        r"\b\d+(?:\.\d+)?\s+(?:personnel|people|staff|officers|members)\b",

        # Example:
        # 47 minutes
        r"\b\d+(?:\.\d+)?\s+(?:seconds?|minutes?|hours?|days?)\b",

        # Example:
        # 25 vehicles
        r"\b\d+(?:\.\d+)?\s+(?:vehicles?|trucks?|cars?|units?)\b",

        # Example:
        # 15 systems
        r"\b\d+(?:\.\d+)?\s+(?:systems?|devices?|equipment)\b",

        # Example:
        # 50 kg
        r"\b\d+(?:\.\d+)?\s*(?:kg|kilograms?|km|kilometers?|m|meters?)\b",
    ]

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        quantities.extend(matches)

    return quantities


# --------------------------------------------------
# Number extraction
# --------------------------------------------------

def extract_numbers(text: str):

    return re.findall(
        r"\b\d+(?:\.\d+)?\b",
        text
    )


def extract_dates(text: str):

    patterns = [

        # 14/08/2026
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",

        r"\b\d{4}-\d{2}-\d{2}\b",

        r"\b(?:January|February|March|April|May|June|July|"
        r"August|September|October|November|December)"
        r"\s+\d{1,2}(?:,\s*\d{4})?\b",
    ]

    dates = []

    for pattern in patterns:

        dates.extend(
            re.findall(
                pattern,
                text,
                flags=re.IGNORECASE
            )
        )

    return dates

def extract_known_locations(text: str):

    locations = []

    for location in KNOWN_LOCATIONS:

        pattern = rf"\b{re.escape(location)}\b"

        if re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        ):

            locations.append(location)

    return locations

def extract_entities(text: str) -> dict:

    result = {
        "persons": [],
        "organizations": [],
        "locations": [],
        "dates": [],
        "quantities": [],
    }

    if nlp:

        doc = nlp(text)

        for ent in doc.ents:

            if ent.label_ == "PERSON":

                result["persons"].append(
                    ent.text
                )

            elif ent.label_ in {
                "ORG",
                "NORP"
            }:

                result["organizations"].append(
                    ent.text
                )

            elif ent.label_ in {
                "GPE",
                "LOC",
                "FAC"
            }:

                result["locations"].append(
                    ent.text
                )

            elif ent.label_ == "DATE":

                result["dates"].append(
                    ent.text
                )

            elif ent.label_ == "TIME":

                result["quantities"].append(
                    ent.text
                )

            elif ent.label_ == "QUANTITY":

                result["quantities"].append(
                    ent.text
                )

    result["locations"].extend(
        extract_known_locations(text)
    )

    result["dates"].extend(
        extract_dates(text)
    )

    result["quantities"].extend(
        extract_domain_quantities(text)
    )
    for key in result:

        result[key] = unique(
            result[key]
        )

    return result