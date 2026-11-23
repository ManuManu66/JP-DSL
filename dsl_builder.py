"""
Bridges the JSON storage used by the web IDE with the textX grammar and
validators the team already defined and tested (pizzeria.tx, validator.py,
validate_catalog.py).

Every time an order or the catalog is created/edited through the IDE, we
render it back into real Pizzeria DSL syntax, parse it with the SAME
grammar used in class, and run it through the SAME validation functions.
If the grammar or the validators reject it, the IDE refuses to save it.
This keeps the web app from ever drifting away from the language we
defined in the Rules and Grammar document.
"""

import os
from textx import metamodel_from_file

GRAMMAR_PATH = os.path.join(os.path.dirname(__file__), "pizzeria.tx")
_mm = metamodel_from_file(GRAMMAR_PATH)


def _escape(value: str) -> str:
    # The grammar's STRING token doesn't define escape sequences, so we
    # just strip quotes the user might have typed instead of rejecting them.
    return (value or "").replace('"', "'")


def render_catalog_block(catalog: dict) -> str:
    return (
        "catalog {\n"
        f"    crusts: {', '.join(catalog['crusts'])}\n"
        f"    sauces: {', '.join(catalog['sauces'])}\n"
        f"    cheeses: {', '.join(catalog['cheeses'])}\n"
        f"    toppings: {', '.join(catalog['toppings'])}\n"
        f"    drinks: {', '.join(catalog['drinks'])}\n"
        "}\n"
    )


def _render_item(item: dict) -> str:
    if item["type"] == "pizza":
        toppings = item.get("toppings") or []
        lines = [
            f"        {item['quantity']} pizza {{",
            f"            crust: {item['crust']},",
            f"            sauce: {item['sauce']},",
            f"            cheese: {item['cheese']}" + ("," if toppings else ""),
        ]
        if toppings:
            lines.append(f"            toppings: {', '.join(toppings)}")
        lines.append("        }")
        return "\n".join(lines) + "\n"
    else:  # drink
        return f"        {item['quantity']} drink {item['drink']}\n"


def render_order_block(order: dict) -> str:
    items_text = "\n".join(_render_item(i) for i in order["items"])
    return (
        "order {\n"
        f'    customer: "{_escape(order["customer"])}"\n'
        f'    contact: "{_escape(order["contact"])}"\n'
        f"    status: {order['status']}\n"
        "    items {\n"
        f"{items_text}"
        "    }\n"
        "}\n"
    )


def validate_catalog_data(catalog: dict):
    """Parse + validate a standalone catalog block. Returns (ok, errors)."""
    from validate_catalog import validate_catalog

    text = render_catalog_block(catalog)
    try:
        model = _mm.model_from_str(text)
    except Exception as exc:
        return False, [f"Grammar error: {exc}"]

    catalog_model = model.declarations[0]
    errors = validate_catalog(catalog_model)
    return (len(errors) == 0), errors


def validate_order_data(order: dict, catalog: dict):
    """Parse + validate a single order against the given catalog.

    Returns (ok, errors).
    """
    from validator import validate_order

    text = render_catalog_block(catalog) + "\n" + render_order_block(order)
    try:
        model = _mm.model_from_str(text)
    except Exception as exc:
        return False, [f"Grammar error: {exc}"]

    catalog_model = next(
        d for d in model.declarations if d.__class__.__name__ == "CatalogDecl"
    )
    order_model = next(
        d for d in model.declarations if d.__class__.__name__ == "OrderDecl"
    )
    errors = validate_order(order_model, catalog_model)
    return (len(errors) == 0), errors
