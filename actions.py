from app.services import product_service


def display_product(product):
    print(
        f"ID: {product.id} | Name: {product.name} | "
        f"Price: {product.price} | Quantity: {product.quantity} | "
        f"SKU: {product.sku}"
    )

def create_product_action():
    while True:
        try:
            product_id = int(input("\nEnter the product ID: "))
            break
        except ValueError:
            print("Invalid input. PLease enter digit/digits")
    if product_service.get_product(product_id):
        print(f"Product with ID :-{product_id} already exists.")
        return

    name = input("Enter the product name: ")

    try:
        price = float(input("Enter price: "))
        quantity = int(input("Enter quantity: "))
    except ValueError:
        print("Price and quantity must be a whole number.")
        return

    sku = input("Enter the SKU: ")

    try:
        product_service.create_product(product_id, name, price, quantity, sku)
        print("Product created successfully.")
    except ValueError as error:
        print(error)


def get_product_action():
    search_by = input("Search by (1) ID or (2) name? ")

    if search_by == "1":
        product_id = int(input("Enter the product ID: "))
        product = product_service.get_product(product_id)

        if product:
            display_product(product)
        else:
            print("Product not found.")

    elif search_by == "2":
        name = input("Which product do you want to find? ")
        matching_products = product_service.get_products_by_name(name)

        if matching_products:
            for product in matching_products:
                display_product(product)
        else:
            print("Product not found.")

    else:
        print("Invalid choice.")


def list_products_action():
    products = product_service.get_all_products()

    if products:
        for product in products:
            display_product(product)
    else:
        print("No products found.")


def delete_product_action():
    delete_by = input("Delete by (1) ID or (2) name? ")

    if delete_by == "1":
        product_id = int(input("Enter the product ID: "))
        deleted = product_service.delete_product(product_id)

        if deleted:
            print("Product deleted successfully.")
        else:
            print("Product not found.")

    elif delete_by == "2":
        name = input("Which product do you want to delete? ")
        matching_products = product_service.get_products_by_name(name)

        if not matching_products:
            print("Product not found.")
            return

        for product in matching_products:
            display_product(product)

        product_id = int(input("Enter the ID you want to delete: "))

        if any(product.id == product_id for product in matching_products):
            deleted = product_service.delete_product(product_id)

            if deleted:
                print("Product deleted successfully.")
        else:
            print("That ID is not one of the matching products.")

    else:
        print("Invalid choice.")


def update_product_action():
    update_by = input("Update by (1) ID or (2) name? ")
    product_id = None

    if update_by == "1":
        product_id = int(input("Enter the product ID: "))

    elif update_by == "2":
        name = input("Which product do you want to update? ")
        matching_products = product_service.get_products_by_name(name)

        if not matching_products:
            print("Product not found.")
            return

        for product in matching_products:
            display_product(product)

        selected_id = int(input("Enter the ID you want to update: "))

        if any(product.id == selected_id for product in matching_products):
            product_id = selected_id
        else:
            print("That ID is not one of the matching products.")
            return

    else:
        print("Invalid choice.")
        return

    product = product_service.get_product(product_id)

    if product is None:
        print("Product not found.")
        return

    updates = {}

    while True:
        print("\nWhat details do you want to update?")
        print("1. name")
        print("2. price")
        print("3. quantity")
        print("4. SKU")
        print("5. Done")

        update_choice = input("Select: ")

        if update_choice == "1":
            updates["name"] = input("Enter the updated name: ")

        elif update_choice == "2":
            try:
                updates["price"] = float(input("Enter the updated price: "))
            except ValueError:
                print("Price must be a number.")

        elif update_choice == "3":
            try:
                updates["quantity"] = int(input("Enter the updated quantity: "))
            except ValueError:
                print("Quantity must be a whole number.")

        elif update_choice == "4":
            updates["sku"] = input("Enter the updated SKU: ")

        elif update_choice == "5":
            break

        else:
            print("Invalid input.")

    if not updates:
        print("No updates were made.")
        return

    updated_product = product_service.update_product(product_id, updates)

    if updated_product is not None:
        print("Product updated successfully.")
        display_product(updated_product)
    else:
        print("Product not found.")