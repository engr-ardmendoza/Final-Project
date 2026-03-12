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

        self.add_btn = ctk.CTkButton(input_box, text="Add Transaction", command=self.add_expense)
        self.add_btn.pack(pady=5, fill="x")
        self.delete_btn = ctk.CTkButton(input_box, text="Delete Transaction", fg_color="#D32F2F", command=self.remove_expense)
        self.edit_btn = ctk.CTkButton(input_box, text="Edit Transaction", command=self.handle_edit_transaction)
        
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
        self.tree.bind("<Delete>", lambda event: self.remove_expense())
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Button-1>", self.handle_click_outside)
        self.tree.bind("<Escape>", lambda e: self.clear_selection())
        
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
        amount_raw = self.amount_entry.get()
        t_type = self.type_var.get()
        
        category = self.category_combo.get() if t_type == "Expense" else "Income/Salary"
        desc = self.desc_entry.get()

        if not amount_raw:
            messagebox.showwarning("Error", "Please enter an amount")
            return
        
        if self.category_combo.get() == "Select Category" and t_type == "Expense":
            messagebox.showwarning("Error", "Please select what type of Expense is this")
            return

        try:
            amount = float(amount_raw)
            # --- NEW VALIDATION ---
            if amount <= 0:
                messagebox.showwarning("Error", "Amount must be a positive number")
                return
            # ----------------------

            user_id = self.controller.current_user_id
            new_tx = Transaction(None, amount, category, desc, t_type)
            
            self.budget_manager.add_transaction(user_id, new_tx)
            
            self.amount_entry.delete(0, 'end')
            self.desc_entry.delete(0, 'end')
            self.refresh_ui()
        except ValueError:
            messagebox.showerror("Error", "Invalid amount. Please enter a valid number.")
            
    def remove_expense(self):
        try: 
            selected_item = self.tree.selection()
            if not selected_item:
                messagebox.showwarning("Selection Error", "Please select a transaction to delete")
                return

            confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this?")
            if confirm:
                # 1. Pull the hidden database ID from the tags
                db_id = self.tree.item(selected_item[0])['tags'][0]
                
                # 2. Tell the manager to delete by ID
                self.budget_manager.db.delete_transaction(db_id)
                
                # 3. Refresh
                self.refresh_ui()
                
                # FORCE HIDE after deletion
                self.edit_btn.pack_forget()
                self.delete_btn.pack_forget()
                
        except ValueError:
            messagebox.showerror("Selection Error", "Please select a transaction to delete")
    
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
            if hasattr(self, 'visualizer'):
                # Use a default "Pie" just in case current_chart_type is missing
                chart = getattr(self.visualizer, 'current_chart_type', "Pie")
                self.visualizer.draw_chart(chart)
            
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
            
    def on_tree_select(self, event=None):
        selected = self.tree.selection()
        
        if selected:
            item_data = self.tree.item(selected[0])
            val = item_data['values']
            tags = item_data['tags']
            
            # 1. Store the Database ID (stored in the first tag)
            self.editing_id = tags[0] 
            
            # 2. Clean the amount (remove $ and +/-)
            clean_amt = str(val[0]).replace("$", "").replace("+", "").replace("-", "").strip()
            
            # 3. Auto-fill the sidebar fields
            self.amount_entry.delete(0, 'end')
            self.amount_entry.insert(0, clean_amt)
            
            # Tags[1] is the description we passed in refresh_ui
            self.desc_entry.delete(0, 'end')
            self.desc_entry.insert(0, tags[1] if len(tags) > 1 else "") 
            
            self.type_var.set(val[2])
            self.toggle_inputs(val[2])
            
            if val[2] == "Expense":
                self.category_combo.set(val[1])

            # 4. Show Edit/Delete buttons (they only appear when a row is clicked)
            # 1. SWAP BUTTONS: Hide Add, Show Edit/Delete
            self.add_btn.pack_forget() 
            self.edit_btn.pack(pady=5, fill="x", after=self.desc_entry)
            self.delete_btn.pack(pady=5, fill="x", after=self.edit_btn)
        else:
            # Nothing selected? Reset UI
            self.editing_id = None
            self.clear_sidebar_fields()

    def handle_edit_transaction(self):
        if not self.editing_id:
            messagebox.showwarning("Selection Required", "Please select a transaction.")
            return

        try:
            amount = float(self.amount_entry.get())
            t_type = self.type_var.get()
            category = self.category_combo.get() if t_type == "Expense" else "Income/Salary"
            description = self.desc_entry.get()
            
            # Preserve the original date from the table
            selected_item = self.tree.selection()[0]
            original_date = self.tree.item(selected_item)['values'][3]

            updated_tx = Transaction(
                db_id=self.editing_id,
                amount=amount,
                category=category,
                description=description,
                t_type=t_type,
                date=original_date
            )

            self.budget_manager.db.update_transaction(updated_tx)
            messagebox.showinfo("Success", "Transaction updated!")
            
            self.refresh_ui()
            self.clear_sidebar_fields()
            
        except ValueError:
            messagebox.showerror("Error", "Invalid amount. Please enter a number.")
            
    def handle_click_outside(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region == "nothing":
            self.tree.selection_remove(self.tree.selection())
            self.on_tree_select() # This resets the sidebar

    def clear_sidebar_fields(self):
        self.amount_entry.delete(0, 'end')
        self.desc_entry.delete(0, 'end')
        self.category_combo.set("Select Category")
        
        # 1. Hide the Edit and Delete buttons first
        self.edit_btn.pack_forget()
        self.delete_btn.pack_forget()
        
        # 2. Pack the Add button relative to the Description entry 
        # (Since desc_entry is always visible, this won't crash)
        self.add_btn.pack(pady=5, fill="x", after=self.desc_entry)