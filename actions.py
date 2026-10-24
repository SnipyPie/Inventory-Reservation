from app.services import product_service
from decimal import Decimal, InvalidOperation
from app.services import inventory_service, product_service
from datetime import date
from app.services.inventory_service import get_inventory_summary_by_name
from getpass import getpass
from app.services import user_service
from app.services import wallet_service

def show_wallet_balance_action(user_id: int):
    balance = wallet_service.get_wallet_balance(user_id)

    if balance is None:
        print("No wallet was found for this user.")
        return

    print(f"Your wallet balance is: {balance:.2f}")

def deposit_to_wallet_action(user_id: int):
    amount_text = input("Enter the deposit amount: ").strip()

    try:
        amount = Decimal(amount_text)
    except InvalidOperation:
        print("Please enter a valid number.")
        return

    try:
        new_balance = wallet_service.deposit_to_wallet(user_id, amount)
    except ValueError as error:
        print(error)
        return

    print(f"Deposit recorded. New balance: {new_balance:.2f}")
    
def signup_user_action():
    email = input("Enter your email: ").strip()
    password = getpass("Create a password: ")
    confirm_password = getpass("Confirm your password: ")

    if password != confirm_password:
        print("The passwords do not match.")
        return

    try:
        user = user_service.register_user(email, password)
    except ValueError as error:
        print(error)
        return None

    print(f"Account created. Your user ID is {user.id}.")
    print("Please log in before buying.")
    return user

def login_or_signup_action():
    while True:
        email = input("Enter your email: ").strip()
        password = getpass("Enter your password: ")

        try:
            user, status = user_service.authenticate_user(email, password)
        except ValueError as error:
            print(error)
            continue

        if status == "not_found":
            print("No account found for that email. Please sign up.")
            new_user = signup_user_action()

            if new_user is None:
                return None

            print("Now log in with your new account.")
            continue

        if status == "wrong_password":
            print("Incorrect password. Try again.")
            continue

        if status == "invalid_hash":
            print("Could not verify the saved password for this account.")
            return None

        print(f"Login successful. Welcome, {user.email}.")
        return user

def show_inventory_summary():
    name = input("Enter a product name to search: ").strip()
    '''
    Fetches the Product from the Inventory and displays all its skus and '''
    rows = get_inventory_summary_by_name(name)

    if not rows:
        print("No matching products found.")
        return

    for row in rows:
        print(
             f"ID: {row['product_id']} | Name: {row['name']} | "
            f"SKU: {row['sku']} | "
            f"Available: {row['available_quantity']} | "
            f"Expired: {row['expired_quantity']} | "
            f"Total: {row['total_quantity']} | "            
            f"Batches: {row['batch_count']}"
        )

def list_inventory_batches_action():
    name = input("Enter a product name to find its batches: ").strip()

    try:
        rows = inventory_service.get_inventory_batches_by_name(name)
    except ValueError as error:
        print(error)
        return

    if not rows:
        print("No inventory batches found for that product.")
        return

    for batch, product_name, sku in rows:
        print(
            f"Batch ID: {batch.id} | Product: {product_name} | "
            f"SKU: {sku} | Received: {batch.quantity_received} | "
            f"Remaining: {batch.quantity_remaining} | "
            f"Stocked: {batch.stock_in_date} | "
            f"Expires: {batch.expiry_date}"
        )

def add_inventory_batch_action():
    try:
        product_id = int(input("Enter the product ID: "))
    except ValueError:
        print("Product ID must be a whole number.")
        return

    product = product_service.get_product(product_id)

    if product is None:
        print("Product not found.")
        return

    try:
        quantity = int(input("Enter the batch quantity: "))
    except ValueError:
        print("Quantity must be a whole number.")
        return

    stock_in_text = input(
        "Enter stock-in date as YYYY-MM-DD, or press Enter for today: "
    ).strip()

    if stock_in_text:
        try:
            stock_in_date = date.fromisoformat(stock_in_text)
        except ValueError:
            print("Enter the date in YYYY-MM-DD format.")
            return
    else:
        stock_in_date = None

    try:
        batch = inventory_service.add_inventory_batch(
            product_id=product_id,
            quantity=quantity,
            stock_in_date=stock_in_date,
        )
    except ValueError as error:
        print(error)
        return

    if batch is None:
        print("Product not found.")
        return

    print(
        f"Batch {batch.id} added for {product.name}. "
        f"It expires on {batch.expiry_date}."
    )

def update_inventory_batch_action():
    name = input("Enter a product name to find its batches: ").strip()

    try:
        rows = inventory_service.get_inventory_batches_by_name(name)
    except ValueError as error:
        print(error)
        return

    if not rows:
        print("No inventory batches found for that product.")
        return

    for batch, product_name, sku in rows:
        print(
            f"Batch ID: {batch.id} | Product: {product_name} | "
            f"SKU: {sku} | Received: {batch.quantity_received} | "
            f"Remaining: {batch.quantity_remaining} | "
            f"Stocked: {batch.stock_in_date} | "
            f"Expires: {batch.expiry_date}"
        )

    try:
        batch_id = int(input("Enter the batch ID to update: "))
    except ValueError:
        print("Batch ID must be a whole number.")
        return

    if not any(batch.id == batch_id for batch, _, _ in rows):
        print("That batch ID is not in the results above.")
        return

    quantity_text = input(
        "Enter the new quantity, or press Enter to keep it: "
    ).strip()

    if quantity_text:
        try:
            quantity = int(quantity_text)
        except ValueError:
            print("Quantity must be a whole number.")
            return
    else:
        quantity = None

    date_text = input(
        "Enter the new stock-in date as YYYY-MM-DD, "
        "or press Enter to keep it: "
    ).strip()

    if date_text:
        try:
            stock_in_date = date.fromisoformat(date_text)
        except ValueError:
            print("Enter the date in YYYY-MM-DD format.")
            return
    else:
        stock_in_date = None

    try:
        batch = inventory_service.update_inventory_batch(
            batch_id=batch_id,
            quantity=quantity,
            stock_in_date=stock_in_date,
        )
    except ValueError as error:
        print(error)
        return

    if batch is None:
        print("Batch not found.")
        return

    print(
        f"Batch {batch.id} updated. Remaining: {batch.quantity_remaining} | "
        f"Stocked: {batch.stock_in_date} | Expires: {batch.expiry_date}"
    )

def delete_inventory_batch_action():
    name = input("Enter a product name to find its batches: ").strip()

    try:
        rows = inventory_service.get_inventory_batches_by_name(name)
    except ValueError as error:
        print(error)
        return

    if not rows:
        print("No inventory batches found for that product.")
        return

    for batch, product_name, sku in rows:
        print(
            f"Batch ID: {batch.id} | Product: {product_name} | "
            f"SKU: {sku} | Received: {batch.quantity_received} | "
            f"Remaining: {batch.quantity_remaining} | "
            f"Stocked: {batch.stock_in_date} | "
            f"Expires: {batch.expiry_date}"
        )

    try:
        batch_id = int(input("Enter the batch ID to delete: "))
    except ValueError:
        print("Batch ID must be a whole number.")
        return

    if not any(batch.id == batch_id for batch, _, _ in rows):
        print("That batch ID is not in the results above.")
        return

    confirmation = input(
        f"Delete batch {batch_id}? Enter y to confirm: "
    ).strip().lower()

    if confirmation != "y":
        print("Deletion cancelled.")
        return

    deleted = inventory_service.delete_inventory_batch(batch_id)

    if deleted:
        print(f"Batch {batch_id} deleted.")
    else:
        print("Batch not found.")

def display_product(product):
    print(
        f"ID: {product.id} | Name: {product.name} | "
        f"Price: {product.price} | SKU: {product.sku} | "
        f"Shelf life: {product.shelf_life_days} days"
    )

def report_product_delete_result(result):
    if result == "deleted":
        print("Product deleted successfully.")
    elif result == "has_batches":
        print(
            "Cannot delete this product because it has inventory batches. "
            "Delete its batches first."
        )
    else:
        print("Product not found.")

def create_product_action():
    name = input("Enter the product name: ")
    sku = input("Enter the SKU: ")

    try:
        price = Decimal(input("Enter price: "))
    except InvalidOperation:
        print("Price must be a number.")
        return

    if price < 0:
        print("Price cannot be negative.")
        return

    try:
        shelf_life_days = int(input("Enter shelf life in days: "))
    except ValueError:
        print("Shelf life must be a whole number.")
        return

    try:
        product = product_service.create_product(
            name=name,
            sku=sku,
            price=price,
            shelf_life_days=shelf_life_days,
        )
        print(f"Product created successfully. Its ID is {product.id}.")
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
        try:
            product_id = int(input("Enter the product ID: "))
        except ValueError:
            print("Product ID must be a whole number.")
            return

        result = product_service.delete_product(product_id)
        report_product_delete_result(result)

    elif delete_by == "2":
        name = input("Which product do you want to delete? ")
        matching_products = product_service.get_products_by_name(name)

        if not matching_products:
            print("Product not found.")
            return

        for product in matching_products:
            display_product(product)

        try:
            product_id = int(input("Enter the ID you want to delete: "))
        except ValueError:
            print("Product ID must be a whole number.")
            return

        if any(product.id == product_id for product in matching_products):
            result = product_service.delete_product(product_id)
            report_product_delete_result(result)
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
    display_product(product)
    updates = {}

    while True:
        print("\nWhat details do you want to update?")
        print("1. name")
        print("2. price")
        print("3. SKU")
        print("4. Shelf life")
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
            updates["sku"] = input("Enter the updated SKU: ")

        elif update_choice == "4":
            try:
                updates["shelf_life_days"] = int(
                    input("Enter the updated shelf life in days: ")
                )
            except ValueError:
                print("Shelf life must be a whole number.")

        elif update_choice == "5":
            break
        else:
            print("Invalid input.")

    if not updates:
        print("No updates were made.")
        return

    try:
        updated_product = product_service.update_product(product_id, updates)
    except ValueError as error:
        print(error)
        return
    if updated_product is not None:
        print("Product updated successfully.")
        display_product(updated_product)
    else:
        print("Product not found.")