from collections import Counter

def exact_field_accuracy(expected,predicted,field_name:str)->float:
    expected=list(expected); predicted=list(predicted)
    if len(expected)!=len(predicted): raise ValueError("expected and predicted lengths differ")
    if not expected: raise ValueError("cannot evaluate an empty dataset")
    return sum(getattr(a,field_name)==getattr(b,field_name) for a,b in zip(expected,predicted,strict=True))/len(expected)

def dataset_summary(records):
    rows=list(records)
    return {"count":len(rows),"severity_counts":dict(Counter(r.severity for r in rows)),"failure_mode_counts":dict(Counter(r.failure_mode for r in rows)),"abstention_count":sum(r.abstain for r in rows),"human_review_count":sum(r.requires_human_review for r in rows)}
