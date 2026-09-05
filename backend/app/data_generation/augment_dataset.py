from pathlib import Path
import random
import pandas as pd


DOCUMENT_DIR = Path("data/raw/documents")
LABEL_FILE = Path("data/labels/document_labels.csv")


COMMON_SENTENCES = [
    "The team reviewed the operational status of the assigned resources.",
    "Personnel recorded the observations and submitted the report for further review.",
    "The activity included coordination between multiple teams.",
    "The report contained information about equipment, personnel and operational procedures.",
    "Several resources were inspected during the activity.",
    "The findings were documented for future analysis.",
    "The team completed the required assessment and recorded the results.",
    "Additional monitoring was recommended after the initial assessment.",
]


CATEGORY_CONTENT = {

    "Emergency": [
        "The response team assessed the incident and coordinated emergency procedures.",
        "Personnel were deployed following an unexpected event.",
        "The team reviewed evacuation and rescue procedures.",
        "Emergency resources were allocated to support the affected area.",
    ],

    "Technical": [
        "Engineers inspected the communication and computing systems.",
        "Technical personnel reviewed system performance and configuration.",
        "Hardware and software components were examined during the assessment.",
        "The engineering team performed diagnostics on the system.",
    ],

    "Logistics": [
        "The logistics team reviewed inventory and transportation requirements.",
        "Equipment and supplies were scheduled for movement.",
        "Resource quantities were recorded and compared with requirements.",
        "Transportation and supply availability were assessed.",
    ],

    "Infrastructure": [
        "The facility and supporting infrastructure were inspected.",
        "The assessment included buildings, network connectivity and maintenance requirements.",
        "Infrastructure conditions were documented for future maintenance.",
        "The facility team reviewed structural and network requirements.",
    ],

    "Public Safety": [
        "Safety procedures and emergency preparedness were reviewed.",
        "Potential hazards were identified during the inspection.",
        "The team evaluated evacuation procedures and public safety requirements.",
        "Emergency preparedness and safety communication were assessed.",
    ],

    "Administrative": [
        "Administrative procedures and documentation requirements were reviewed.",
        "The management team discussed policy compliance and reporting.",
        "Approval procedures and official records were examined.",
        "The team reviewed administrative workflows and documentation.",
    ],
}


LOCATIONS = [
    "Delhi",
    "Pune",
    "Jaipur",
    "Chandigarh",
    "Lucknow",
    "Bengaluru",
    "Hyderabad",
    "Ahmedabad",
]


def create_document(category, index):

    category_sentence = random.choice(
        CATEGORY_CONTENT[category]
    )

    common_sentence = random.choice(
        COMMON_SENTENCES
    )

    location = random.choice(LOCATIONS)

    personnel = random.randint(10, 250)

    response_time = random.randint(10, 120)

    text = (
        f"The activity was conducted in {location}. "
        f"{common_sentence} "
        f"{category_sentence} "
        f"The report recorded {personnel} personnel "
        f"and approximately {response_time} minutes "
        f"of processing or response time."
    )

    # Add an unrelated sentence sometimes.
    if random.random() < 0.5:

        text += " " + random.choice(
            COMMON_SENTENCES
        )

    filename = (
        f"augmented_"
        f"{category.lower().replace(' ', '_')}_"
        f"{index:03d}.txt"
    )

    path = DOCUMENT_DIR / filename

    path.write_text(
        text,
        encoding="utf-8"
    )

    return filename


def main():

    random.seed(123)

    df = pd.read_csv(
        LABEL_FILE
    )

    rows = []

    next_id = len(df) + 1

    # 12 additional documents per category
    for category in CATEGORY_CONTENT:

        for _ in range(12):

            filename = create_document(
                category,
                next_id
            )

            rows.append({
                "document_id": f"DOC-{next_id:04d}",
                "filename": filename,
                "category": category
            })

            next_id += 1

    new_df = pd.DataFrame(rows)

    df = pd.concat(
        [df, new_df],
        ignore_index=True
    )

    df.to_csv(
        LABEL_FILE,
        index=False
    )

    print(
        f"Dataset now contains {len(df)} documents."
    )

    print(
        "\\nDocuments per category:"
    )

    print(
        df["category"].value_counts()
    )


if __name__ == "__main__":
    main()