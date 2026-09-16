import argparse
import json
import re

class AppleSupportPipeline:
    INTENT_KEYWORDS = {
        "ACCOUNT_SECURITY_ICLOUD": ["icloud", "apple id", "password", "locked", "hacked", "verification", "2fa"],
        "BILLING_SUBSCRIPTIONS": ["charge", "billed", "refund", "subscription", "apple music", "in-app", "receipt"],
        "HARDWARE_PHYSICAL_DAMAGE": ["screen", "shattered", "cracked", "water", "port", "dropped", "broken", "bent"],
        "BATTERY_PERFORMANCE": ["battery", "draining", "health", "warm", "standby", "charge percentage"],
        "SOFTWARE_OS_BUG": ["ios", "update", "lag", "crash", "frozen", "logo", "stuttering", "gesture"],
        "CONNECTIVITY_BLUETOOTH_WIFI": ["wi-fi", "wifi", "bluetooth", "pair", "airpods", "hotspot", "disconnecting"]
    }

    ESCALATION_MAP = {
        "ACCOUNT_SECURITY_ICLOUD": "Escalate: Account compromised or credentials locked.",
        "BILLING_SUBSCRIPTIONS": "Escalate: Financial dispute or refund request.",
        "HARDWARE_PHYSICAL_DAMAGE": "Escalate: Physical repair inspection required.",
        "other": "Escalate: Unrecognized query or out-of-scope intent."
    }

    # Baseline 1: Trivial Baseline (Predicts majority class)
    @staticmethod
    def trivial_baseline(text: str) -> dict:
        return {
            "predicted_intent": "CONNECTIVITY_BLUETOOTH_WIFI",
            "escalation_decision": "Auto-handled",
            "should_escalate": False,
            "generated_reply": "Please restart your Wi-Fi router and try connecting again."
        }

    # Baseline 2: Simple Baseline (First-hit keyword matching)
    @classmethod
    def simple_baseline(cls, text: str) -> dict:
        text_lower = text.lower()
        for intent, kws in cls.INTENT_KEYWORDS.items():
            if any(k in text_lower for k in kws):
                esc = cls.ESCALATION_MAP.get(intent, "Auto-handled")
                return {
                    "predicted_intent": intent,
                    "escalation_decision": esc,
                    "should_escalate": esc != "Auto-handled",
                    "generated_reply": "Thank you for contacting Apple Support. Please review our support documents."
                }
        return {
            "predicted_intent": "other",
            "escalation_decision": "Escalate: Unrecognized query or out-of-scope intent.",
            "should_escalate": True,
            "generated_reply": "Please contact our customer support team directly."
        }

    # Primary Agent: Ranked scoring + policy enforcement + DM grounding
    @classmethod
    def primary_agent(cls, text: str) -> dict:
        text_lower = text.lower()
        scores = {}
        for intent, kws in cls.INTENT_KEYWORDS.items():
            scores[intent] = sum(1 for k in kws if k in text_lower)
        
        best_intent, score = max(scores.items(), key=lambda x: x[1])
        if score == 0:
            best_intent = "other"

        escalation = cls.ESCALATION_MAP.get(best_intent, "Auto-handled")
        should_escalate = escalation != "Auto-handled"

        # Formulate grounded, compliant reply under 280 characters
        if should_escalate:
            reply = f"We take this issue seriously. Please send us a DM with your details so our team can securely assist: apple.co/DM"
        else:
            reply = f"We'd love to help resolve this {best_intent.replace('_', ' ').lower()} issue. Try restarting, or DM us if it persists."

        # Strict Regex verification constraint check
        assert re.match(r'^(Auto-handled|Escalate: .*)$', escalation), "Escalation format invalid!"

        return {
            "predicted_intent": best_intent,
            "escalation_decision": escalation,
            "should_escalate": should_escalate,
            "generated_reply": reply
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--brand", default="AppleSupport")
    parser.add_argument("--sample", action="store_true")
    args = parser.parse_args()

    test_tweet = "@AppleSupport I was double-charged for my cloud storage subscription!"
    result = AppleSupportPipeline.primary_agent(test_tweet)
    print(f"Pipeline sanity test successful for {args.brand}:")
    print(json.dumps(result, indent=2))
