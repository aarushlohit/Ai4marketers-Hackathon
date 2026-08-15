"""AST-based condition evaluator for workflows."""

import operator
from typing import Any, Dict

OPERATORS = {
    "eq": operator.eq,
    "ne": operator.ne,
    "gt": operator.gt,
    "lt": operator.lt,
    "gte": operator.ge,
    "lte": operator.le,
    "contains": lambda a, b: b in a if hasattr(a, "__contains__") else False,
}


def evaluate_condition(condition: Dict[str, Any], payload: Dict[str, Any]) -> bool:
    """
    Evaluate if payload matches the condition structure.
    
    Structure of condition:
      {
        "field": "health_score",
        "operator": "lt",
        "value": 50
      }
    Or nested conditions:
      {
        "logical": "and|or",
        "rules": [ ... ]
      }
    """
    if not condition:
        return True

    # Logical combined rules
    if "logical" in condition:
        logical = condition["logical"].lower()
        rules = condition.get("rules", [])
        if not rules:
            return True
        
        if logical == "and":
            return all(evaluate_condition(r, payload) for r in rules)
        elif logical == "or":
            return any(evaluate_condition(r, payload) for r in rules)
        else:
            raise ValueError(f"Unknown logical operator: {logical}")

    # Single rule evaluation
    field = condition.get("field")
    op_name = condition.get("operator")
    target_value = condition.get("value")

    if not field or not op_name:
        return False

    if field not in payload:
        return False

    payload_value = payload[field]
    op_func = OPERATORS.get(op_name)
    if not op_func:
        return False

    try:
        return op_func(payload_value, target_value)
    except Exception:
        return False
