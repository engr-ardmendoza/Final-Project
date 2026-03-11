import os
import sqlite3
import hashlib
from .passwordValidation import PasswordValidation

class Database:
    """
    Handles all SQLite database operations including user authentication,
    transaction management, and administrative privileges.
    """

    def __init__(self, db_name="finance.db"):
        """Initialize database connection and ensure tables exist."""
        # Get the absolute path to the backend directory to avoid 'file not found' errors
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(backend_dir, db_name)
        
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()
        
        # Ensure the master admin account (Ralph) always has admin rights
        self.set_primary_admin("Ralph")

    def create_tables(self):
        """Create users and transactions tables if they do not already exist."""
        # Table for storing user credentials and roles
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                is_admin INTEGER DEFAULT 0
            )
        ''')
        # Table for storing financial records linked to specific users
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                user_id INTEGER,
                amount REAL,
                category TEXT,
                description TEXT,
                type TEXT,
                date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        self.conn.commit()

    def set_primary_admin(self, username):
        """Hardcode admin status for the master user."""
        self.cursor.execute("UPDATE users SET is_admin = 1 WHERE username = ?", (username,))
        self.conn.commit()

    # --- USER AUTHENTICATION LOGIC ---

    def hash_password(self, password):
        """Convert plain text password into a secure SHA-256 hash."""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password):
        """Validate and save a new user to the database."""
        # 1. Check if password meets security complexity requirements
        is_valid, message = PasswordValidation.check_requirements(username, password)
        if not is_valid:
            return False, message

        try:
            # 2. Automatically grant admin status if the name is 'Ralph'
            is_admin_value = 1 if username.lower() == "ralph" else 0
            
            # 3. Insert user with hashed password
            self.cursor.execute(
                "INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", 
                (username, self.hash_password(password), is_admin_value)
            )
            self.conn.commit()
            return True, "Account created successfully!"
        except sqlite3.IntegrityError:
            return False, "Username already exists."

    def login_user(self, username, password):
        """Verify credentials and return (user_id, is_admin) or None."""
        self.cursor.execute(
            "SELECT id, is_admin FROM users WHERE username = ? AND password = ?", 
            (username, self.hash_password(password))
        )
        result = self.cursor.fetchone()
        return result if result else None

    def change_password(self, user_id, old_password, new_password):
        """
        Securely updates a user's password using Old Password verification 
        and PasswordValidation complexity rules.
        """
        try:
            # 1. Fetch current credentials
            self.cursor.execute("SELECT username, password FROM users WHERE id = ?", (user_id,))
            result = self.cursor.fetchone()
            
            if not result:
                return False, "User account not found."
            
            username, stored_hash = result

            # 2. Verify Old Password (Identity Verification)
            if self.hash_password(old_password) != stored_hash:
                return False, "Current password is incorrect."

            # 3. Check Complexity (Using your PasswordValidation class)
            is_valid, message = PasswordValidation.check_requirements(username, new_password)
            if not is_valid:
                return False, message

            # 4. Hash and Commit the new password
            new_hashed = self.hash_password(new_password)
            self.cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new_hashed, user_id))
            self.conn.commit()
            
            return True, "Password updated successfully!"

        except sqlite3.Error as e:
            return False, f"Database error: {e}"

    # --- ADMINISTRATIVE LOGIC ---
    def get_all_users_summary(self):
        """Retrieve list of all users and their total income/expenses for Admin view."""
        query = """
            SELECT 
                u.id, 
                u.username, 
                COALESCE(SUM(CASE WHEN t.type = 'Income' THEN t.amount ELSE 0 END), 0) as income,
                COALESCE(SUM(CASE WHEN t.type = 'Expense' THEN t.amount ELSE 0 END), 0) as expense
            FROM users u
            LEFT JOIN transactions t ON u.id = t.user_id
            GROUP BY u.id, u.username
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []

    def delete_user(self, user_id):
        """Perform a cascading delete: removes user records and all their transactions."""
        try:
            # Remove financial data first to maintain foreign key integrity
            self.cursor.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,)) 
            self.cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            self.conn.commit()
            return True, "User and their data deleted successfully."
        except sqlite3.Error as e:
            return False, f"Error: {e}"

    def promote_to_admin(self, username):
        """Grant administrative privileges to a specific username."""
        self.cursor.execute("UPDATE users SET is_admin = 1 WHERE username = ?", (username,))
        self.conn.commit()
        return True, f"{username} is now an Admin."
    
    def demote_to_user(self, username):
        """Removes administrative privileges from a specific username."""
        # Safety: Don't let Ralph demote himself or he'll be locked out of the Admin panel!
        if username.lower() == "ralph":
            return False, "Cannot demote the primary administrator."
            
        self.cursor.execute("UPDATE users SET is_admin = 0 WHERE username = ?", (username,))
        self.conn.commit()
        return True, f"{username} has been demoted."

    # --- TRANSACTION MANAGEMENT ---
    def save_transaction(self, user_id, t):
        """Insert a new financial record into the database."""
        self.cursor.execute('''
            INSERT INTO transactions (user_id, amount, category, description, type, date)
            VALUES (?, ?, ?, ?, ?, ?)''', 
            (user_id, t.amount, t.category, t.description, t.type, t.date))
        self.conn.commit()
        
    def get_all_users_basic(self):
        """Returns basic info for admin table."""
        self.cursor.execute("SELECT id, username, is_admin FROM users")
        return self.cursor.fetchall()

    def get_user_transactions(self, user_id):
        """Retrieve all transactions for a specific user, most recent first."""
        self.cursor.execute("""
            SELECT id, amount, category, description, type, date 
            FROM transactions WHERE user_id = ? ORDER BY date DESC
        """, (user_id,))
        return self.cursor.fetchall()

    def delete_transaction(self, transaction_id):
        """Permanently remove a transaction by its ID."""
        self.cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        self.conn.commit()
        
    def reset_password(self, username, new_password):
        """Admin only: Resets password without needing the old one."""
        # Still check complexity so the admin doesn't set '123'
        is_valid, message = PasswordValidation.check_requirements(username, new_password)
        if not is_valid:
            return False, message

        new_hashed = self.hash_password(new_password)
        self.cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_hashed, username))
        self.conn.commit()
        return True, f"Password for {username} reset successfully."
        
    def get_daily_total(self, user_id, date_str):
        """
        Fetches sum of expenses for a specific date.
        Uses 'LIKE' to ignore the time (HH:MM) stored in the database.
        """
        # Adding % after the date matches "YYYY-MM-DD" with "YYYY-MM-DD HH:MM"
        query = """
            SELECT SUM(amount) 
            FROM transactions 
            WHERE user_id = ? 
            AND date LIKE ? || '%' 
            AND type = 'Expense'
        """
        try:
            self.cursor.execute(query, (user_id, date_str))
            result = self.cursor.fetchone()
            return result[0] if result and result[0] is not None else 0.0
        except sqlite3.Error as e:
            print(f"Database Error: {e}")
            return 0.0