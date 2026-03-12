import matplotlib.pyplot as plt # type: ignore
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # type: ignore
from collections import defaultdict

class Visualization:
    """
    Handles the creation and rendering of Matplotlib charts within 
    a Tkinter container for budget data analysis.
    """
    def __init__(self, container, budget_manager):
        """
        Initialize the Visualization controller.
        
        Args:
            container: The Tkinter frame/widget where the chart will be packed.
            budget_manager: The data source containing transaction history.
        """
        self.container = container
        self.budget_manager = budget_manager
        self.canvas = None  # Holds the FigureCanvasTkAgg object
        self.current_chart_type = "Pie"

    def draw_chart(self, chart_type="Pie"):
        """
        Generates a specific plot based on chart_type and embeds it into the GUI.
        """
        
        self.current_chart_type = chart_type
        # Clear the previous chart from the UI if it exists
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        # Create a new figure and axis for the plot
        fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
        
        # --- Logic for Categorical Data (Pie/Bar) ---
        if chart_type in ["Pie", "Bar"]:
            summary = self.budget_manager.get_category_summary(t_type="Expense")
            if not summary: 
                return # Exit if no data is available to plot
            
            categories = list(summary.keys())
            values = list(summary.values())

            if chart_type == "Pie":
                ax.pie(values, labels=categories, autopct='%1.1f%%', startangle=140)
                ax.set_title("Expenses by Category")
            elif chart_type == "Bar":
                ax.bar(categories, values, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
                ax.set_title("Spending Comparison")
                ax.set_ylabel("Amount ($)")

        # --- Logic for Time-Based Data (Scatter/Line) ---
        elif chart_type in ["Scatter", "Line"]:
            # Aggregate expense amounts by date to prevent overlapping data points
            daily_totals = defaultdict(float)
            for t in self.budget_manager.transactions:
                if t.type == "Expense":
                    # Extract date only (YYYY-MM-DD) from possible timestamp string
                    date_only = t.date.split(" ")[0]
                    daily_totals[date_only] += t.amount
            
            # Sort data chronologically for proper line/scatter flow
            sorted_dates = sorted(daily_totals.keys())
            sorted_amounts = [daily_totals[d] for d in sorted_dates]

            if chart_type == "Scatter":
                ax.scatter(sorted_dates, sorted_amounts, color='purple')
                ax.set_title("Daily Spending (Points)")
            else: # Line Chart
                ax.plot(sorted_dates, sorted_amounts, marker='o', linestyle='-', color='#e74c3c')
                ax.set_title("Spending Trend Over Time")
            
            # Rotate date labels to prevent overlap
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

        # --- Cash Flow Logic (Income vs Expense) ---
        elif chart_type == "Cash Flow":
            # Sum totals directly from the transaction list
            income = sum(t.amount for t in self.budget_manager.transactions if t.type == "Income")
            expense = sum(t.amount for t in self.budget_manager.transactions if t.type == "Expense")
            
            ax.bar(["Total Income", "Total Expense"], [income, expense], color=['#2ecc71', '#e74c3c'])
            ax.set_title("Cash Flow Overview")
            ax.set_ylabel("Total ($)")

        # Finalize layout and embed the plot into the Tkinter container
        fig.tight_layout()
        self.canvas = FigureCanvasTkAgg(fig, master=self.container)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)