import pickle
from datetime import datetime, timedelta

# ==================== Класи для даних ====================

class Field:
    def __init__(self, value):
        self.value = value

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone must be 10 digits")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone: str):
        self.phones.append(Phone(phone))

    def change_phone(self, old_phone: str, new_phone: str):
        for i, ph in enumerate(self.phones):
            if ph.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return True
        return False

    def add_birthday(self, birthday: str):
        self.birthday = Birthday(birthday)

    def days_to_birthday(self):
        if self.birthday:
            today = datetime.today().date()
            next_birthday = self.birthday.value.replace(year=today.year)
            if next_birthday < today:
                next_birthday = next_birthday.replace(year=today.year + 1)
            return (next_birthday - today).days
        return None

class AddressBook:
    def __init__(self):
        self.records = {}

    def add_record(self, record: Record):
        self.records[record.name.value] = record

    def find(self, name: str):
        return self.records.get(name)

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming = {}
        for record in self.records.values():
            days = record.days_to_birthday()
            if days is not None and 0 <= days <= 7:
                upcoming[record.name.value] = record.birthday.value
        return upcoming

# ==================== Функції для pickle ====================

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

# ==================== Декоратор для обробки помилок ====================

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, IndexError) as e:
            return f"Error: {str(e)}"
    return wrapper

# ==================== Функції команд ====================

@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_phone(args, book):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    if record.change_phone(old_phone, new_phone):
        return "Phone updated."
    return "Old phone not found."

@input_error
def show_phone(args, book):
    name, *_ = args
    record = book.find(name)
    if record:
        return ", ".join([ph.value for ph in record.phones]) if record.phones else "No phones."
    return "Contact not found."

def show_all(book):
    if not book.records:
        return "Address book is empty."
    result = []
    for rec in book.records.values():
        phones = ", ".join([ph.value for ph in rec.phones])
        birthday = rec.birthday.value.strftime("%d.%m.%Y") if rec.birthday else "No birthday"
        result.append(f"{rec.name.value}: Phones: {phones}, Birthday: {birthday}")
    return "\n".join(result)

@input_error
def add_birthday(args, book):
    name, birthday, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    record.add_birthday(birthday)
    return f"Birthday added for {name}."

@input_error
def show_birthday(args, book):
    name, *_ = args
    record = book.find(name)
    if record and record.birthday:
        return record.birthday.value.strftime("%d.%m.%Y")
    return "Birthday not set or contact not found."

def show_upcoming_birthdays(book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays next week."
    return "\n".join([f"{name}: {date.strftime('%d.%m.%Y')}" for name, date in upcoming.items()])

# ==================== Функція для парсингу вводу ====================

def parse_input(user_input):
    parts = user_input.strip().split()
    command = parts[0].lower() if parts else ""
    args = parts[1:]
    return command, *args

# ==================== Основний цикл ====================

def main():
    book = load_data()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_phone(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(show_upcoming_birthdays(book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
