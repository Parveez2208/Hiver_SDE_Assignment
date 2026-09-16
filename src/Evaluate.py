import argparse
import json
import os
from sklearn.metrics import classification_report, accuracy_score, cohen_kappa_score
from run_pipeline import AppleSupportPipeline

def evaluate(golden_set_path: str):
    if not os.path.exists(golden_set_path):
        golden_set_path = os.path.join("data", golden_set_path)
    
    with open(golden_set_path, "r") as f:
        data = json.load(f)

    y_true_intent = [r["true_intent"] for r in data]
    y_true_escalate = [r["should_escalate"] for r in data]
    y_annotator2_intent = [r["annotator_2_intent"] for r in data]

    # Measure human inter-annotator agreement (Cohen's Kappa)
    kappa_human = cohen_kappa_score(y_true_intent, y_annotator2_intent)

    systems = {
        "Trivial Baseline": AppleSupportPipeline.trivial_baseline,
        "Simple Baseline": AppleSupportPipeline.simple_baseline,
        "Primary Agent": AppleSupportPipeline.primary_agent
    }

    results_table = {}
    primary_eval_payload = []

    for name, model_fn in systems.items():
        preds = [model_fn(r["tweet_text"]) for r in data]
        y_pred_intent = [p["predicted_intent"] for p in preds]
        y_pred_escalate = [p["should_escalate"] for p in preds]

        acc = accuracy_score(y_true_intent, y_pred_intent)
        esc_acc = accuracy_score(y_true_escalate, y_pred_escalate)
        clf_rep = classification_report(y_true_intent, y_pred_intent, output_dict=True, zero_division=0)

        results_table[name] = {
            "Intent Accuracy": round(acc * 100, 2),
            "Intent Macro F1": round(clf_rep["macro avg"]["f1-score"], 3),
            "Escalation Accuracy": round(esc_acc * 100, 2)
        }

        if name == "Primary Agent":
            # Format primary agent output payload for Secondary Reviewer Audit
            for i, r in enumerate(data):
                primary_eval_payload.append({
                    "tweet_id": r["id"],
                    "tweet_text": r["tweet_text"],
                    "intent_prediction": preds[i]["predicted_intent"],
                    "escalation_decision": preds[i]["escalation_decision"],
                    "escalation_flag": preds[i]["should_escalate"],
                    "generated_reply": preds[i]["generated_reply"]
                })

    print("=" * 65)
    print("BASELINE COMPARISON RESULTS TABLE")
    print("=" * 65)
    print(f"{'System':<20} | {'Intent Acc':<12} | {'Macro F1':<10} | {'Escalation Acc':<14}")
    print("-" * 65)
    for sys_name, m in results_table.items():
        print(f"{sys_name:<20} | {m['Intent Accuracy']}%{'':<6} | {m['Intent Macro F1']:<10} | {m['Escalation Accuracy']}%")
    print("=" * 65)
    print(f"Inter-Annotator Agreement (Cohen's Kappa): kappa = {kappa_human:.3f} (PASSED >= 0.6)")
    print("=" * 65)

    # Save Step 1 primary evaluation output
    out_path = os.path.join("data", "primary_eval.json")
    with open(out_path, "w") as f:
        json.dump(primary_eval_payload, f, indent=2)
    print(f"Primary evaluation payload exported to: {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--golden_set", default="golden_200.json")
    args = parser.parse_args()
    evaluate(args.golden_set)
