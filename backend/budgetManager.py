from backend.transaction import Transaction

class BudgetManager:
    """Manages transactions and calculations using the SQLite database."""
    def __init__(self, db_manager):
        self.transactions = []
        self.db = db_manager  # Pass the Database instance here

    def load_user_data(self, user_id):
        """Loads only the logged-in user's transactions from SQLite."""
        self.transactions = []
        raw_data = self.db.get_user_transactions(user_id)
        
        for item in raw_data:
            # row format: (amount, category, description, type, date)
            self.transactions.append(Transaction(*item))

    def add_transaction(self, user_id, transaction):
        """Saves to DB and local list."""
        self.db.save_transaction(user_id, transaction)
        self.transactions.append(transaction)

    def delete_transaction(self, user_id, index):
        if 0 <= index < len(self.transactions):
            # Get the specific transaction object
            target = self.transactions[index]
            
            # Delete from SQLite database
            self.db.delete_transaction(user_id, target.date, target.amount)
            
            # Remove from the local memory list
            del self.transactions[index]
    # --- Calculations ---

    def calculate_total_income(self):
        return sum(t.amount for t in self.transactions if t.type == "Income")

    def calculate_total_expenses(self):
        return sum(t.amount for t in self.transactions if t.type == "Expense")

    def calculate_balance(self):
        total_income = sum(t.amount for t in self.transactions if t.type == "Income")
        total_expense = sum(t.amount for t in self.transactions if t.type == "Expense")
        return total_income - total_expense

    def get_category_summary(self, t_type="Expense"):
        summary = {}
        for t in self.transactions:
            if t.type == t_type:
                summary[t.category] = summary.get(t.category, 0) + t.amount
        return summary