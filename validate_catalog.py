
def validate_catalog(catalog):

    errors = []

    categories = {
        "crusts": catalog.crusts,
        "sauces": catalog.sauces,
        "cheeses": catalog.cheeses,
        "toppings": catalog.toppings,
        "drinks": catalog.drinks
    }

    for category, names in categories.items():

        if len(names) != len(set(names)):
            errors.append(
                f"Duplicate name found in catalog category: {category}"
            )

    return errors


def validate_catalog_count(model):

    catalogs = [
        d for d in model.declarations
        if d.__class__.__name__ == "CatalogDecl"
    ]

    errors = []

    if len(catalogs) > 1:
        errors.append("Only one catalog block is allowed.")

    return errors
