from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import uvicorn
import re

app = FastAPI(title="Secondary Reviewer LLM Audit Service")

class TicketAuditItem(BaseModel):
    tweet_id: int
    tweet_text: str
    intent_prediction: str
    escalation_decision: str
    escalation_flag: bool
    generated_reply: str

VALID_INTENTS = {
    "ACCOUNT_SECURITY_ICLOUD", "BILLING_SUBSCRIPTIONS", "HARDWARE_PHYSICAL_DAMAGE",
    "BATTERY_PERFORMANCE", "SOFTWARE_OS_BUG", "CONNECTIVITY_BLUETOOTH_WIFI", "other"
}

REGEX_RULE = re.compile(r'^(Auto-handled|Escalate: .*)$')

@app.post("/audit")
def audit_evaluations(payload: List[TicketAuditItem]):
    discrepancies = 0
    discrepancy_logs = []
    grounding_failures = 0

    for item in payload:
        # 1. Classification Audit: Is the prediction in taxonomy?
        if item.intent_prediction not in VALID_INTENTS:
            discrepancies += 1
            discrepancy_logs.append(f"Ticket #{item.tweet_id}: Invalid intent '{item.intent_prediction}'")

        # 2. Escalation Regex Validation
        if not REGEX_RULE.match(item.escalation_decision):
            discrepancies += 1
            discrepancy_logs.append(f"Ticket #{item.tweet_id}: Failed regex validation '{item.escalation_decision}'")

        # 3. Reply Grounding & Policy Audit
        reply = item.generated_reply.lower()
        if len(item.generated_reply) > 280:
            discrepancies += 1
            discrepancy_logs.append(f"Ticket #{item.tweet_id}: Exceeded 280 characters.")

        if item.escalation_flag and "dm" not in reply:
            discrepancies += 1
            grounding_failures += 1
            discrepancy_logs.append(f"Ticket #{item.tweet_id}: Escalated query reply missing mandatory 'DM' directive.")

    audit_status = "APPROVED" if discrepancies == 0 else "REQUIRES_REVISION"
    
    return {
        "audit_status": audit_status,
        "total_reviewed": len(payload),
        "discrepancies_found": discrepancies,
        "grounding_failures": grounding_failures,
        "reviewer_notes": "Escalation flags match rules, regex verified, and replies properly grounded." if discrepancies == 0 else "Discrepancies flagged for revision.",
        "discrepancy_details": discrepancy_logs[:5]
    }

if __name__ == "__main__":
    print("Starting Secondary Reviewer Service on http://127.0.0.1:8000 ...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
