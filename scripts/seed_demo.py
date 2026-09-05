from pathlib import Path

from backend.app.services.document_service import process_document


DATA_DIR = Path("data/raw/documents")


def seed_demo():
    files = sorted(
        [
            *DATA_DIR.glob("*.txt"),
            *DATA_DIR.glob("*.pdf"),
        ]
    )

    if not files:
        print("No demo documents found.")
        return

    print(f"Found {len(files)} demo documents.")
    print("-" * 60)

    successful = 0
    failed = 0

    for file_path in files:
        suffix = file_path.suffix.lower()

        try:
            result = process_document(
                path=str(file_path),
                suffix=suffix,
                filename=file_path.name,
            )

            if result.get("status") == "success":
                successful += 1

                category = result["classification"]["category"]
                risk = result["risk"]["risk_score"]
                priority = result["risk"]["priority"]
                anomaly = result["anomaly"]["is_anomaly"]

                print(
                    f"✓ {file_path.name} | "
                    f"{category} | "
                    f"Risk: {risk} | "
                    f"Priority: {priority} | "
                    f"Anomaly: {anomaly}"
                )

            else:
                failed += 1
                print(
                    f"✗ {file_path.name} | "
                    f"{result.get('message', 'Unknown error')}"
                )

        except Exception as e:
            failed += 1
            print(f"✗ {file_path.name} | {e}")

    print("-" * 60)
    print("Demo seeding completed.")
    print(f"Successful: {successful}")
    print(f"Failed:     {failed}")


if __name__ == "__main__":
    seed_demo()