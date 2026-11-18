
from textx import metamodel_from_file
from validator import validate_order
from validate_catalog import validate_catalog, validate_catalog_count

# Load grammar and parse the program
pizzeria_mm = metamodel_from_file("pizzeria.tx")
model = pizzeria_mm.model_from_file("example.pizza")

print("Program parsed successfully!\n")

# Find the catalog
catalog = next(
    d for d in model.declarations
    if d.__class__.__name__ == "CatalogDecl"
)

catalog_errors = validate_catalog_count(model)

catalogs = [
    d for d in model.declarations
    if d.__class__.__name__ == "CatalogDecl"
]

if catalogs:
    catalog_errors.extend(validate_catalog(catalogs[0]))

if catalog_errors:
    print("CATALOG VALIDATION FAILED:")

    for error in catalog_errors:
        print("-", error)
else:
    print("Catalog validation successful!")

# Process orders
for declaration in model.declarations:

    if declaration.__class__.__name__ == "OrderDecl":

        # Validate the order only once
        if catalog_errors:
            print("Order validation skipped: catalog is invalid.")

        else:
            errors = validate_order(declaration, catalog)

            if errors:
                print("ORDER VALIDATION FAILED:")
                for error in errors:
                    print("-", error)
            else:
                print("Order validation successful!")

        # Display customer information
        print("Customer:", declaration.customer)
        print("Contact:", declaration.contact)
        print("Status:", declaration.status)

        # Display order items
        for item in declaration.items:

            if item.__class__.__name__ == "PizzaItem":
                print("\nPizza")
                print("Quantity:", item.quantity)
                print("Crust:", item.crust)
                print("Sauce:", item.sauce)
                print("Cheese:", item.cheese)

                if item.toppings:
                    print("Toppings:", item.toppings.toppings)

            elif item.__class__.__name__ == "DrinkItem":
                print("\nDrink")
                print("Quantity:", item.quantity)
                print("Name:", item.drink)
