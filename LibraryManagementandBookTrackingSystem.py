# ================================================================
#                 LIBRARY MANAGEMENT SYSTEM
#       Book Inventory | Borrowing | Returns | Date Tracking
# ================================================================

from datetime import datetime

# ANSI colors (most modern terminals support these)
RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"

# Data structures
# books: [book_id, title, author, total_quantity, available_quantity]
# members: [member_id, name]
# borrow_records: [book_id, member_id, borrow_quantity, date_borrowed,
#                 most_recent_date_returned, quantity_returned]
books = []
members = []
borrow_records = []


def heading(title):
    width = 76
    print(f"\n{CYAN}{BOLD}{'=' * width}{RESET}")
    print(f"{CYAN}{BOLD}{title.center(width)}{RESET}")
    print(f"{CYAN}{BOLD}{'=' * width}{RESET}")


def get_integer(prompt, minimum=1):
    while True:
        try:
            value = int(input(f"{YELLOW}{prompt}{RESET}"))
            if value < minimum:
                print(f"{RED}[ERROR] Enter a whole number of at least {minimum}.{RESET}")
                continue
            return value
        except ValueError:
            print(f"{RED}[ERROR] Please enter a valid whole number.{RESET}")


def current_datetime():
    """Return the computer's current local date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_date(prompt):   
    """Accept a manually entered date in YYYY-MM-DD format (kept as a helper)."""
    while True:
        value = input(f"{YELLOW}{prompt}{RESET}").strip()
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            print(f"{RED}[ERROR] Use YYYY-MM-DD, for example 2026-10-12.{RESET}")


def find_book(book_id):
    for book in books:
        if book[0] == book_id:
            return book
    return None


def print_table(headers, rows, widths):
    """Print a readable text table with aligned columns."""
    line = "+" + "+".join("-" * (width + 2) for width in widths) + "+"
    print(BLUE + line + RESET)
    print(BLUE + "|" + "|".join(f" {str(header)[:width]:<{width}} " for header, width in zip(headers, widths)) + "|" + RESET)
    print(BLUE + line + RESET)
    if not rows:
        print("|" + "|".join(f" {'No records':<{width}} " if i == 0 else f" {'':<{width}} " for i, width in enumerate(widths)) + "|")
    else:
        for row in rows:
            cells = []
            for value, width in zip(row, widths):
                text = str(value)
                if len(text) > width:
                    text = text[:width - 3] + "..."
                cells.append(f" {text:<{width}} ")
            print("|" + "|".join(cells) + "|")
    print(BLUE + line + RESET)


def register_book(book_id, title, author, quantity):
    if find_book(book_id):
        print(f"{RED}[ERROR] Book ID {book_id} already exists.{RESET}")
        return
    books.append([book_id, title, author, quantity, quantity])
    print(f"{GREEN}[SUCCESS] '{title}' added with {quantity} copies.{RESET}")


def register_member(member_id, name):
    if any(member[0] == member_id for member in members):
        print(f"{RED}[ERROR] Member ID {member_id} already exists.{RESET}")
        return
    members.append([member_id, name])
    print(f"{GREEN}[SUCCESS] Member '{name}' registered.{RESET}")


def borrow_book(book_id, member_id, quantity, date_borrowed):
    if not any(member[0] == member_id for member in members):
        print(f"{RED}[ERROR] Member ID {member_id} is not registered.{RESET}")
        return
    book = find_book(book_id)
    if book is None:
        print(f"{RED}[ERROR] Book ID {book_id} was not found.{RESET}")
        return
    if quantity > book[4]:
        print(f"{RED}[ERROR] Only {book[4]} copy/copies are available.{RESET}")
        return

    book[4] -= quantity
    borrow_records.append([book_id, member_id, quantity, date_borrowed, None, 0])
    print(f"{GREEN}[SUCCESS] Borrowed {quantity} copy/copies of '{book[1]}'.{RESET}")
    print(f"Borrowed on: {date_borrowed}")
    print(f"\n{MAGENTA}{BOLD}UPDATED BOOK AVAILABILITY{RESET}")
    print_table(
        ["BOOK ID", "BOOK TITLE", "AUTHOR", "TOTAL QTY", "AVAILABLE QTY", "STATUS"],
        [[book[0], book[1], book[2], book[3], book[4],
          "AVAILABLE" if book[4] > 0 else "OUT OF STOCK"]],
        [8, 22, 20, 10, 13, 14],
    )


def return_book(book_id, member_id, quantity_to_return, date_returned):
    book = find_book(book_id)
    if book is None:
        print(f"{RED}[ERROR] Book ID {book_id} was not found.{RESET}")
        return

    # Search for an outstanding borrowing record. Partial returns are supported.
    for record in borrow_records:
        if record[0] == book_id and record[1] == member_id:
            outstanding = record[2] - record[5]
            if outstanding <= 0:
                continue
            if quantity_to_return > outstanding:
                print(f"{RED}[ERROR] Only {outstanding} copy/copies remain to be returned on this record.{RESET}")
                return
            if date_returned < record[3]:
                print(f"{RED}[ERROR] Return date cannot be earlier than borrow date.{RESET}")
                return

            record[5] += quantity_to_return
            record[4] = date_returned
            book[4] += quantity_to_return
            print(f"{GREEN}[SUCCESS] Returned {quantity_to_return} copy/copies of '{book[1]}'.{RESET}")
            print(f"Date Borrowed: {record[3]} | Date Returned: {record[4]}")
            print(f"Available copies now: {book[4]}")
            remaining = record[2] - record[5]
            if remaining:
                print(f"{YELLOW}[NOTICE] {remaining} copy/copies still outstanding.{RESET}")
            else:
                print(f"{GREEN}[STATUS] All copies from this borrowing record have been returned.{RESET}")
            return

    print(f"{RED}[ERROR] No outstanding borrowing record found for this book and member.{RESET}")


def library_report():
    heading("LIBRARY REPORT - INVENTORY AND TRANSACTION HISTORY")
    print(f"\n{MAGENTA}{BOLD}BOOK INVENTORY{RESET}")
    inventory_rows = []
    for book in books:
        borrowed = book[3] - book[4]
        status = "AVAILABLE" if book[4] > 0 else "OUT OF STOCK"
        inventory_rows.append([book[0], book[1], book[2], book[3], book[4], borrowed, status])
    print_table(
        ["BOOK ID", "BOOK TITLE", "AUTHOR", "TOTAL QTY", "AVAILABLE QTY", "BORROWED", "STATUS"],
        inventory_rows,
        [8, 20, 18, 9, 13, 8, 12],
    )

    print(f"\n{MAGENTA}{BOLD}BORROW / RETURN HISTORY{RESET}")
    history_rows = []
    for record in borrow_records:
        outstanding = record[2] - record[5]
        returned_qty = record[5]
        returned_date = record[4] if record[4] else "Not yet returned"
        history_rows.append([record[0], record[1], record[2], record[3], returned_date, returned_qty, outstanding])
    print_table(
        ["BOOK ID", "MEMBER ID", "BORROW QTY", "DATE BORROWED", "DATE RETURNED", "RETURNED QTY", "OUTSTANDING"],
        history_rows,
        [8, 9, 10, 19, 19, 12, 11],
    )


def book_availability():
    heading("AVAILABLE BOOKS - QUANTITY TABLE")
    rows = []
    for book in books:
        status = "AVAILABLE" if book[4] > 0 else "OUT OF STOCK"
        rows.append([book[0], book[1], book[2], book[3], book[4], status])
    print_table(
        ["BOOK ID", "BOOK TITLE", "AUTHOR", "TOTAL QTY", "AVAILABLE QTY", "STATUS"],
        rows,
        [8, 22, 20, 10, 13, 14],
    )
    total = sum(book[3] for book in books)
    available = sum(book[4] for book in books)
    print(f"\n{BOLD}Total copies: {total}   Available copies: {available}   Borrowed copies: {total - available}{RESET}")


def main():
    while True:
        heading("LIBRARY MANAGEMENT SYSTEM")
        print(f" {GREEN}[1]{RESET} Register Book")
        print(f" {GREEN}[2]{RESET} Register Member")
        print(f" {GREEN}[3]{RESET} Borrow Book")
        print(f" {GREEN}[4]{RESET} Return Book")
        print(f" {GREEN}[5]{RESET} View Library Report")
        print(f" {GREEN}[6]{RESET} View Available Books Table")
        print(f" {RED}[7]{RESET} Exit System")
        print(f"{CYAN}{'=' * 76}{RESET}")
        choice = input(f"{YELLOW}Select an option (1-7): {RESET}").strip()

        if choice == "1":
            book_id = get_integer("Enter Book ID: ")
            if find_book(book_id) is not None:
                print(f"{RED}[ERROR] Book ID {book_id} already registered.{RESET}")
                continue
            title = input("Enter Book Title: ").strip()
            author = input("Enter Author: ").strip()
            if not title or not author:
                print(f"{RED}[ERROR] Book title and author cannot be empty.{RESET}")
                continue
            quantity = get_integer("Enter Total Book Quantity: ")
            register_book(book_id, title, author, quantity)
        elif choice == "2":
            member_id = get_integer("Enter Member ID: ")
            if any(member[0] == member_id for member in members):
                print(f"{RED}[ERROR] Member ID {member_id} already registered.{RESET}")
                continue
            name = input("Enter Member Name: ").strip()
            if not name:
                print(f"{RED}[ERROR] Member name cannot be empty.{RESET}")
                continue
            register_member(member_id, name)
        elif choice == "3":
            book_id = get_integer("Enter Book ID: ")
            member_id = get_integer("Enter Member ID: ")
            quantity = get_integer("Enter Quantity to Borrow: ")
            date_borrowed = current_datetime()
            borrow_book(book_id, member_id, quantity, date_borrowed)
        elif choice == "4":
            book_id = get_integer("Enter Book ID: ")
            member_id = get_integer("Enter Member ID: ")
            quantity = get_integer("Enter Quantity to Return: ")
            date_returned = current_datetime()
            return_book(book_id, member_id, quantity, date_returned)
        elif choice == "5":
            library_report()
        elif choice == "6":
            book_availability()
        elif choice == "7":
            print(f"\n{GREEN}{BOLD}Thank you for using the Library Management System!{RESET}")
            break
        else:
            print(f"{RED}[ERROR] Invalid option. Please select 1-7.{RESET}")


if __name__ == "__main__":
    main()