from app.services import product_service

def display_product(product):
    print(
        f"ID: {product.id} | Name: {product.name} | "
        f"Price: {product.price} | Quantity: {product.quantity} | "
        f"SKU: {product.sku}"
    )
while True:
    print("1. create product ")
    print("2. get product by ID or Name ")
    print("3. get all product ")
    print("4. delete a product ")
    print("5. update product's detail")
    print("6. exit")
    choice=input("select your preference")

    if choice=="1":
        product_id = int(input("\nEnter the product id "))
        name=input("\nEnter the name of the product ")
        price=float(input(f"\nEnter the price of the {name} "))
        quantity=int(input(f"\nEnter the quantity of {name} "))
        sku=input("\nEnter the sku ")
        product_service.create_product(product_id, name, price, quantity, sku)
        print("Product created successfully")

    elif choice == "2":
        search_by = input("Search by (1) ID or (2) name? ")

        if search_by == "1":
            product_id = int(input("Enter the product ID: "))
            product = product_service.get_product(product_id)

            if product:
                display_product(product)
            else:
                print("Product not found")

        elif search_by == "2":
            name = input("Which product do you want to find? ")
            matching_products = product_service.get_products_by_name(name)

            if matching_products:
                for product in matching_products:
                    display_product(product)
            else:
                print("Product not found")

        else:
            print("Invalid choice")

    elif choice=="3":
        products=product_service.get_all_products()
        if products:
            for product in products:
                display_product(product)
        else:
            print("No products found")
    elif choice == "4":
        delete_by = input("Delete by (1) ID or (2) name? ")

        if delete_by == "1":
            product_id = int(input("Enter the product ID: "))
            deleted = product_service.delete_product(product_id)

            if deleted:
                print("Product deleted successfully")
            else:
                print("Product not found")

        elif delete_by == "2":
            name = input("Which product do you want to delete? ")
            matching_products = product_service.get_products_by_name(name)

            if not matching_products:
                print("Product not found")
            else:
                for product in matching_products:
                    display_product(product)

                product_id = int(input("Enter the ID you want to delete: "))

                if any(product.id == product_id for product in matching_products):
                    deleted = product_service.delete_product(product_id)
                    if deleted:
                        print("Product deleted successfully")
                else:
                    print("That ID is not one of the matching products")

        else:
            print("Invalid choice")
    elif choice == "5":
        update_by = input("Update by (1) ID or (2) name? ")
        product_id = None

        if update_by == "1":
            product_id = int(input("Enter the product ID: "))

        elif update_by == "2":
            name = input("Which product do you want to update? ")
            matching_products = product_service.get_products_by_name(name)

            if matching_products:
                for product in matching_products:
                    display_product(product)

                selected_id = int(input("Enter the ID you want to update: "))

                if any(product.id == selected_id for product in matching_products):
                    product_id = selected_id
                else:
                    print("That ID is not one of the matching products")
            else:
                print("Product not found")

        else:
            print("Invalid choice")

        if product_id is not None:
            product = product_service.get_product(product_id)

            if product is None:
                print("Product not found")
            else:
                updates = {}

                while True:
                    print("\nWhat details do you want to update?")
                    print("1. name")
                    print("2. price")
                    print("3. quantity")
                    print("4. sku")
                    print("5. Done")

                    update_choice = input("Select: ")

                    if update_choice == "1":
                        updates["name"] = input("Enter the updated name: ")
                    elif update_choice == "2":
                        updates["price"] = float(input("Enter the updated price: "))
                    elif update_choice == "3":
                        updates["quantity"] = int(input("Enter the updated quantity: "))
                    elif update_choice == "4":
                        updates["sku"] = input("Enter the updated SKU: ")
                    elif update_choice == "5":
                        break
                    else:
                        print("Invalid input")

                if updates:
                    updated_product = product_service.update_product(product_id, updates)

                    if updated_product is not None:
                        print("Product updated successfully")
                        display_product(updated_product)
                    else:
                        print("Product not found")
                else:
                    print("No updates were made")