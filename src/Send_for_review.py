import json
import os
import requests

def execute_audit():
    input_path = os.path.join("data", "primary_eval.json")
    output_path = os.path.join("data", "final_audit_report.json")

    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found. Run 'python src/evaluate.py' first.")
        return

    with open(input_path, "r") as f:
        payload = json.load(f)

    url = "http://127.0.0.1:8000/audit"
    print(f"Sending {len(payload)} items to Reviewer Service via HTTP POST...")

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        report = response.json()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to http://127.0.0.1:8000.")
        print("Make sure 'python src/reviewer_service.py' is running in another terminal.")
        return

    with open(output_path, "w") as f:
        json.dump(report, f, indent=4)

    print("\n" + "=" * 55)
    print("STEP 4: FINAL AUDIT REPORT GENERATED")
    print("=" * 55)
    print(json.dumps(report, indent=2))
    print(f"\nUnified integrity report saved to: {output_path}")

if __name__ == "__main__":
    execute_audit()
