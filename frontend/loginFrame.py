import tkinter as tk
import customtkinter as ctk  # type: ignore
from tkinter import messagebox
from PIL import Image # type: ignore
import os

class LoginFrame(ctk.CTkFrame):
    """
    The entry point of the application. 
    Provides a split-screen interface for user authentication.
    """
    def __init__(self, parent, controller, budget_manager):
        # Set main background to the standard dark theme (#1a1a1a)
        super().__init__(parent, fg_color="#1a1a1a")
        self.controller = controller
        self.budget_manager = budget_manager

        # --- STATE ---
        self.password_visible = False # Track whether password is shown or masked

        # Configure 1x2 grid for a 50/50 split-screen layout
        self.grid_columnconfigure(0, weight=1) # Left side (Branding)
        self.grid_columnconfigure(1, weight=1) # Right side (Form)
        self.grid_rowconfigure(0, weight=1)

        # --- LEFT SIDE: BRANDING ---
        # Darker background (#111111) to provide visual depth
        self.left_side = ctk.CTkFrame(self, fg_color="#111111", corner_radius=0)
        self.left_side.grid(row=0, column=0, sticky="nsew")
        
        # Centered container for logo and company text
        self.brand_container = ctk.CTkFrame(self.left_side, fg_color="transparent")
        self.brand_container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo Loading Logic
        try:
            base_path = os.path.dirname(os.path.realpath(__file__))
            logo_path = os.path.join(base_path, "assets", "company_logo.png")
            my_logo = ctk.CTkImage(
                light_image=Image.open(logo_path),
                dark_image=Image.open(logo_path),
                size=(150,100) 
            )
            logo_label = ctk.CTkLabel(self.brand_container, image=my_logo, text="")
            logo_label.pack(pady=20)
        except Exception:
            # Fallback text if logo file is missing
            ctk.CTkLabel(self.brand_container, text="X", font=("Arial", 80)).pack(pady=20)
        
        ctk.CTkLabel(self.brand_container, text="SyntaxSpend", font=("Arial", 40, "bold"), text_color="#3498db").pack(pady=10)
        ctk.CTkLabel(self.brand_container, text="You Imagine, We Innovate\nTkinterThinkers", 
                     font=("Arial", 16), text_color="white", justify="center").pack()

        # --- RIGHT SIDE: LOGIN FORM ---
        self.right_side = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=0)
        self.right_side.grid(row=0, column=1, sticky="nsew")

        # The Login Card (Centralized box)
        self.box = ctk.CTkFrame(self.right_side, width=380, height=520, fg_color="#111111", corner_radius=15)
        self.box.place(relx=0.5, rely=0.5, anchor="center")
        self.box.pack_propagate(False)

        ctk.CTkLabel(self.box, text="Login", font=("Arial", 32, "bold"), text_color="white").pack(pady=(50, 30))

        # Reusable dictionary for consistent input field styling
        field_style = {
            "width": 300, "height": 50, "fg_color": "#1a1a1a",
            "border_color": "#2d2d2d", "border_width": 1,
            "corner_radius": 8, "text_color": "white"
        }

        # --- Username Entry ---
        ctk.CTkLabel(self.box, text="Username", font=("Arial", 16), text_color="#3498db").pack(anchor ="w", padx=40)
        self.user_entry = ctk.CTkEntry(self.box, placeholder_text="Enter username", **field_style)
        self.user_entry.pack(pady=10)

        # --- Password Entry ---
        ctk.CTkLabel(self.box, text="Password", font=("Arial", 16), text_color="#3498db").pack(anchor ="w", padx=40)
        self.pass_entry = ctk.CTkEntry(self.box, placeholder_text="Enter password", show="*", **field_style)
        self.pass_entry.pack(pady=(10, 0))

        # --- Visibility Toggle Button ---
        self.toggle_btn = ctk.CTkButton(
            self.box, 
            text="👁 Show Password", 
            font=("Arial", 11),
            fg_color="transparent", 
            text_color="gray60",
            hover_color="#1a1a1a",
            width=100,
            height=20,
            command=self.toggle_password_visibility
        )
        self.toggle_btn.pack(pady=(5, 10), anchor="e", padx=40)

        # --- Login and Navigation Buttons ---
        self.login_btn = ctk.CTkButton(
            self.box, text="Login", width=300, height=50, 
            font=("Arial", 16, "bold"), fg_color="#3498db", 
            hover_color="#2980b9", command=self.handle_login
        )
        self.login_btn.pack(pady=(20, 10))

        ctk.CTkButton(
            self.box, text="Create an account", fg_color="transparent", 
            text_color="#3498db", hover_color="#1a1a1a",
            command=lambda: controller.show_frame("RegisterFrame")
        ).pack()

    def toggle_password_visibility(self):
        """Switches the password entry between masked symbols and plain text."""
        if self.password_visible:
            self.pass_entry.configure(show="*")
            self.toggle_btn.configure(text="👁 Show Password")
            self.password_visible = False
        else:
            self.pass_entry.configure(show="")
            self.toggle_btn.configure(text="👁 Hide Password")
            self.password_visible = True

    def handle_login(self):
        """Processes authentication and routes the user based on their access level (Admin vs User)."""
        user = self.user_entry.get().strip()
        pw = self.pass_entry.get().strip()
        
        # Verify credentials against database
        result = self.budget_manager.db.login_user(user, pw)
        
        if result:
            user_id, is_admin = result
            # Store the logged-in user's ID globally in the GUI controller
            self.controller.current_user_id = user_id
            
            # Route to appropriate dashboard
            if is_admin == 1: 
                self.controller.show_frame("AdminFrame")
            else: 
                self.controller.show_frame("DashboardFrame")
        else:
            messagebox.showerror("Error", "Invalid username or password.")
            
    def clear_fields(self):
        """Resets the form to a blank state. Triggered by controller when showing the frame."""
        self.user_entry.delete(0, 'end')
        self.pass_entry.delete(0, 'end')
        
        # Ensure password masking is reset to 'Hidden'
        self.password_visible = True
        self.toggle_password_visibility()