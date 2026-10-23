from actions import (
    create_product_action,
    delete_product_action,
    get_product_action,
    list_products_action,
    update_product_action,
    add_inventory_batch_action,
    show_inventory_summary,
    list_inventory_batches_action,
    update_inventory_batch_action,
    delete_inventory_batch_action
)


def cli():
    while True:
        print("\n1. Create product")
        print("2. Get product by ID or name")
        print("3. Get all products")
        print("4. Delete a product")
        print("5. Update product details")
        print("6. Add inventory batch")
        print("7. Show inventory summary")
        print("8. List inventory batches")
        print("9. Update inventory batch")
        print("10. Delete inventory batch")
        print("11. Exit")

        choice = input("Select your preference: ")

        if choice == "1":
            create_product_action()
        elif choice == "2":
            get_product_action()
        elif choice == "3":
            list_products_action()
        elif choice == "4":
            delete_product_action()
        elif choice == "5":
            update_product_action()
        elif choice == "6":
            add_inventory_batch_action()
        elif choice == "7":
            show_inventory_summary()
        elif choice == "8":
            list_inventory_batches_action()
        elif choice == "9":
            update_inventory_batch_action()
        elif choice == "10":
            delete_inventory_batch_action()
        elif choice == "11":
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    cli()