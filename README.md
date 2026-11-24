# John Papa's Pizzeria DSL - local IDE

A small local web app that uses your own `pizzeria.tx` grammar and your
own `validator.py` / `validate_catalog.py` to enforce every business rule
whenever an order or the catalog changes. No database, no internet
connection needed: everything is saved as JSON under `data/`.

## Run it

```bash
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000 in your browser.

## What's in each file

- `pizzeria.tx`, `validator.py`, `validate_catalog.py` - your grammar and
  validators, unchanged.
- `dsl_builder.py` - takes the JSON an order/catalog is stored as, renders
  it back into real Pizzeria DSL text, parses it with textX, and runs it
  through your validators. If it fails, nothing gets saved.
- `storage.py` - reads/writes `data/orders.json` and `data/catalog.json`.
- `app.py` - the Flask routes (the three screens below).
- `templates/`, `static/style.css` - the pages themselves.

## The three screens

- **Orders** (`/`) - shared by the receptionist and kitchen staff, as we
  defined in the Rules and Grammar document:
  - Receptionist: "New order", "Edit" and "Cancel" (edit/cancel only work
    while the order is still `pending`).
  - Kitchen staff: "Advance" moves an order one step forward through
    `pending -> processing -> ready -> completed`. There's no way to go
    backwards or skip a step.
- **Catalog** (`/catalog`) - the Domain Expert screen. This is the only
  place where crusts, sauces, cheeses, toppings and drinks can be
  added or removed (CRUD on terminal symbols). Every add/remove is
  re-validated (duplicate names, etc.) before it's saved.
  **Protected by Domain Expert Login**:
  - Allowed users: `Luis`, `Manu`, `Thelma`
  - Password: `pizz@321!`

## Notes / things you may want to add later

- **Authentication**: Access to the Domain Expert screen (`/catalog`) requires logging in with one of the team member credentials above. The Orders screen remains shared between receptionist and kitchen staff.
- Removing a catalog item doesn't currently re-check existing orders that
  already used it. For a class project this is an acceptable edge case to
  mention in your write-up rather than solve in code.
- `app.run(debug=True)` is fine for local demos; turn `debug` off if you
  ever deploy this anywhere other than your own machine.
