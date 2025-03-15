import tkinter.messagebox

from tkinter import *
import random
import string
import pyperclip
import json
import os
from tkinter import simpledialog
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import base64

EMAIL_FILE = "email.json"
ENCRYPTED_FILE = "accounts_remembered.enc"
load_dotenv()
FERNET_KEY  = os.getenv("FERNET_KEY")

def save_email(email):
    with open(EMAIL_FILE, "w") as file:
        json.dump({"email": email}, file, indent=4)
def load_email():
    if os.path.exists(EMAIL_FILE):
        try:
            with open(EMAIL_FILE, "r") as file:
                data = json.load(file)
                user_email = data.get("email")
        except:
            root = Tk()
            root.withdraw()
            user_email = simpledialog.askstring("Input email!", "Please enter your email: ")
            if user_email:
                save_email(user_email)
            root.destroy()

    return user_email
def generate_password():
    pass_len = random.randint(10, 16)
    small_letters = list(string.ascii_lowercase)
    upper_letters = list(string.ascii_uppercase)
    numbers = list(string.digits)
    special_characters = list(string.punctuation)

    pass_small_letters = [random.choice(small_letters) for _ in range(2,5)]
    pass_upper_letters = [random.choice(upper_letters) for _ in range(2,5)]
    pass_numbers = [random.choice(numbers) for _ in range(2,5)]
    pass_special_characters = [random.choice(special_characters) for _ in range(2,5)]

    pass_characters = pass_small_letters + pass_upper_letters + pass_numbers + pass_special_characters
    random.shuffle(pass_characters)

    password = "".join(pass_characters)

    generated_password = StringVar()
    generated_password.set(password)
    password_entry.config(textvariable=generated_password)
    pyperclip.copy(password)


def add_button_clicked():
    consecutive_patterns = [
        "123", "234", "345", "456", "567", "678", "789", "890", "012",
        "abc", "bcd", "cde", "def", "efg", "fgh", "ghi", "hij", "ijk",
        "jkl", "klm", "lmn", "mno", "nop", "opq", "pqr", "qrs", "rst",
        "stu", "tuv", "uvw", "vwx", "wxy", "xyz"
    ]
    financial_words = [
        "JPG", "PDF", "PNG", "DOC", "XLS", "ZIP", "BANK", "CREDIT",
        "VISA", "PAYPAL", "CHASE", "CITI", "BOA", "HSBC", "GOLDMAN",
        "AMEX", "MASTERCARD", "SWIFT", "PIN", "SSN", "ACCOUNT",
        "MONEY", "CHECKING", "SAVINGS", "LOAN"
    ]
    common_passwords = [
        "123456", "password", "123456789", "12345678", "12345", "1234567",
        "123123", "qwerty", "abc123", "password1", "iloveyou", "admin",
        "welcome", "letmein", "football", "monkey", "dragon", "sunshine",
        "princess", "master", "hello", "freedom"
    ]

    prev_passwords = list()
    with open("accounts_remembered.txt", "r") as file:
        counter = 0
        for line in file:
            data_splitted = line.split("|")
            prev_passwords.append(data_splitted[2].strip())
            counter += 1
            if counter == 5:
                break

    website_label.config(fg="black")
    email_or_username_label.config(fg="black")
    password_label.config(fg="black")
    errors = False

    if any(element for element in common_passwords if element.lower() in password_entry.get().lower()) \
        or any(element for element in financial_words if element.lower() in password_entry.get().lower()) \
        or any(element for element in consecutive_patterns if element in password_entry.get()) \
        or any(character for character in password_entry.get().lower() if password_entry.get().lower().count(character) > 2) \
        or password_entry.get() == email_or_username_entry.get() \
        or len(password_entry.get()) < 8 or len(password_entry.get()) > 32 \
            or any(prev_password for prev_password in prev_passwords if password_entry.get() == prev_password):
            errors = True
            password_label.config(fg="red")

    if website_entry.get() == "":
        errors = True
        website_label.config(fg="red")

    if email_or_username_entry.get() == "":
        errors = True
        email_or_username_label.config(fg="red")

    if not errors:
        new_data = {
            website_entry.get().lower() : {
                "email" : email_or_username_entry.get(),
                "password" : password_entry.get(),
            }
        }

        def added_succesed():
            website_entry.delete(0, END)
            password_entry.delete(0, END)
            tkinter.messagebox.showinfo(title="Success", message="Password has been added successfully")

        try:
            add_password(json.dumps(new_data), FERNET_KEY)
            added_succesed()
        except:
            print("some error")

    else:
        tkinter.messagebox.showerror(title="Error", message="Some errors has occured.")

def generate_key():
    key = Fernet.generate_key().decode()
    with open(".env", "a") as env_file:
        env_file.write(f"\nFERNET_KEY={key}")
def load_encrypted_data(key):
    cipher = Fernet(key)
    if not os.path.exists(ENCRYPTED_FILE):
        return {}  # Zwracamy pusty JSON, jeśli plik nie istnieje

    try:
        with open(ENCRYPTED_FILE, "rb") as file:
            encrypted_data = file.read()
            decrypted_data = cipher.decrypt(encrypted_data).decode()
            return json.loads(decrypted_data)
    except Exception as e:
        print(f"Błąd odszyfrowywania pliku: {e}")
        return {}

def save_encrypted_data(data, key):
    cipher = Fernet(key)
    try:
        json_string = json.dumps(data, indent=4)
        encrypted_data = cipher.encrypt(json_string.encode())

        with open(ENCRYPTED_FILE, "wb") as file:
            file.write(encrypted_data)

    except Exception as e:
        print(f"Error while encrypting: {e}")

def add_password(json_data, key):
    try:
        new_data = json.loads(json_data)
    except json.JSONDecodeError:
        print("Error: Invalid JSON format!")
        return

    existing_data = load_encrypted_data(key)

    for service, accounts in new_data.items():
        if service in existing_data:
            existing_data[service].extend(accounts)
        else:
            existing_data[service] = accounts

    save_encrypted_data(existing_data, key)

def search_button_clicked():
    try:
        data_from_file = load_encrypted_data(FERNET_KEY)
    except:
        tkinter.messagebox.showinfo(title="Empty file", message="File doesn't have any input yet.")
        return

    website = website_entry.get().lower()

    if website in data_from_file:
        found_accounts = data_from_file[website]

        message = ""
        for account in found_accounts:
            message += f"Email: {account['email']}\nPassword: {account['password']}\n\n"

        tkinter.messagebox.showinfo(title=website_entry.get().title(), message=message.strip())
    else:
        tkinter.messagebox.showinfo(title="Fail", message=f"Website '{website_entry.get()}' has not been found.")

FONT_TUPLE = ("Courier", 12, "normal")

my_email = load_email()

if not (os.path.exists(r".\.env") and os.path.getsize(r".\.env") > 0):
    generate_key()

window = Tk()
window.title("Password Manager")
window.config(padx = 100, pady = 50)

canvas = Canvas(window, width = 200, height = 200)
image = PhotoImage(file = 'logo.png')
canvas.create_image(100, 100, image=image)
canvas.grid(row = 0, column = 1)

website_label = Label(window, text='Website: ', padx = 30, pady = 10, font = FONT_TUPLE)
website_label.grid(row = 1, column = 0)

website_entry = Entry(window, font = FONT_TUPLE)
website_entry.grid(row = 1, column = 1, sticky = "ew")

search_by_website_button = Button(window, text="Search", padx = 5, pady = 2, command = search_button_clicked, bd=3, font=FONT_TUPLE)
search_by_website_button.grid(row = 1, column = 2, sticky = "ew", padx=20)

email_or_username_label = Label(window, text='Email/Username: ', padx = 30, pady = 10, font = FONT_TUPLE)
email_or_username_label.grid(row = 2, column = 0)

email_or_username_entry = Entry(window, font = FONT_TUPLE)
email_or_username_entry.insert(0, my_email)
email_or_username_entry.grid(row = 2, column = 1, sticky = "ew", columnspan = 2)

password_label = Label(window, text='Password: ', padx = 30, pady = 10, font = FONT_TUPLE)
password_label.grid(row = 3, column = 0, sticky = "ew")

password_entry = Entry(window, font = FONT_TUPLE)
password_entry.grid(row = 3, column = 1)

button_password_label = Button(window, text='Generate Password', padx = 5, pady = 2, font = FONT_TUPLE, command=generate_password)
button_password_label.grid(row = 3, column = 2, padx=20)

button_add = Button(window, text='Add', padx = 5, pady = 2, font = FONT_TUPLE, bd=3, command=add_button_clicked)
button_add.grid(row = 4, column = 1, sticky = "ew", columnspan=2)

website_entry.focus()


window.mainloop()
