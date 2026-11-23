"""
Plain JSON persistence for the IDE. No database — just two files under
data/, as the team decided (fully local, simple).
"""

import json
import os
import threading

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CATALOG_PATH = os.path.join(DATA_DIR, "catalog.json")
ORDERS_PATH = os.path.join(DATA_DIR, "orders.json")

_lock = threading.Lock()

STATUS_FLOW = ["pending", "processing", "ready", "completed"]


def load_catalog() -> dict:
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_catalog(catalog: dict) -> None:
    with _lock:
        with open(CATALOG_PATH, "w", encoding="utf-8") as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)


def _load_orders_raw() -> dict:
    with open(ORDERS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_orders_raw(data: dict) -> None:
    with open(ORDERS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_orders() -> list:
    return _load_orders_raw()["orders"]


def get_order(order_id: int):
    for o in load_orders():
        if o["id"] == order_id:
            return o
    return None


def create_order(order: dict) -> dict:
    with _lock:
        data = _load_orders_raw()
        order = dict(order)
        order["id"] = data["next_id"]
        data["next_id"] += 1
        data["orders"].append(order)
        _save_orders_raw(data)
        return order


def update_order(order: dict) -> None:
    with _lock:
        data = _load_orders_raw()
        for i, o in enumerate(data["orders"]):
            if o["id"] == order["id"]:
                data["orders"][i] = order
                break
        _save_orders_raw(data)


def set_status(order_id: int, new_status: str) -> None:
    with _lock:
        data = _load_orders_raw()
        for o in data["orders"]:
            if o["id"] == order_id:
                o["status"] = new_status
                break
        _save_orders_raw(data)
