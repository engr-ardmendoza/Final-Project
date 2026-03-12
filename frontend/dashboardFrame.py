import tkinter as tk
import customtkinter as ctk # type: ignore
from tkinter import messagebox, filedialog
from frontend.visualization import Visualization
from backend.transaction import Transaction
from tkcalendar import Calendar # type: ignore
from PIL import Image # type: ignore
import os
from datetime import datetime
import pandas as pd # type: ignore

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, controller, budget_manager):
        super().__init__(parent)
        self.controller = controller
        self.budget_manager = budget_manager
        
        # Grid Configuration
        self.grid_columnconfigure(1, weight=1) # Right panel expands
        self.grid_rowconfigure(0, weight=1)

        # 1. Initialize State
        self.type_var = ctk.StringVar(value="Expense")
        self.current_view = "history" # Track which view is active

        # 2. Sidebar Layout
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # 3. Content Area (Right Side)
        self.content_area = ctk.CTkFrame(self, corner_radius=15)
        self.content_area.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.setup_sidebar()
        self.show_history_view() # Load History by default

    def setup_sidebar(self):
        """Builds the left navigation and input form."""
        # Header
        base_path = os.path.dirname(os.path.realpath(__file__))
        logo_path = os.path.join(base_path, "assets", "company_logo.png")
        my_logo = ctk.CTkImage(
            light_image=Image.open(logo_path),
            dark_image=Image.open(logo_path),
            size=(100,50) 
        )
        logo_label = ctk.CTkLabel(self.sidebar, image=my_logo, text="")
        logo_label.pack(pady=20)

        # Navigation Buttons
        ctk.CTkButton(self.sidebar, text="History", font=("Arial", 14), 
                      text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                      command=self.show_history_view).pack(fill="x", padx=20, pady=10)
        ctk.CTkButton(self.sidebar, text="Analytics", font=("Arial", 14),
                      text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                      command=self.show_analytics_view).pack(fill="x", padx=20)
        ctk.CTkButton(self.sidebar, text="Calendar View", font=("Arial", 14),
                      text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                      command=self.show_calendar_view).pack(fill="x", padx=20, pady=(10, 0))
        ctk.CTkButton(self.sidebar, text="Export Excel", font=("Arial", 14),
                      text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                      command=self.export_to_excel).pack(fill="x", padx=20, pady=(10, 10))

        ctk.CTkLabel(self.sidebar, text="────────────────", text_color="gray").pack(pady=(10,0))

        # --- Quick Add Form ---
        input_box = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        input_box.pack(fill="x", padx=20)

        self.type_selector = ctk.CTkSegmentedButton(
            input_box, 
            values=["Expense", "Income"], 
            variable=self.type_var,
            command=self.toggle_inputs # <--- Add this
        )
        self.type_selector.pack(pady=10, fill="x")

        # Define other fields
        self.amount_entry = ctk.CTkEntry(input_box, placeholder_text="Amount ($)")
        self.amount_entry.pack(pady=5, fill="x")

        self.category_combo = ctk.CTkComboBox(input_box, values=["Food", "Rent", "Transport", "Entertainment", "Other"])
        self.category_combo.set("Select Category")
        self.category_combo.pack(pady=5, fill="x")

        self.desc_entry = ctk.CTkEntry(input_box, placeholder_text="Description")
        self.desc_entry.pack(pady=5, fill="x")

        ctk.CTkButton(input_box, text="Add Transaction", command=self.add_expense).pack(pady=5, fill="x")
        ctk.CTkButton(input_box, text="Delete Transaction", command=self.remove_expense).pack(pady=5, fill="x")
        ctk.CTkButton(input_box, text="Edit Transaction", command=self.handle_edit_transaction).pack(pady=5, fill="x")
        
        ctk.CTkButton(self.sidebar, text="Logout", fg_color="#D32F2F", hover_color="#B71C1C",
                      command= lambda: self.controller.show_frame("LoginFrame")).pack(side="bottom", padx= 20, pady=(10, 20), fill="x")
        ctk.CTkButton(self.sidebar, text="Change Password", hover_color=("gray70", "gray30"),
                      command= lambda: self.controller.show_frame("ChangePasswordFrame")).pack(side="bottom", padx= 20, fill="x")

    def show_calendar_view(self):
        """Switches the panel to the Calendar View."""
        self.current_view = "calendar"
        self.clear_content()

        ctk.CTkLabel(self.content_area, text="Daily Spending Calendar", font=("Arial", 24, "bold")).pack(pady=15)

        # Calendar Card
        cal_container = ctk.CTkFrame(self.content_area, fg_color="#2b2b2b", corner_radius=15)
        cal_container.pack(pady=20, padx=40, fill="both", expand=True)

        self.cal = Calendar(cal_container, selectmode='day', 
                    # Main Colors
                    background="#1a1a1a",      # Matches your frame
                    foreground="white", 
                    borderwidth=0,
                    
                    # Header (Month/Year)
                    headersbackground="#3498db", 
                    headersforeground="white",
                    
                    # Days of the Week
                    selectbackground="#3498db", 
                    selectforeground="white",
                    
                    # The actual grid
                    normalbackground="#2d2d2d", 
                    normalforeground="white",
                    weekendbackground="#2d2d2d", 
                    weekendforeground="#3498db", # Highlight weekends in blue
                    
                    # The "Other Month" days
                    othermonthbackground="#1a1a1a",
                    othermonthforeground="gray30",
                    othermonthwebackground="#1a1a1a",
                    othermonthweforeground="gray30")
        self.cal.pack(pady=20, padx=20, fill="both", expand=True)

        # Total Label for Selected Date
        self.cal_total_label = ctk.CTkLabel(cal_container, text="Select a date to see spending", 
                                            font=("Arial", 18, "bold"), text_color="#3498db")
        self.cal_total_label.pack(pady=(0, 20))

        # Event Binding
        self.cal.bind("<<CalendarSelected>>", self.update_calendar_total)
        
    def update_calendar_total(self, event=None):
        raw_date = self.cal.get_date() 
        
        try:
            # Convert tkcalendar format (e.g. 3/12/26) to DB format (2026-03-12)
            date_obj = datetime.strptime(raw_date, '%m/%d/%y')
            formatted_date = date_obj.strftime('%Y-%m-%d') 
        except ValueError:
            formatted_date = raw_date

        user_id = self.controller.current_user_id
        total = self.budget_manager.db.get_daily_total(user_id, formatted_date)
        
        # UI Update
        if total > 0:
            self.cal_total_label.configure(
                text=f"Total Expenses on {formatted_date}: ${total:,.2f}", 
                text_color="#e74c3c"
            )
        else:
            self.cal_total_label.configure(
                text=f"No expenses found for {formatted_date}", 
                text_color="#2ecc71"
            )

    def toggle_inputs(self, selected_value):
        """Hides category combo if Income is selected."""
        if selected_value == "Income":
            self.category_combo.pack_forget()
        else:
            # Re-pack it before the description entry to keep the order
            self.category_combo.pack(pady=5, fill="x", before=self.desc_entry)

    # --- Content Switching Logic ---
    def clear_content(self):
        """Clears the right-side content area before switching views."""
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def show_history_view(self):
        self.current_view = "history"
        self.clear_content()
        
        ctk.CTkLabel(self.content_area, text="Transaction History", font=("Arial", 24, "bold")).pack(pady=15)
        
        # --- Modern Styling for Treeview ---
        style = tk.ttk.Style()
        style.theme_use("default") # Required to allow custom colors
        
        style.configure("Treeview",
                        background="#2b2b2b",
                        foreground="white",
                        rowheight=35, # More breathing room
                        fieldbackground="#2b2b2b",
                        borderwidth=0,
                        font=("Arial", 11))
        
        style.configure("Treeview.Heading",
                        background="#333333",
                        foreground="white",
                        relief="flat",
                        font=("Arial", 12, "bold"))

        # Highlight color when a row is selected
        style.map("Treeview", background=[('selected', '#1f538d')]) 

        # Summary Labels Card
        summary_f = ctk.CTkFrame(self.content_area, fg_color="#333333", corner_radius=10)
        summary_f.pack(fill="x", padx=20, pady=10)
        
        self.total_label = ctk.CTkLabel(summary_f, text="Balance: $0.00", font=("Arial", 20, "bold"))
        self.total_label.pack(side="left", padx=20, pady=15)

        # --- Treeview Table ---
        cols = ("Amount", "Category", "Type", "Date")
        # Wrap Treeview in a frame to give it a "borderless" card appearance
        tree_container = ctk.CTkFrame(self.content_area, fg_color="transparent")
        tree_container.pack(fill="both", expand=True, padx=20, pady=10)

        self.tree = tk.ttk.Treeview(tree_container, columns=cols, show="headings", style="Treeview")
        # Double-click a row to edit
        self.tree.bind("<Double-1>", lambda event: self.handle_edit_transaction())
        
        for col in cols:
            self.tree.heading(col, text=col)
            # Center the text for Category/Type/Date, Right-align for Amount
            anchor_val = "e" if col == "Amount" else "center"
            self.tree.column(col, width=100, anchor=anchor_val)

        # Add zebra stripes for readability
        self.tree.tag_configure('oddrow', background='#333333')
        self.tree.tag_configure('evenrow', background='#2b2b2b')

        self.tree.pack(fill="both", expand=True)
        
        self.refresh_ui()

    def show_analytics_view(self):
        self.current_view = "analytics"
        self.clear_content()
        
        # 1. Header
        ctk.CTkLabel(self.content_area, text="Financial Insights", font=("Arial", 24, "bold")).pack(pady=(20, 10))

        # Calculate data for cards
        total_spent = sum(t.amount for t in self.budget_manager.transactions if t.type == "Expense")
        total_income = sum(t.amount for t in self.budget_manager.transactions if t.type == "Income")
        net_savings = total_income - total_spent

        # 2. Quick Stats Row
        stats_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        stats_frame.pack(fill="x", padx=30, pady=10)

        # Configure the grid to have 3 equal columns
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Create 3 mini-cards using .grid instead of .pack
        self.create_stat_card(stats_frame, "Total Spent", f"${total_spent:,.2f}", "#e74c3c").grid(row=0, column=0, padx=10, sticky="nsew")
        self.create_stat_card(stats_frame, "Total Income", f"${total_income:,.2f}", "#2ecc71").grid(row=0, column=1, padx=10, sticky="nsew")
        self.create_stat_card(stats_frame, "Net Savings", f"${net_savings:,.2f}", "#3498db").grid(row=0, column=2, padx=10, sticky="nsew")

        # 3. Chart Selector - added fill="x" and increased padx to match cards
        selector = ctk.CTkSegmentedButton(
            self.content_area, 
            values=["Pie", "Bar", "Line", "Scatter", "Cash Flow"],
            command=lambda v: self.visualizer.draw_chart(v),
            height=40  # Slightly taller for better touch/click area
        )
        selector.set("Pie")
        # fill="x" makes it stretch from left to right
        selector.pack(pady=20, padx=40, fill="x")

        # 4. Chart Container with "Card" styling
        self.chart_frame = ctk.CTkFrame(self.content_area, fg_color="#2b2b2b", corner_radius=15, border_width=1, border_color="#3d3d3d")
        self.chart_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        self.visualizer = Visualization(self.chart_frame, self.budget_manager)
        self.visualizer.draw_chart("Pie")

    def create_stat_card(self, parent, title, value, color):
        """Helper method to create a clean-looking stat box."""
        card = ctk.CTkFrame(parent, fg_color="#333333", corner_radius=12, height=100)
        ctk.CTkLabel(card, text=title, font=("Arial", 13), text_color="gray").pack(pady=(15, 0))
        ctk.CTkLabel(card, text=value, font=("Arial", 20, "bold"), text_color=color).pack(pady=(5, 15))
        return card

    # --- Core Functionality ---

    def add_expense(self):
        amount = self.amount_entry.get()
        t_type = self.type_var.get()
        
        category = self.category_combo.get() if t_type == "Expense" else "Income/Salary"
        desc = self.desc_entry.get()

        if not amount:
            messagebox.showwarning("Error", "Please enter an amount")
            return

        try:
            user_id = self.controller.current_user_id
        
            new_tx = Transaction(None, float(amount), category, desc, t_type)
            
            self.budget_manager.add_transaction(user_id, new_tx)
            
            self.amount_entry.delete(0, 'end')
            self.desc_entry.delete(0, 'end')
            self.refresh_ui()
        except ValueError:
            messagebox.showerror("Error", "Invalid amount")
            
    def remove_expense(self):
        selected_item = self.tree.selection()
        
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a transaction to delete.")
            return

        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this?")
        if confirm:
            # 1. Pull the hidden database ID from the tags
            db_id = self.tree.item(selected_item[0])['tags'][0]
            
            # 2. Tell the manager to delete by ID
            self.budget_manager.db.delete_transaction(db_id)
            
            # 3. Refresh
            self.refresh_ui()
    
    def refresh_ui(self):
        """Updates data depending on which view is currently active with modern styling."""
        user_id = self.controller.current_user_id
        if not user_id: return
        
        self.budget_manager.load_user_data(user_id)
        
        if self.current_view == "history":
            # 1. Clear current table data
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            # 2. Configure visual tags for colors (if not already set in show_history_view)
            self.tree.tag_configure('income_text', foreground='#2ecc71') # Modern Green
            self.tree.tag_configure('expense_text', foreground='#e74c3c') # Modern Red
            self.tree.tag_configure('oddrow', background='#333333')
            self.tree.tag_configure('evenrow', background='#2b2b2b')
            
            # 3. Re-fill Table with enhanced logic
            for i, tx in enumerate(self.budget_manager.transactions):
                # Calculate zebra stripe tag
                stripe_tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                
                # Determine text color tag based on type
                type_tag = 'income_text' if tx.type == "Income" else 'expense_text'
                
                # Formatting the display
                prefix = "+" if tx.type == "Income" else "-"
                display_amt = f"{prefix}${tx.amount:.2f}"
                
                # Insert with combined tags
                # First tag is always the DB ID, others are for styling
                # Change this line inside your loop in refresh_ui:
                self.tree.insert("", "end", 
                                values=(display_amt, tx.category, tx.type, tx.date),
                                # Add tx.description to the tags here!
                                tags=(tx.db_id, tx.description, stripe_tag, type_tag))
            
            # 4. Update Balance Label
            bal = self.budget_manager.calculate_balance()
            self.total_label.configure(text=f"Balance: ${bal:.2f}", 
                                        text_color="#2ecc71" if bal >= 0 else "#e74c3c")
            
        elif self.current_view == "analytics":
            # Ensure visualizer uses the updated transaction list
            self.visualizer.draw_chart(self.visualizer.current_chart_type)
            
    def export_to_excel(self):
        """Converts current transaction history into an Excel spreadsheet."""
        # 1. Check if there is actually data to export
        if not self.budget_manager.transactions:
            messagebox.showwarning("Export", "No transactions found to export.")
            return

        # 2. Ask user where to save the file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile="My_Expenses.xlsx"
        )
        
        if not file_path:
            return

        try:
            # 3. Convert your list of Transaction objects into a list of dictionaries
            data = [t.to_dict() for t in self.budget_manager.transactions]
            
            # 4. Create DataFrame and clean up columns for the user
            df = pd.DataFrame(data)
            
            # Rename columns to look professional in Excel
            df = df.rename(columns={
                "amount": "Amount ($)",
                "category": "Category",
                "description": "Description",
                "type": "Type",
                "date": "Date & Time"
            })
            
            # Drop the internal database ID so the user doesn't see it
            if "db_id" in df.columns:
                df = df.drop(columns=["db_id"])

            # 5. Save to Excel
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Export Success", f"File saved successfully at:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred: {e}")
            
    def handle_edit_transaction(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Required", "Please select a transaction to edit.")
            return

        # 1. Pull data from Treeview
        # Columns: 0:Amount, 1:Category, 2:Type, 3:Date
        item_data = self.tree.item(selected_item[0])
        val = item_data['values']
        tags = item_data['tags']
        
        db_id = tags[0]
        existing_desc = tags[1] # Assumes you updated refresh_ui to store desc in tags

        # 2. Window Setup
        edit_win = ctk.CTkToplevel(self)
        edit_win.title("Edit Transaction")
        edit_win.geometry("400x600")
        edit_win.attributes("-topmost", True)

        # --- Description ---
        ctk.CTkLabel(edit_win, text="Description:").pack(pady=(20, 0))
        desc_entry = ctk.CTkEntry(edit_win, width=300)
        desc_entry.insert(0, existing_desc)
        desc_entry.pack(pady=5)

        # --- Amount (Numeric Validation) ---
        ctk.CTkLabel(edit_win, text="Amount:").pack()
        amount_entry = ctk.CTkEntry(edit_win, width=300)
        # Strip prefixes for the entry box
        clean_amt = str(val[0]).replace("$", "").replace("+", "").replace("-", "").strip()
        amount_entry.insert(0, clean_amt)
        amount_entry.pack(pady=5)

        # --- Category ---
        ctk.CTkLabel(edit_win, text="Category:").pack()
        category_dropdown = ctk.CTkComboBox(edit_win, values=["Food", "Rent", "Transport", "Entertainment", "Other"], width=300)
        category_dropdown.set(val[1])
        category_dropdown.pack(pady=5)

        # --- Type ---
        ctk.CTkLabel(edit_win, text="Type:").pack()
        type_dropdown = ctk.CTkComboBox(edit_win, values=["Expense", "Income"], width=300)
        type_dropdown.set(val[2])
        type_dropdown.pack(pady=5)

        # Logic: If initially Income, lock category
        if val[2] == "Income":
            category_dropdown.set("Income/Salary")
            category_dropdown.configure(state="disabled")

        def on_type_change(choice):
            if choice == "Income":
                category_dropdown.set("Income/Salary")
                category_dropdown.configure(state="disabled")
            else:
                category_dropdown.configure(state="normal")
                # Don't overwrite if it was already an expense category
                if category_dropdown.get() == "Income/Salary":
                    category_dropdown.set("Other")

        type_dropdown.configure(command=on_type_change)

        def save_changes():
            # 1. Recheck Amount for Alpha characters
            raw_amt = amount_entry.get().strip()
            try:
                # This check prevents letters from being saved
                final_amt = float(raw_amt)
                if final_amt < 0:
                    messagebox.showerror("Error", "Amount cannot be negative.")
                    return
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a number only for the amount.")
                return

            # 2. Recheck Income Logic
            final_type = type_dropdown.get()
            final_cat = "Income/Salary" if final_type == "Income" else category_dropdown.get()

            try:
                # 3. Create the object for the Database
                updated_t = Transaction(
                    db_id=db_id,
                    amount=final_amt,
                    category=final_cat,
                    description=desc_entry.get(),
                    t_type=final_type,
                    date=val[3] # Preserves original timestamp
                )

                # 4. Push to DB
                self.budget_manager.db.update_transaction(updated_t)
                messagebox.showinfo("Success", "Transaction updated successfully!")
                self.refresh_ui()
                edit_win.destroy()
            except Exception as e:
                messagebox.showerror("System Error", f"Could not update: {e}")

        ctk.CTkButton(edit_win, text="Save Changes", fg_color="#2ecc71", 
                      hover_color="#27ae60", command=save_changes).pack(pady=30)