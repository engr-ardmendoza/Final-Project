from frontend.root import GUI  # Updated Import
from backend.budgetManager import BudgetManager
from backend.database import Database

if __name__ == "__main__":
    db = Database()
    budget_mgr = BudgetManager(db)
    app = GUI(budget_mgr)
    app.mainloop()