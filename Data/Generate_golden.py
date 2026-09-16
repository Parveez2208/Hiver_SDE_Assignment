import json
import random
import pandas as pd

random.seed(42)

intents = [
    ("ACCOUNT_SECURITY_ICLOUD", "Escalate: Account compromised or credentials locked.", True),
    ("BILLING_SUBSCRIPTIONS", "Escalate: Financial dispute or refund request.", True),
    ("HARDWARE_PHYSICAL_DAMAGE", "Escalate: Physical repair inspection required.", True),
    ("BATTERY_PERFORMANCE", "Auto-handled", False),
    ("SOFTWARE_OS_BUG", "Auto-handled", False),
    ("CONNECTIVITY_BLUETOOTH_WIFI", "Auto-handled", False),
    ("other", "Escalate: Unrecognized query or out-of-scope intent.", True),
]

templates = {
    "ACCOUNT_SECURITY_ICLOUD": [
        "Locked out of my Apple ID after suspicious login alert.",
        "Need help recovering my iCloud account credentials.",
        "Two-factor verification codes not sending to my trusted number.",
        "Someone hacked my iCloud and changed the recovery email."
    ],
    "BILLING_SUBSCRIPTIONS": [
        "Charged twice for Apple Music subscription this month.",
        "Requesting a refund for an accidental App Store in-app purchase.",
        "Why was my card billed $9.99 without authorization?",
        "Need receipt and billing clarification for Apple Care charge."
    ],
    "HARDWARE_PHYSICAL_DAMAGE": [
        "iPhone screen shattered after dropping it on concrete.",
        "Back glass cracked and camera lens is scratched.",
        "Lightning port loose and pins seem bent inside.",
        "Device liquid damaged after falling into water."
    ],
    "BATTERY_PERFORMANCE": [
        "Battery health dropped to 78% within five months.",
        "Phone battery draining 20% per hour on standby.",
        "iPhone gets unusually warm while charging on standard brick.",
        "Sudden battery percentage drops from 40% to zero."
    ],
    "SOFTWARE_OS_BUG": [
        "iOS update froze my screen on the Apple logo.",
        "Keyboard lag and stuttering across apps after system update.",
        "Camera app crashing immediately upon launch.",
        "Control Center gestures unresponsive after waking device."
    ],
    "CONNECTIVITY_BLUETOOTH_WIFI": [
        "Wi-Fi keeps disconnecting every few minutes on 5GHz band.",
        "AirPods won't pair with MacBook Bluetooth.",
        "Bluetooth toggle grayed out in Settings app.",
        "Personal Hotspot fails to assign IP address to connected iPad."
    ],
    "other": [
        "What time does the Regent Street Apple Store close tonight?",
        "Are trade-in values higher in September?",
        "Nice keynote presentation yesterday, loved the wallpaper!",
        "Where can I find employment opportunities at corporate HQ?"
    ]
}

dataset = []
sample_csv_data = []

# Generate 200 items (~28-30 per category, satisfying >=15 rule)
for intent_name, escalation_reason, should_escalate in intents:
    queries = templates[intent_name]
    count = 30 if intent_name != "other" else 20
    for i in range(count):
        base_query = random.choice(queries)
        tweet = f"@AppleSupport {base_query} [ref-{random.randint(100, 999)}]"
        
        # Dual-annotator simulation for Kappa validation (90% agreement, 10% edge-case drift)
        annotator_2_intent = intent_name if random.random() > 0.10 else "other"
        annotator_2_escalate = should_escalate if random.random() > 0.08 else not should_escalate

        record = {
            "id": len(dataset) + 1,
            "tweet_text": tweet,
            "true_intent": intent_name,
            "should_escalate": should_escalate,
            "escalation_reason": escalation_reason,
            "annotator_2_intent": annotator_2_intent,
            "annotator_2_escalate": annotator_2_escalate
        }
        dataset.append(record)
        sample_csv_data.append({"tweet_id": record["id"], "text": tweet, "author_id": f"user_{record['id']}"})

# Expand sample_data.csv to 500 rows for quick local reproduction
while len(sample_csv_data) < 500:
    idx = len(sample_csv_data) + 1
    sample_csv_data.append({
        "tweet_id": idx,
        "text": f"@AppleSupport Random support inquiry test record #{idx}",
        "author_id": f"user_{idx}"
    })

with open("golden_200.json", "w") as f:
    json.dump(dataset, f, indent=2)

pd.DataFrame(sample_csv_data).to_csv("sample_data.csv", index=False)
print(f"Generated golden_200.json ({len(dataset)} rows) and sample_data.csv ({len(sample_csv_data)} rows).")
