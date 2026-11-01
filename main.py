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
    delete_inventory_batch_action,
    login_or_signup_action,
    show_wallet_balance_action,
    deposit_to_wallet_action,
    buy_product_action,
    show_order_history_action,
    show_wallet_transactions_action
)


def cli():
    current_user = None

    while True:
        if current_user is None:
            print("\n1. Customer login / sign up")
            print("2. Exit")
            choice = input("Select your preference: ").strip()

            if choice == "1":
                current_user = login_or_signup_action()

                if current_user is not None and current_user.role == "customer":
                    show_wallet_balance_action(current_user.id)

            elif choice == "2":
                break
            else:
                print("Invalid choice.")

            continue

        if current_user.role == "admin":
            print("\n--- Administrator Menu ---")
            print("1. Create product")
            print("2. Get product by ID or name")
            print("3. Get all products")
            print("4. Delete a product")
            print("5. Update product details")
            print("6. Add inventory batch")
            print("7. Show inventory summary")
            print("8. List inventory batches")
            print("9. Update inventory batch")
            print("10. Delete inventory batch")
            print("11. Log out")
            print("12. Exit")

            choice = input("Select your preference: ").strip()

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
                current_user = None
                print("Logged out.")
            elif choice == "12":
                break
            else:
                print("Invalid choice.")

        else:
            print("\n--- Customer Menu ---")
            print("1. Check wallet balance")
            print("2. Top up wallet")
            print("3. Buy product")
            print("4. View order history")
            print("5. View wallet transaction history")
            print("6. Log out")
            print("7. Exit")

            choice = input("Select your preference: ").strip()

            if choice == "1":
                show_wallet_balance_action(current_user.id)
            elif choice == "2":
                deposit_to_wallet_action(current_user.id)
            elif choice == "3":
                buy_product_action(current_user.id)
            elif choice=="4":
                show_order_history_action(current_user.id)
            elif choice == "5":
                show_wallet_transactions_action(current_user.id)
            elif choice == "6":
                current_user = None
                print("Logged out.")
            elif choice == "7":
                break
            else:
                print("Invalid choice.")

if __name__ == "__main__":
    cli()