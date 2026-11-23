"""
John Papa's Pizzeria DSL - local IDE

One shared screen for the receptionist and kitchen staff (orders), and a
separate screen for the Domain Expert (catalog CRUD), matching the roles
defined in the Rules and Grammar document:

  - Receptionist: create / edit / cancel orders (only while "pending").
  - Kitchen staff: advance an order's status forward, one step at a time.
  - Domain Expert: add/remove catalog items (crusts, sauces, cheeses,
    toppings, drinks) -- the only place CRUD on terminal symbols happens.

Everything is persisted as JSON (data/orders.json, data/catalog.json).
Nothing leaves this machine.
"""

from flask import Flask, render_template, request, redirect, url_for, flash

import storage
from dsl_builder import validate_order_data, validate_catalog_data

app = Flask(__name__)
app.secret_key = "pizzeria-dsl-dev"  # local-only app, fine to hardcode

MAX_ITEM_ROWS = 8
MAX_TOPPINGS = 5


# ---------------------------------------------------------------- orders --

@app.route("/")
def index():
    orders = sorted(storage.load_orders(), key=lambda o: o["id"], reverse=True)
    return render_template(
        "index.html", orders=orders, status_flow=storage.STATUS_FLOW
    )


def _parse_items_from_form(form, catalog) -> list:
    items = []
    for i in range(1, MAX_ITEM_ROWS + 1):
        kind = form.get(f"item_type_{i}", "")
        if kind not in ("pizza", "drink"):
            continue

        quantity_raw = form.get(f"quantity_{i}", "").strip()
        try:
            quantity = int(quantity_raw)
        except ValueError:
            quantity = 0

        if kind == "pizza":
            toppings = form.getlist(f"toppings_{i}")[:MAX_TOPPINGS]
            items.append(
                {
                    "type": "pizza",
                    "quantity": quantity,
                    "crust": form.get(f"crust_{i}", ""),
                    "sauce": form.get(f"sauce_{i}", ""),
                    "cheese": form.get(f"cheese_{i}", ""),
                    "toppings": toppings,
                }
            )
        else:
            items.append(
                {
                    "type": "drink",
                    "quantity": quantity,
                    "drink": form.get(f"drink_{i}", ""),
                }
            )
    return items


@app.route("/orders/new", methods=["GET", "POST"])
def new_order():
    catalog = storage.load_catalog()

    if request.method == "POST":
        order = {
            "customer": request.form.get("customer", "").strip(),
            "contact": request.form.get("contact", "").strip(),
            "status": "pending",
            "items": _parse_items_from_form(request.form, catalog),
        }

        if not order["items"]:
            errors = ["An order needs at least one item."]
        else:
            ok, errors = validate_order_data(order, catalog)

        if not errors:
            storage.create_order(order)
            flash("Order created.", "success")
            return redirect(url_for("index"))

        return render_template(
            "order_form.html",
            catalog=catalog,
            order=order,
            errors=errors,
            max_rows=MAX_ITEM_ROWS,
            form_title="New order",
        )

    return render_template(
        "order_form.html",
        catalog=catalog,
        order=None,
        errors=[],
        max_rows=MAX_ITEM_ROWS,
        form_title="New order",
    )


@app.route("/orders/<int:order_id>/edit", methods=["GET", "POST"])
def edit_order(order_id):
    catalog = storage.load_catalog()
    existing = storage.get_order(order_id)

    if existing is None:
        flash("Order not found.", "error")
        return redirect(url_for("index"))

    if existing["status"] != "pending":
        flash("Only pending orders can be edited.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        order = {
            "id": order_id,
            "customer": request.form.get("customer", "").strip(),
            "contact": request.form.get("contact", "").strip(),
            "status": "pending",
            "items": _parse_items_from_form(request.form, catalog),
        }

        if not order["items"]:
            errors = ["An order needs at least one item."]
        else:
            ok, errors = validate_order_data(order, catalog)

        if not errors:
            storage.update_order(order)
            flash("Order updated.", "success")
            return redirect(url_for("index"))

        return render_template(
            "order_form.html",
            catalog=catalog,
            order=order,
            errors=errors,
            max_rows=MAX_ITEM_ROWS,
            form_title=f"Edit order #{order_id}",
        )

    return render_template(
        "order_form.html",
        catalog=catalog,
        order=existing,
        errors=[],
        max_rows=MAX_ITEM_ROWS,
        form_title=f"Edit order #{order_id}",
    )


@app.route("/orders/<int:order_id>/cancel", methods=["POST"])
def cancel_order(order_id):
    order = storage.get_order(order_id)
    if order is None:
        flash("Order not found.", "error")
    elif order["status"] != "pending":
        flash("Only pending orders can be cancelled.", "error")
    else:
        storage.set_status(order_id, "cancelled")
        flash(f"Order #{order_id} cancelled.", "success")
    return redirect(url_for("index"))


@app.route("/orders/<int:order_id>/advance", methods=["POST"])
def advance_order(order_id):
    order = storage.get_order(order_id)
    if order is None:
        flash("Order not found.", "error")
        return redirect(url_for("index"))

    flow = storage.STATUS_FLOW
    if order["status"] not in flow:
        flash("This order can no longer move forward.", "error")
        return redirect(url_for("index"))

    idx = flow.index(order["status"])
    if idx == len(flow) - 1:
        flash("Order is already completed.", "error")
        return redirect(url_for("index"))

    storage.set_status(order_id, flow[idx + 1])
    flash(f"Order #{order_id} moved to '{flow[idx + 1]}'.", "success")
    return redirect(url_for("index"))


# --------------------------------------------------------------- catalog --

@app.route("/catalog", methods=["GET", "POST"])
def catalog_view():
    catalog = storage.load_catalog()
    errors = []

    if request.method == "POST":
        action = request.form.get("action")
        category = request.form.get("category")
        value = (request.form.get("value") or "").strip().lower()

        if category not in catalog:
            errors = [f"Unknown category: {category}"]
        elif action == "add":
            if not value:
                errors = ["Enter a name before adding."]
            elif value in catalog[category]:
                errors = [f"'{value}' already exists in {category}."]
            else:
                new_catalog = {**catalog, category: catalog[category] + [value]}
                ok, errors = validate_catalog_data(new_catalog)
                if ok:
                    storage.save_catalog(new_catalog)
                    flash(f"Added '{value}' to {category}.", "success")
                    return redirect(url_for("catalog_view"))
        elif action == "remove":
            if value not in catalog[category]:
                errors = [f"'{value}' is not in {category}."]
            else:
                new_catalog = {
                    **catalog,
                    category: [v for v in catalog[category] if v != value],
                }
                ok, errors = validate_catalog_data(new_catalog)
                if ok:
                    storage.save_catalog(new_catalog)
                    flash(f"Removed '{value}' from {category}.", "success")
                    return redirect(url_for("catalog_view"))
        elif action == "update":
            old_value = (request.form.get("old_value") or "").strip().lower()
            if old_value not in catalog[category]:
                errors = [f"'{old_value}' is not in {category}."]
            elif not value:
                errors = ["Enter a new name before saving."]
            elif value == old_value:
                flash("No changes to save.", "success")
                return redirect(url_for("catalog_view"))
            elif value in catalog[category]:
                errors = [f"'{value}' already exists in {category}."]
            else:
                new_catalog = {
                    **catalog,
                    category: [
                        value if v == old_value else v for v in catalog[category]
                    ],
                }
                ok, errors = validate_catalog_data(new_catalog)
                if ok:
                    storage.save_catalog(new_catalog)
                    flash(f"Renamed '{old_value}' to '{value}' in {category}.", "success")
                    return redirect(url_for("catalog_view"))

    return render_template("catalog.html", catalog=catalog, errors=errors)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
