import customtkinter as ctk # type: ignore
from tkinter import messagebox, ttk
from PIL import Image # type: ignore
import os

class AdminFrame(ctk.CTkFrame):
    """
    Main Administrative interface providing user management, 
    privilege escalation, and security override tools.
    """
    def __init__(self, parent, controller, budget_manager):
        # Initialize the frame with a specific dark background color
        super().__init__(parent, fg_color="#1a1a1a") 
        self.controller = controller
        self.budget_manager = budget_manager

        # Layout Configuration: Column 0 (Sidebar) is fixed, Column 1 (Content) expands
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- 1. SIDEBAR NAVIGATION ---
        # Sidebar uses a deep dark color (#111111) to distinguish it from main content
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#111111")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False) # Prevents sidebar from shrinking to fit buttons

        # Logo Branding logic: Tries to load company_logo.png from assets folder
        base_path = os.path.dirname(os.path.realpath(__file__))
        logo_path = os.path.join(base_path, "assets", "company_logo.png")
        
        try:
            my_logo = ctk.CTkImage(
                light_image=Image.open(logo_path),
                dark_image=Image.open(logo_path),
                size=(150,100)
            )
            logo_label = ctk.CTkLabel(self.sidebar, image=my_logo, text="")
            logo_label.pack(pady=20)
        except Exception:
            # Fallback if image fails to load
            ctk.CTkLabel(self.sidebar, text="ADMIN", font=("Arial", 24, "bold"), text_color="#3498db").pack(pady=20)

        # Sidebar Navigation Buttons Styling
        nav_style = {"fg_color": "transparent", "text_color": "gray80", "hover_color": "#2d2d2d", "anchor": "w"}
        
        # Navigation buttons to switch between internal panels
        ctk.CTkButton(self.sidebar, text="User Database", command=lambda: self.show_panel("database"), **nav_style).pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(self.sidebar, text="Manage Access", command=lambda: self.show_panel("access"), **nav_style).pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(self.sidebar, text="Reset Password", command=lambda: self.show_panel("password"), **nav_style).pack(fill="x", padx=20, pady=5)
        
        # --- SIDEBAR EXIT SECTION ---
        # Lower grouped buttons for Dashboard return and Logout
        self.exit_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.exit_container.pack(side="bottom", fill="x", pady=20)

        ctk.CTkButton(
            self.exit_container, 
            text="Back to Dashboard", 
            fg_color="#2d2d2d", 
            hover_color="#3d3d3d",
            command=lambda: self.controller.show_frame("DashboardFrame") 
        ).pack(fill="x", padx=20, pady=5)

        ctk.CTkButton(
            self.exit_container, 
            text="Logout", 
            fg_color="#A12222", 
            hover_color="#801b1b",
            command=lambda: self.controller.show_frame("LoginFrame")
        ).pack(fill="x", padx=20, pady=5)

        # --- 2. MAIN CONTENT VIEW ---
        # This area acts as a dynamic canvas where different panels are swapped
        self.main_view = ctk.CTkFrame(self, fg_color="transparent")
        self.main_view.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.main_view.grid_columnconfigure(0, weight=1)
        
        # Dictionary to store references to panels for easy toggling
        self.panels = {}
        self.init_panels()
        
        # Set the default view on startup
        self.show_panel("database")

    def init_panels(self):
        """Initializes all sub-panels (Database, Access, Password) within the main view."""
        
        # --- PANEL A: USER DATABASE ---
        db_panel = ctk.CTkFrame(self.main_view, fg_color="transparent")
        
        # 1. Stats Ribbon (Summary cards at the top)
        self.stats_ribbon = ctk.CTkFrame(db_panel, fg_color="transparent")
        self.stats_ribbon.pack(fill="x", pady=(0, 20))
        self.stats_ribbon.grid_columnconfigure((0, 1, 2), weight=1)
        self.render_stats(0, 0) 

        # 2. Main Database Content (Split between Table and Side Log)
        db_container = ctk.CTkFrame(db_panel, fg_color="transparent")
        db_container.pack(fill="both", expand=True)
        db_container.grid_columnconfigure(0, weight=4) # Left side (Table)
        db_container.grid_columnconfigure(1, weight=1) # Right side (Preview Log)

        # Left Column: Search Bar + Treeview Table
        table_section = ctk.CTkFrame(db_container, fg_color="transparent")
        table_section.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

        search_frame = ctk.CTkFrame(table_section, fg_color="#1a1c24", height=50)
        search_frame.pack(fill="x", pady=(0, 10))
        search_frame.pack_propagate(False)
        
        ctk.CTkLabel(search_frame, text=" 🔍 ", font=("Arial", 18)).pack(side="left", padx=10)
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Filter database by username...", 
                                        fg_color="transparent", border_width=0, font=("Arial", 14))
        self.search_entry.pack(side="left", fill="both", expand=True)
        # Search input binding to refresh the table instantly
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_ui(self.search_entry.get()))

        table_card = ctk.CTkFrame(table_section, fg_color="#1a1c24", corner_radius=15)
        table_card.pack(fill="both", expand=True)
        self.setup_treeview(table_card)

        # Right Column: Mini Activity Log for a quick overview
        side_log_card = ctk.CTkFrame(db_container, fg_color="#1a1c24", corner_radius=15)
        side_log_card.grid(row=0, column=1, sticky="nsew")
        
        ctk.CTkLabel(side_log_card, text="Recent Activity", font=("Arial", 16, "bold")).pack(pady=15)
        self.side_activity_log = ctk.CTkTextbox(side_log_card, fg_color="transparent", font=("Consolas", 11), text_color="gray80")
        self.side_activity_log.pack(fill="both", expand=True, padx=10, pady=10)
        self.side_activity_log.configure(state="disabled")
        
        self.panels["database"] = db_panel

        # --- PANEL B: ACCESS & MONITORING ---
        access_panel = ctk.CTkFrame(self.main_view, fg_color="transparent")
        
        ctk.CTkLabel(access_panel, text="Access Control & System Logs", 
                     font=("Arial", 26, "bold")).pack(anchor="w", pady=(0, 20))

        # Role Management Cards (Top half of panel)
        cards_container = ctk.CTkFrame(access_panel, fg_color="transparent")
        cards_container.pack(fill="x", pady=(0, 15))
        cards_container.grid_columnconfigure((0, 1), weight=1)

        # Iteratively create Promote and Demote cards
        for i, (title, color, drop_attr, btn_text, cmd) in enumerate([
            ("Promote User", "#2ecc71", "promo_dropdown", "Grant Admin", self.handle_promotion),
            ("Demote User", "#e74c3c", "demote_dropdown", "Revoke Admin", self.handle_demotion)
        ]):
            card = ctk.CTkFrame(cards_container, fg_color="#1a1c24", corner_radius=15, border_width=1, border_color="#3d3d3d")
            card.grid(row=0, column=i, padx=(0 if i==1 else 10, 10 if i==0 else 0), sticky="nsew")
            
            ctk.CTkLabel(card, text=title, font=("Arial", 20, "bold"), text_color=color).pack(pady=20)
            dropdown = ctk.CTkComboBox(card, values=[], width=300, height=40, state="readonly")
            dropdown.pack(pady=10)
            setattr(self, drop_attr, dropdown) # Link dropdown to class attribute
            ctk.CTkButton(card, text=btn_text, fg_color=color, hover_color="#222222", 
                          height=45, width=200, font=("Arial", 14, "bold"), command=cmd).pack(pady=25)

        # Detailed Audit Log (Bottom half of panel, fills remaining space)
        log_full_card = ctk.CTkFrame(access_panel, fg_color="#1a1c24", corner_radius=15, border_width=1, border_color="#3d3d3d")
        log_full_card.pack(fill="both", expand=True)
        
        ctk.CTkLabel(log_full_card, text="Detailed System Audit Log", 
                     font=("Arial", 16, "bold")).pack(pady=10, anchor="w", padx=20)
        
        self.activity_log = ctk.CTkTextbox(log_full_card, fg_color="#111111", corner_radius=10, font=("Consolas", 12))
        self.activity_log.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.activity_log.configure(state="disabled")

        self.panels["access"] = access_panel

        # --- PANEL C: RESET PASSWORD ---
        pw_panel = ctk.CTkFrame(self.main_view, fg_color="transparent")
        pw_card = ctk.CTkFrame(pw_panel, fg_color="#1a1c24", corner_radius=15, border_width=1, border_color="#3d3d3d")
        pw_card.place(relx=0.5, rely=0.4, anchor="center") # Centered card layout

        ctk.CTkLabel(pw_card, text="Security Override", font=("Arial", 22, "bold"), text_color="#3498db").pack(pady=(30, 20), padx=50)
        self.pw_dropdown = ctk.CTkComboBox(pw_card, values=[], width=350, height=40, state="readonly")
        self.pw_dropdown.pack(pady=10, padx=50)
        self.new_pw_entry = ctk.CTkEntry(pw_card, placeholder_text="New Password", width=350, height=45, show="*")
        self.new_pw_entry.pack(pady=10, padx=50)
        ctk.CTkButton(pw_card, text="Update", fg_color="#3498db", command=self.handle_password_reset, height=45, width=350).pack(pady=(20, 30))
        
        self.panels["password"] = pw_panel
        
    def show_panel(self, name):
        """Switches the visible panel by forgetting all others and packing the chosen one."""
        for panel in self.panels.values():
            panel.pack_forget()
        self.panels[name].pack(fill="both", expand=True)
        self.refresh_ui()

    def setup_treeview(self, parent):
        """Sets up and styles the Tkinter Treeview to match the modern theme."""
        style = ttk.Style()
        style.theme_use("default")
        
        # Table body styling
        style.configure("Treeview", 
                        background="#1a1c24", 
                        foreground="white", 
                        fieldbackground="#1a1c24", 
                        rowheight=40, 
                        borderwidth=0)
        
        # Column Header styling
        style.configure("Treeview.Heading", 
                        background="#2d303a", 
                        foreground="white", 
                        relief="flat", 
                        font=("Arial", 12, "bold"))
        
        style.map("Treeview", background=[('selected', '#3498db')])

        cols = ("User ID", "Username", "Is Admin")
        self.tree = ttk.Treeview(parent, columns=cols, show="headings", style="Treeview")
        
        for col in cols:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, anchor="center", width=150)
        
        self.tree.pack(fill="both", expand=True, padx=15, pady=15)

    def refresh_ui(self, filter_text=""):
        """
        Synchronizes the UI with the latest database records.
        Refreshes the table, stats, and all selection dropdowns.
        """
        try:
            # Clear existing data from table
            self.tree.delete(*self.tree.get_children())
            
            # Fetch user list from DB
            users_data = self.budget_manager.db.get_all_users_basic() 
            
            all_usernames = []
            promote_list = [] # Users who can be promoted
            demote_list = []  # Users who can be demoted
            
            total_users = len(users_data)
            total_admins = 0

            for u_id, u_name, is_admin in users_data:
                all_usernames.append(str(u_name))
                
                # Logic for status labels and list sorting
                if is_admin == 1:
                    total_admins += 1
                    demote_list.append(str(u_name))
                    admin_status = "Yes"
                else:
                    promote_list.append(str(u_name))
                    admin_status = "No"
                
                # Apply search filter and insert into UI
                if filter_text.lower() in u_name.lower():
                    self.tree.insert("", "end", values=(u_id, u_name, admin_status))
            
            # Update Dashboard visuals and dynamic dropdowns
            self.render_stats(total_users, total_admins)
            self.promo_dropdown.configure(values=promote_list) 
            self.demote_dropdown.configure(values=demote_list) 
            self.pw_dropdown.configure(values=all_usernames) 
            
        except Exception as e:
            print(f"Admin Refresh Error: {e}")
        
    def handle_promotion(self):
        """Grants admin privileges to a selected user."""
        user = self.promo_dropdown.get()
        if user and messagebox.askyesno("Confirm", f"Grant Admin to {user}?"):
            self.budget_manager.db.promote_to_admin(user)
            messagebox.showinfo("Success", f"{user} is now an Admin!")
            
    def handle_demotion(self):
        """Revokes admin privileges. Prevents master user from being demoted."""
        user = self.demote_dropdown.get() 
        
        if user.lower() == "ralph":
            messagebox.showwarning("Restricted", "You cannot demote the master admin account.")
            return

        if user and messagebox.askyesno("Confirm", f"Remove Administration Access from {user}?"):
            self.budget_manager.db.demote_to_user(user)
            messagebox.showinfo("Success", f"{user} is no longer an Admin!")
            self.refresh_ui()

    def handle_password_reset(self):
        """Updates a user's password directly via administrative override."""
        user = self.pw_dropdown.get()
        new_pw = self.new_pw_entry.get()

        if not user or user == "Select User": # Basic validation
            messagebox.showwarning("Input Error", "Please select a user.")
            return

        if not new_pw:
            messagebox.showwarning("Input Error", "Please enter a new password.")
            return

        # 1. Capture the success status and the message from the DB method
        success, message = self.budget_manager.db.reset_password(user, new_pw)

        if success:
            messagebox.showinfo("Success", message)
            self.new_pw_entry.delete(0, 'end')
        else:
            # 2. Show the specific validation error (e.g., "Password too short")
            messagebox.showerror("Validation Error", message)

    def handle_delete(self):
        """Deletes a user account. Prevents deletion of the master account."""
        item = self.tree.selection()
        if not item: return
        
        val = self.tree.item(item)['values']
        
        if str(val[1]).lower() == "ralph": 
            messagebox.showwarning("Restricted", "This primary account cannot be deleted.")
            return
            
        if messagebox.askyesno("Delete", f"Permanently delete {val[1]}?"):
            self.budget_manager.db.delete_user(val[0])
            self.refresh_ui()

    def clear_fields(self):
        """Wipes input fields and refreshes data."""
        self.new_pw_entry.delete(0, 'end')
        self.refresh_ui()
        
    def create_stat_card(self, parent, title, value, color):
        """Helper to create stylized statistical boxes."""
        card = ctk.CTkFrame(parent, fg_color="#1a1c24", corner_radius=12)
        ctk.CTkLabel(card, text=title, font=("Arial", 13), text_color="gray70").pack(pady=(15, 0))
        ctk.CTkLabel(card, text=value, font=("Arial", 22, "bold"), text_color=color).pack(pady=(5, 15))
        return card

    def render_stats(self, user_count, admin_count):
        """Redraws the ribbon cards with updated user/admin totals."""
        for widget in self.stats_ribbon.winfo_children():
            widget.destroy()

        self.create_stat_card(self.stats_ribbon, "Total Users", str(user_count), "white").grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        self.create_stat_card(self.stats_ribbon, "System Admins", str(admin_count), "#3498db").grid(row=0, column=1, padx=10, sticky="nsew")
        self.create_stat_card(self.stats_ribbon, "System Status", "Online", "#2ecc71").grid(row=0, column=2, padx=(10, 0), sticky="nsew")
        
    def log_activity(self, action, user):
        """Appends an administrative event to both internal logs with a timestamp."""
        from datetime import datetime
        time_str = datetime.now().strftime("%H:%M:%S")
        message = f"[{time_str}] {action.upper()} - {user}\n"
        
        for log in [self.activity_log, self.side_activity_log]:
            log.configure(state="normal")
            log.insert("0.0", message)
            log.configure(state="disabled")

    def update_system_status(self, is_online=True):
        """Updates the health indicator label (if defined)."""
        color = "#2ecc71" if is_online else "#e74c3c"
        text = "OK" if is_online else "ERROR"
        # Note: Ensure self.db_status is initialized before calling this
        self.db_status.configure(text=f"● DB Connection: {text}", text_color=color)