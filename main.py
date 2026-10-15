from app.services import product_service

while True:
    print("1. create product ")
    print("2. get product ")
    print("3. get all product ")
    print("4. delete a product ")
    print("5. update product's detail")
    print("6. exit")
    choice=input("select your preference")

    if choice=="1":
        name=input("\nEnter the name of the product ")
        price=float(input(f"\nEnter the price of the {name} "))
        quantity=int(input(f"\nEnter the quantity of {name} "))
        sku=input("\nEnter the sku ")
        product_service.create_product(name,price,quantity,sku)
        print("Product created successfully")

    elif choice=="2":
        name=input("Which Product do you want to see")
        product=product_service.get_product(name)
        if product:
            print(product)
        else:
            print("Product not found")

    elif choice=="3":
        product=product_service.get_all_products()
        if product:
            print(product)
        else:
            print("Product not found")

    elif choice=="4":
        name=input("Which product you want to delete? ")
        matching_products=product_service.get_products_by_name(name)
        if matching_products:
            for product in matching_products:
                print(product)
            product_id=input("Enter the product id you want to delte ")
            if any(product.id==product_id for product in matching_products):
                deleted=product_service.delete_product(product_id)
                if deleted:
                    print("Product delete successfully")
            else:
                print("Product Id not Found")
        else:
            print("Product Not Found")

    elif choice=="5":
        name=input("Which Product's details you want to update")
        matching_products=product_service.get_products_by_name(name)
        if matching_products:
            for product in matching_products:
                print(product)
            product_id=input("Enter the product id: ")
            if any(product.id==product_id for product in matching_products):
                updates={}
                while True:
                    print("\nWhat details do you want to update?")
                    print("1. name")
                    print("2. price")
                    print("3. quantity")
                    print("4. sku")
                    print("5. Done")

                    update_choice=input("Select: ")
                    if update_choice=="1":
                        updates["name"]=input(f"Enter the updated name of {name}:- ")
                    elif update_choice=="2":
                        updates["price"]=float(input(f"Enter the updated price of {name}:- "))
                    elif update_choice=="3":
                        updates["quantity"]=int(input(f"Enter the updated quantity of {name}:- "))
                    elif update_choice=="4":
                        updates["sku"]=input(f"Enter the updated sku of {name}:- ")
                    elif update_choice=="5":
                        break
                    else:
                        print("Invalid input")
                if updates:
                    product=product_service.update_product(product_id,updates)
                    if product is not None:
                        print("Product updated successfully")
                        print(product)
                    else:
                        print("Product not found")
                else:
                    print("No updates were made")
            else:
                print("Invalid product id for this product")
        else:
            print("Product not found")

    elif choice=="6":
        break

    else:
        print("Invalid choice")
    