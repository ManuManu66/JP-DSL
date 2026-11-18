
def validate_order(order, catalog):

    errors = []
    if not order.customer.strip():
        errors.append("Customer name cannot be empty.")

    if not order.contact.strip():
        errors.append("Customer contact cannot be empty.")

    pizza_count = 0
    drink_count = 0

    for item in order.items:

        # Validate pizza
        if item.__class__.__name__ == "PizzaItem":

            if item.quantity <= 0:
                errors.append("Pizza quantity must be greater than zero.")

            pizza_count += item.quantity

            # Validate catalog ingredients
            if item.crust not in catalog.crusts:
                errors.append(f"Invalid crust: {item.crust}")

            if item.sauce not in catalog.sauces:
                errors.append(f"Invalid sauce: {item.sauce}")

            if item.cheese not in catalog.cheeses:
                errors.append(f"Invalid cheese: {item.cheese}")

            # Validate toppings
            if item.toppings:

                toppings = item.toppings.toppings

                if len(toppings) > 5:
                    errors.append("A pizza cannot have more than 5 toppings.")

                if len(toppings) != len(set(toppings)):
                    errors.append("Repeated topping detected.")

                for topping in toppings:
                    if topping not in catalog.toppings:
                        errors.append(f"Invalid topping: {topping}")

        # Validate drinks
        elif item.__class__.__name__ == "DrinkItem":

            if item.quantity <= 0:
                errors.append("Drink quantity must be greater than zero.")

            drink_count += item.quantity

            if item.drink not in catalog.drinks:
                errors.append(f"Invalid drink: {item.drink}")

    # Validate order limits
    if pizza_count > 5:
        errors.append("An order cannot contain more than 5 pizzas.")

    if drink_count > 10:
        errors.append("An order cannot contain more than 10 drinks.")

    return errors
