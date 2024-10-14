import tkinter as tk
from tkinter import simpledialog, messagebox
import random
import string
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fpdf import FPDF
import webbrowser
import datetime


# Log transactions to a file
def log_transaction(username, transaction_type, amount):
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('TransactionLog.txt', 'a') as f:
        f.write(f'{username},{transaction_type},{amount},{current_time}\n')


# generate and convert transaction data into a PDF statement
def convert_file(username):
    pdf = FPDF()
    pdf.add_page()

    # Add title "BANK STATEMENT"
    pdf.set_font("Arial", 'BI', size=20)
    pdf.cell(0, 10, 'DigiBank TRANSACTION STATEMENT', 0, 1, 'C')
    pdf.ln(10)  # Add a line break after the title

    # Extract banker details from BankData.txt
    banker_details = ""
    current_balance = 0.0
    with open('BankData.txt', 'r') as file:
        for line in file:
            data = line.strip().split(',')
            if len(data) >= 5 and data[0] == username:
                account_number = data[4]
                current_balance = float(data[2])
                banker_details = (f"Username: {data[0]}\nEmail: {data[3]}\nCell Number: {data[6]}\nBanker Address:"
                                  f" {data[5]}\nAccount Number: " f"{account_number}")
                break

    # Set font for the banker details
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, banker_details)

    pdf.ln(10)  # Add a line break before the table

    # Set the font and size for the table header
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(40, 10, 'Date', 1)
    pdf.cell(40, 10, 'Time', 1)
    pdf.cell(70, 10, 'Type of Transaction', 1)
    pdf.cell(40, 10, 'Amount', 1)
    pdf.ln()

    with open('TransactionLog.txt', 'r') as file:
        transactions = file.readlines()
        user_transactions = [t.strip() for t in transactions if t.startswith(username)]

    pdf.set_font("Arial", size=12)
    if not user_transactions:
        pdf.cell(190, 10, "No transactions found.", 1, align="C")
    else:
        for transaction in user_transactions:
            transaction_parts = transaction.split(',')
            if len(transaction_parts) < 4:
                continue  # Skip improperly formatted lines
            transaction_type = transaction_parts[1]
            amount = transaction_parts[2]
            transaction_time = transaction_parts[3]

            # Split the datetime into date and time
            date, time = transaction_time.split(' ')

            pdf.cell(40, 10, date, 1)
            pdf.cell(40, 10, time, 1)
            pdf.cell(70, 10, transaction_type, 1)
            pdf.cell(40, 10, f'R{amount}', 1)
            pdf.ln()

    # Draw rectangle and add current balance
    pdf.ln(10)  # Add a line break before the rectangle
    pdf.set_fill_color(220, 220, 220)  # Light grey fill
    pdf.set_draw_color(0, 0, 0)  # Black border
    pdf.rect(10, pdf.get_y(), 190, 10, 'DF')
    pdf.set_xy(10, pdf.get_y() + 1)
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(0, 8, f'Current Balance: R{current_balance:.2f}', 0, 1, 'C')

    # Add message to the banker at the bottom
    pdf.ln(10)  # Add a line break before the message
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, "If you have any questions about your statement, please contact DigiBank.")

    pdf_file = f"{username}_statement.pdf"
    pdf.output(pdf_file)
    return pdf_file


def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(11))
    return password


def generate_account_number():
    account_number = ''.join(random.choice(string.digits) for _ in range(9))
    return account_number


def load_users():
    users = {}
    if os.path.exists('BankData.txt'):
        with open('BankData.txt', 'r') as f:
            for line in f:
                data = line.strip().split(',')
                if len(data) >= 6:
                    username = data[0]
                    password = data[1]
                    try:
                        balance = float(data[2])
                    except ValueError:
                        continue  # Skip this line if balance is not a valid float
                    email = data[3]
                    account_number = data[4]
                    address = data[5]
                    cell_number = data[6] if len(data) > 6 else ''
                    users[username] = (password, balance, email, account_number, address, cell_number)
    return users


def save_users(users):
    with open('BankData.txt', 'w') as f:
        for username, (password, balance, email, account_number, address, cell_number) in users.items():
            f.write(f'{username},{password},{balance},{email},{account_number},{address},{cell_number}\n')


def send_email(email, statement):
    sender_email = 'bahlebolilitye8@gmail.com'  # Update with your email
    sender_password = 'boxx gnqp jhgy kgto'  # Update with your email password

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = 'Your Transaction Statement FROM DigiBank'

    body = "\n".join(statement)
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, email, text)
        server.quit()
        messagebox.showinfo("Email Sent", "Transaction statement sent successfully to your email.")
    except Exception as e:
        messagebox.showerror("Email Error", f"Failed to send email: {str(e)}")


class BankApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.root = None
        self.login_frame = None
        self.signup_frame = None  # Initialize signup_frame here
        self.main_frame = None  # Initialize main_frame here
        self.slogan_label1 = None  # Initialize slogan_label1 here
        self.users = load_users()
        self.current_user = None
        self.balance = 0.0
        self.title("WELCOME TO DigiBank")
        self.geometry("530x780")
        self.configure(bg="#f0f0f0")
        self.create_widgets()

    def create_widgets(self):
        self.login_frame = tk.Frame(self.root, bg="#FFFFFF")
        self.login_frame.pack(fill="both", expand=True)

        # Load and display the logo image
        logo_img = tk.PhotoImage(file="digi.png - Copy.png")  # Update with your image file path
        logo_label = tk.Label(self.login_frame, image=logo_img, bg="#3498db")
        logo_label.image = logo_img  # Keep a reference to prevent image from being garbage collected
        logo_label.pack(pady=5)

        tk.Label(self.login_frame, text="Building Brighter Futures Together", bg="#FFFFFF", fg="black",
                 font=("Helvetica", 15)).pack(pady=15)

        self.login_frame = tk.Frame(self, bg="#3498db")
        tk.Label(self.login_frame, text="Username:", bg="#3498db", fg="black", font=("Helvetica", 15)).pack(pady=5)
        self.login_username_entry = tk.Entry(self.login_frame, width=25)
        self.login_username_entry.pack(pady=5, ipady=5)

        tk.Label(self.login_frame, text="Password:", bg="#3498db", fg="black", font=("Helvetica", 15)).pack(pady=5)
        self.login_password_entry = tk.Entry(self.login_frame, show="*", width=25)
        self.login_password_entry.pack(pady=5, ipady=5)

        self.login_button = tk.Button(self.login_frame, text="Login", command=self.login, bg="#2980b9", fg="white",
                                      padx=1, width=10, height=1, font=("Helvetica", 15), borderwidth=0)
        self.login_button.pack(pady=5)

        self.signup_button = tk.Button(self.login_frame, text="Signup", command=self.show_signup_frame, bg="#34495e",
                                       fg="white", padx=1, width=10, height=1, font=("Helvetica", 15), borderwidth=0)
        self.signup_button.pack(pady=5)
        self.login_frame.pack(fill='both', expand=True)

        self.signup_frame = tk.Frame(self, bg="#bdc3c7")
        tk.Label(self.signup_frame, text="Choose a Username:", bg="#bdc3c7").pack(pady=5)
        self.signup_username_entry = tk.Entry(self.signup_frame)
        self.signup_username_entry.pack(pady=5)

        self.auto_password_var = tk.BooleanVar()
        self.auto_password_checkbox = tk.Checkbutton(self.signup_frame, text="Auto-generate Password",
                                                     variable=self.auto_password_var,
                                                     command=self.toggle_password_entry, bg="#bdc3c7")
        self.auto_password_checkbox.pack(pady=5)

        self.password_label = tk.Label(self.signup_frame, text="Choose a Password:", bg="#bdc3c7")
        self.password_label.pack(pady=5)
        self.signup_password_entry = tk.Entry(self.signup_frame, show="*")
        self.signup_password_entry.pack(pady=5)

        tk.Label(self.signup_frame, text="Enter Initial Balance:", bg="#bdc3c7").pack(pady=5)
        self.signup_balance_entry = tk.Entry(self.signup_frame)
        self.signup_balance_entry.pack(pady=5)

        tk.Label(self.signup_frame, text="Enter Email:", bg="#bdc3c7").pack(pady=5)
        self.signup_email_entry = tk.Entry(self.signup_frame)
        self.signup_email_entry.pack(pady=5)

        # Add Address field to sign-up frame
        tk.Label(self.signup_frame, text="Enter Address:", bg="#bdc3c7").pack(pady=5)
        self.signup_address_entry = tk.Entry(self.signup_frame)
        self.signup_address_entry.pack(pady=5)

        # Add cell number field to sign-up frame
        tk.Label(self.signup_frame, text="Enter Cell Number:", bg="#bdc3c7").pack(pady=5)
        self.signup_cell_entry = tk.Entry(self.signup_frame)
        self.signup_cell_entry.pack(pady=5)

        self.signup_submit_button = tk.Button(self.signup_frame, text="Signup", command=self.signup, bg="#2980b9",
                                              fg="white", padx=1, width=10, height=1, font=("Helvetica", 15),
                                              borderwidth=0)
        self.signup_submit_button.pack(pady=5)

        self.signup_back_button = tk.Button(self.signup_frame, text="Back", command=self.show_login_frame, bg="#FF0000",
                                            fg="white", padx=1, width=10, height=1, font=("Helvetica", 15),
                                            borderwidth=0)
        self.signup_back_button.pack(pady=5)

        self.main_frame = tk.Frame(self, bg="#3498db")
        self.balance_label = tk.Label(self.main_frame, text="Current Balance: R0.00", bg="#ecf0f1")
        self.balance_label.pack(pady=5)

        self.transaction_button = tk.Button(self.main_frame, text="Make a Transaction",
                                            command=self.make_transaction_window, bg="#2980b9", fg="white", padx=1,
                                            width=20, height=1, font=("Helvetica", 15), borderwidth=0)
        self.transaction_button.pack(pady=5)

        self.statement_button = tk.Button(self.main_frame, text="View Statement", command=self.view_statement,
                                          bg="#34495e", fg="white", padx=1, width=20, height=1, font=("Helvetica", 15),
                                          borderwidth=0)
        self.statement_button.pack(pady=10)

        self.email_statement_button = tk.Button(self.main_frame, text="Email Statement", command=self.email_statement,
                                                bg="#e74c3c", fg="white", padx=1, width=20, height=1,
                                                font=("Helvetica", 15), borderwidth=0)
        self.email_statement_button.pack(pady=5)

        self.logout_button = tk.Button(self.main_frame, text="Logout", command=self.logout, bg="#95a5a6", fg="white",
                                       padx=1, width=20, height=1, font=("Helvetica", 15), borderwidth=0)
        self.logout_button.pack(side=tk.BOTTOM, pady=10)

        self.profile_button = tk.Button(self.main_frame, text="My Profile", command=self.show_profile, bg="#34495e",
                                        fg="white", padx=1, width=20, height=1, font=("Helvetica", 15), borderwidth=0)
        self.profile_button.pack(pady=5)

        self.show_login_frame()

    # Other methods...

    def toggle_password_entry(self):
        if self.auto_password_var.get():
            self.signup_password_entry.pack_forget()
            self.password_label.config(text="Auto-generated Password will be used.")
        else:
            self.signup_password_entry.pack(pady=5)
            self.password_label.config(text="Choose a Password:")

    def login(self):
        username = self.login_username_entry.get()
        password = self.login_password_entry.get()

        if username in self.users and self.users[username][0] == password:
            self.current_user = username
            self.balance = self.users[username][1]
            messagebox.showinfo("Login Successful", f'Welcome, {username}!')
            self.show_main_frame()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def send_profile_via_email(self):
        if not self.current_user:
            messagebox.showerror("Error", "Please login first.")
            return

        username = self.current_user
        password, balance, email, account_number, address, cell_number = self.users[username]

        profile_details = (
            f"Username: {username}\n"
            f"Password: {password}\n"
            f"Balance: R{balance:.2f}\n"
            f"Email: {email}\n"
            f"Account Number: {account_number}\n"
            f"Address: {address}\n"
            f"Phone Number: {cell_number}"
        )

        send_email(email, [profile_details])
        messagebox.showinfo("Email Sent", "Profile details sent successfully to your email.")

    def signup(self):
        username = self.signup_username_entry.get()

        if username in self.users:
            messagebox.showerror("Signup Failed", "Username already exists. Please choose a different username.")
            return

        if self.auto_password_var.get():
            password = generate_password()
            messagebox.showinfo("Generated Password", f"Your generated password is: {password}")
        else:
            password = self.signup_password_entry.get()

        try:
            initial_balance = float(self.signup_balance_entry.get())
        except ValueError:
            messagebox.showerror("Signup Failed", "Please enter a valid initial balance.")
            return

        email = self.signup_email_entry.get()
        if not email:
            messagebox.showerror("Signup Failed", "Please enter an email address.")
            return

        address = self.signup_address_entry.get()
        if not address:
            messagebox.showerror("Signup Failed", "Please enter an address.")
            return

        cell_number = self.signup_cell_entry.get()
        if not cell_number:
            messagebox.showerror("Signup Failed", "Please enter a cell number.")
            return

        account_number = generate_account_number()
        self.users[username] = (password, initial_balance, email, account_number, address, cell_number)
        save_users(self.users)

        messagebox.showinfo("Signup Successful", "Account created successfully.")
        self.show_login_frame()

        # Send profile details via email
        self.send_profile_via_email()
        self.show_login_frame()

    def make_transaction_window(self):
        transaction_window = tk.Toplevel(self)
        transaction_window.title("Make a Transaction")
        transaction_window.configure(bg="#3498db")
        transaction_window.geometry("300x200")

        # Show current balance
        current_balance_label = tk.Label(transaction_window, text=f"Balance: R{self.balance:.2f}", bg="#3498db",
                                         fg="black", font=("Helvetica", 15))

        current_balance_label.pack(pady=10)
        deposit_button = tk.Button(transaction_window, text="Deposit", command=self.make_deposit, bg="#2980b9",
                                   fg="white", padx=10)
        deposit_button.pack(pady=10)

        transfer_button = tk.Button(transaction_window, text="Transfer", command=self.make_transfer, bg="#2980b9",
                                    fg="white", padx=10)
        transfer_button.pack(pady=10)

        withdraw_button = tk.Button(transaction_window, text="Withdraw", command=self.make_withdrawal, bg="#2980b9",
                                    fg="white", padx=10)
        withdraw_button.pack(pady=10)

    def make_deposit(self):
        self.perform_transaction('Deposit')

    def make_transfer(self):
        self.perform_transaction('Transfer')

    def make_withdrawal(self):
        self.perform_transaction('Withdraw')

    def perform_transaction(self, transaction_type):
        if not self.current_user:
            messagebox.showerror("Error", "Please login first.")
            return

        try:
            amount = float(simpledialog.askstring("Amount", f"Enter amount to {transaction_type}:"))
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount.")
            return

        if transaction_type == 'Withdraw' and amount > self.balance:
            messagebox.showerror("Error", "Insufficient balance.")
            return

        if transaction_type == 'Deposit':
            self.balance += amount
        elif transaction_type == 'Withdraw':
            self.balance -= amount
        elif transaction_type == 'Transfer':
            self.balance -= amount

        # For Transfer, you would need additional logic to handle transferring funds between accounts

        self.users[self.current_user] = (
            self.users[self.current_user][0], self.balance, self.users[self.current_user][2],
            self.users[self.current_user][3], self.users[self.current_user][4], self.users[self.current_user][5]
        )
        save_users(self.users)
        log_transaction(self.current_user, transaction_type, amount)
        self.update_balance_label()

        # Show message box with the updated balance
        messagebox.showinfo("Transaction Successful",
                            f'Transaction of R{amount} {transaction_type.lower()} '
                            f'successfully.\nCurrent Balance: R{self.balance:.2f}')

    def view_statement(self):
        if not self.current_user:
            messagebox.showerror("Error", "Please login first.")
            return

        username = self.current_user
        pdf_file = convert_file(username)
        webbrowser.open(pdf_file)

    def email_statement(self):
        if not self.current_user:
            messagebox.showerror("Error", "Please login first.")
            return

        username = self.current_user
        user_details = {
            'email': '',
            'account_number': '',
            'address': '',
            'cell_number': ''
        }

        # Read user details from BankData.txt
        with open('BankData.txt', 'r') as file:
            for line in file:
                data = line.strip().split(',')
                if len(data) >= 6 and data[0] == username:
                    user_details['email'] = data[3]
                    user_details['account_number'] = data[4]
                    user_details['address'] = data[5]
                    user_details['cell_number'] = data[6] if len(data) > 6 else ''
                    break

        statement = []

        with open('TransactionLog.txt', 'r') as file:
            transactions = file.readlines()
            user_transactions = [t.strip() for t in transactions if t.startswith(username)]

        if not user_transactions:
            statement.append("No transactions found.")
        else:
            for transaction in user_transactions:
                transaction_parts = transaction.split(',')
                transaction_type = transaction_parts[1]
                amount = transaction_parts[2]
                transaction_time = transaction_parts[3]
                text = f"{transaction_time} - {transaction_type} - R{amount}"
                statement.append(text)

        # Generate PDF statement with instructions
        pdf_file = convert_file(username)

        # Send email with statement and instructions
        send_email(user_details['email'], statement)

        # Optionally, open the generated PDF
        webbrowser.open(pdf_file)

    def logout(self):
        self.current_user = None
        self.balance = 0.0
        self.show_login_frame()

    def show_login_frame(self):
        self.signup_frame.pack_forget()
        self.main_frame.pack_forget()
        self.login_frame.pack(fill='both', expand=True)

    def show_signup_frame(self):
        self.login_frame.pack_forget()
        self.main_frame.pack_forget()
        self.signup_frame.pack(fill='both', expand=True)

    def show_main_frame(self):
        self.login_frame.pack_forget()
        self.signup_frame.pack_forget()
        self.main_frame.pack(fill='both', expand=True)
        self.update_balance_label()

    def update_balance_label(self):
        self.balance_label.config(text=f"Current Balance: R{self.balance:.2f}")

    def show_profile(self):
        if not self.current_user:
            messagebox.showerror("Error", "Please login first.")
            return

        username = self.current_user
        password, balance, email, account_number, address, cell_number = self.users[username]

        profile_window = tk.Toplevel(self)
        profile_window.title("My Profile")
        profile_window.geometry("340x380")  # Set geometry to 320x360 pixels
        profile_window.configure(bg="white")  # Set background color to white

        # Add whitespace at the top
        tk.Label(profile_window, text="", bg="white", height=1).pack()  # Adjust height as needed for top spacing

        # Labels with bold text, font size 13, dark navy blue text color, and whitespace before each line
        tk.Label(profile_window, text=f"Username: {username}", bg="white", fg="#001f3f",
                 font=("Helvetica", 13, "bold")).pack(pady=5, padx=10, anchor='w')
        tk.Label(profile_window, text=f"Password: {password}", bg="white", fg="#001f3f",
                 font=("Helvetica", 13, "bold")).pack(pady=5, padx=10, anchor='w')
        tk.Label(profile_window, text=f"Balance: R{balance:.2f}", bg="white", fg="#001f3f",
                 font=("Helvetica", 13, "bold")).pack(pady=5, padx=10, anchor='w')
        tk.Label(profile_window, text=f"Email: {email}", bg="white", fg="#001f3f", font=("Helvetica", 13, "bold")).pack(
            pady=5, padx=10, anchor='w')
        tk.Label(profile_window, text=f"Account Number: {account_number}", bg="white", fg="#001f3f",
                 font=("Helvetica", 13, "bold")).pack(pady=5, padx=10, anchor='w')

        # Buttons with bold text, font size 13, dark navy blue text color, white background, and white text color
        edit_email_button = tk.Button(profile_window, text="Update Email",
                                      command=lambda: self.edit_email(profile_window, email),
                                      bg="#34495e", fg="white", padx=10, pady=5, width=20,
                                      font=("Helvetica", 13, "bold"))
        edit_email_button.pack(pady=10, padx=10, anchor='w')

        edit_cell_button = tk.Button(profile_window, text="Update Phone Number",
                                     command=lambda: self.edit_cell(profile_window, cell_number),
                                     bg="#34495e", fg="white", padx=10, pady=5, width=20,
                                     font=("Helvetica", 13, "bold"))
        edit_cell_button.pack(pady=5, padx=10, anchor='w')

        edit_address_button = tk.Button(profile_window, text="Update Address",
                                        command=lambda: self.edit_address(profile_window, address),
                                        bg="#34495e", fg="white", padx=10, pady=5, width=20,
                                        font=("Helvetica", 13, "bold"))
        edit_address_button.pack(pady=5, padx=10, anchor='w')

        # Add whitespace at the bottom
        tk.Label(profile_window, text="", bg="white", height=1).pack()  # Adjust height as needed for bottom spacing

    def edit_email(self, profile_window, current_email):
        new_email = simpledialog.askstring("Update Email", "Enter new email address:", initialvalue=current_email)
        if new_email:
            self.users[self.current_user] = (
                self.users[self.current_user][0], self.users[self.current_user][1], new_email,
                self.users[self.current_user][3], self.users[self.current_user][4], self.users[self.current_user][5])
            save_users(self.users)
            messagebox.showinfo("Email Updated", "Email address updated successfully.")
            profile_window.destroy()
            self.show_profile()

    def edit_cell(self, profile_window, current_cell):
        new_cell = simpledialog.askstring("Update Cell Number", "Enter new cell number:", initialvalue=current_cell)
        if new_cell:
            self.users[self.current_user] = (
                self.users[self.current_user][0], self.users[self.current_user][1], self.users[self.current_user][2],
                self.users[self.current_user][3], self.users[self.current_user][4], new_cell)
            save_users(self.users)
            messagebox.showinfo("Cell Number Updated", "Cell number updated successfully.")
            profile_window.destroy()
            self.show_profile()

    def edit_address(self, profile_window, current_address):
        new_address = simpledialog.askstring("Address", "Enter new address:", initialvalue=current_address)
        if new_address:
            self.users[self.current_user] = (
                self.users[self.current_user][0], self.users[self.current_user][1], self.users[self.current_user][2],
                self.users[self.current_user][3], new_address, self.users[self.current_user][5])
            save_users(self.users)
            messagebox.showinfo("Address Updated", "Address updated successfully.")
            profile_window.destroy()
            self.show_profile()


if __name__ == "__main__":
    app = BankApplication()
    app.mainloop()