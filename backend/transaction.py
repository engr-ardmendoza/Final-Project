from datetime import datetime

class Transaction:
    """
    Data model representing a single financial record.
    
    This class bridges the gap between the SQLite database rows and the 
    frontend UI, supporting both Expense and Income types.
    """

    def __init__(self, db_id, amount, category, description, t_type="Expense", date=None):
        """
        Initializes a new Transaction instance.

        Args:
            db_id (int/None): The PRIMARY KEY from the SQLite 'transactions' table.
            amount (float/str): The monetary value of the transaction.
            category (str): The classification (e.g., 'Food', 'Rent', 'Salary').
            description (str): A brief note about the transaction.
            t_type (str): Either 'Expense' or 'Income'. Defaults to 'Expense'.
            date (str/None): The timestamp. If None, uses the current local time.
        """
        self.db_id = db_id  # Unique identifier used for database operations (Delete/Update)
        self.amount = float(amount)
        self.category = category
        self.description = description
        self.type = t_type 
        # Generate a timestamp in YYYY-MM-DD HH:MM format if one isn't provided
        self.date = date if date else datetime.now().strftime("%Y-%m-%d %H:%M")

    def to_dict(self):
        """
        Serializes the object into a dictionary format.
        
        Useful for debugging, transferring data between layers, 
        or preparing data for JSON serialization.
        """
        return {
            "db_id": self.db_id,
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "type": self.type,
            "date": self.date
        }

    @classmethod
    def from_dict(cls, data):
        """
        Factory method to create a Transaction instance from a dictionary.
        
        Args:
            data (dict): A dictionary containing transaction attributes.
            
        Returns:
            Transaction: A new instance of the class.
        """
        return cls(
            data.get('db_id'),          # Use .get() to handle cases where ID hasn't been assigned yet
            data['amount'], 
            data['category'], 
            data['description'], 
            data.get('type', 'Expense'), # Safeguard: default to 'Expense' if key is missing
            data.get('date')             # Handles case where date might not be in the dictionary
        )