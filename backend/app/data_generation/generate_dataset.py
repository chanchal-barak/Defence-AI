from pathlib import Path
import random
import csv


OUTPUT_DIR = Path("data/raw/documents")
LABEL_FILE = Path("data/labels/document_labels.csv")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LABEL_FILE.parent.mkdir(parents=True, exist_ok=True)


TEMPLATES = {
    "Emergency": [
        "An emergency response operation was initiated after an incident was reported in {location}. Response teams were deployed and the situation was assessed. Personnel coordinated rescue and emergency response activities.",
        "An emergency incident occurred in {location}. The response team reached the affected area and initiated evacuation procedures. Resources were allocated to support the emergency operation.",
        "A disaster response exercise was conducted in {location}. Emergency personnel evaluated response time, evacuation procedures and coordination between response teams."
    ],

    "Technical": [
        "A technical inspection was conducted on the communication system at {location}. Engineers evaluated system performance, software configuration and hardware reliability.",
        "The technical team performed maintenance on the computing infrastructure at {location}. System logs were analyzed and software components were tested.",
        "A technical assessment identified several system configuration issues. Engineers performed diagnostics and recommended software and hardware improvements."
    ],

    "Logistics": [
        "A logistics report recorded the movement of equipment and supplies to {location}. Inventory levels were checked and transportation schedules were reviewed.",
        "The logistics team coordinated transportation of essential resources to {location}. Equipment quantities and supply requirements were recorded.",
        "An inventory assessment was completed for resources assigned to {location}. The logistics team reviewed equipment availability, transportation and supply requirements."
    ],

    "Infrastructure": [
        "An infrastructure inspection was conducted at {location}. The team evaluated facility conditions, network connectivity and structural requirements.",
        "The infrastructure team reviewed the condition of facilities at {location}. Maintenance requirements and network infrastructure were documented.",
        "A facility assessment identified infrastructure maintenance requirements. The inspection covered buildings, network systems and supporting infrastructure."
    ],

    "Public Safety": [
        "A public safety assessment was conducted in {location}. The team reviewed safety procedures, potential hazards and emergency preparedness.",
        "A safety inspection identified several potential hazards in {location}. Recommendations were provided to improve public safety and emergency preparedness.",
        "A disaster preparedness exercise was conducted in {location}. Safety procedures, evacuation plans and emergency communication were evaluated."
    ],

    "Administrative": [
        "An administrative review meeting was conducted at {location}. The team discussed operational procedures, documentation and approval requirements.",
        "Administrative procedures were reviewed by the management team. Documentation, policy compliance and reporting requirements were discussed.",
        "The administrative department completed a review of records and approval processes. Several documentation and reporting requirements were identified."
    ]
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
    "Bhopal",
    "Kolkata"
]


def generate_document(category, index):

    template = random.choice(TEMPLATES[category])

    location = random.choice(LOCATIONS)

    text = template.format(
        location=location
    )

    personnel = random.randint(10, 200)
    response_time = random.randint(10, 90)

    text += (
        f" The report recorded {personnel} personnel "
        f"and an estimated response or processing time "
        f"of {response_time} minutes."
    )

    filename = f"{category.lower().replace(' ', '_')}_{index:03d}.txt"

    path = OUTPUT_DIR / filename

    path.write_text(
        text,
        encoding="utf-8"
    )

    return filename


def main():

    random.seed(42)

    rows = []

    documents_per_category = 20

    document_id = 1

    for category in TEMPLATES:

        for _ in range(documents_per_category):

            filename = generate_document(
                category,
                document_id
            )

            rows.append({
                "document_id": f"DOC-{document_id:04d}",
                "filename": filename,
                "category": category
            })

            document_id += 1

    with LABEL_FILE.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "document_id",
                "filename",
                "category"
            ]
        )

        writer.writeheader()
        writer.writerows(rows)

    print(
        f"Generated {len(rows)} documents."
    )

    print(
        f"Labels saved to: {LABEL_FILE}"
    )


if __name__ == "__main__":
    main()