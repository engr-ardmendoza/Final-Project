import tkinter as tk
import customtkinter as ctk  # type: ignore
from tkinter import messagebox
from PIL import Image # type: ignore
import os

class RegisterFrame(ctk.CTkFrame):
    """
    Opposite Split-Screen Registration UI.
    Left Side: Form box for user input.
    Right Side: Promotional/Branding text.
    """
    def __init__(self, parent, controller, budget_manager): 
        # Set main background to match the dark theme (#1a1a1a)
        super().__init__(parent, fg_color="#1a1a1a")
        self.controller = controller
        self.budget_manager = budget_manager

        # Configure grid for 50/50 split
        self.grid_columnconfigure(0, weight=1) # Left side (Form)
        self.grid_columnconfigure(1, weight=1) # Right side (Words)
        self.grid_rowconfigure(0, weight=1)

        # --- LEFT SIDE: THE BOX ---
        self.left_side = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=0)
        self.left_side.grid(row=0, column=0, sticky="nsew")

        # Registration Card
        self.box = ctk.CTkFrame(self.left_side, width=400, height=520, fg_color="#111111", corner_radius=15)
        self.box.place(relx=0.5, rely=0.5, anchor="center")
        self.box.pack_propagate(False) # Maintains fixed size

        ctk.CTkLabel(self.box, text="Create Account", font=("Arial", 32, "bold"), text_color="white").pack(pady=(50, 30))

        # Reusable field styling
        field_style = {
            "width": 300,
            "height": 50,
            "fg_color": "#1a1a1a",
            "border_color": "#2d2d2d",
            "border_width": 1,
            "corner_radius": 8,
            "text_color": "white"
        }

        ctk.CTkLabel(self.box, text="Username", font=("Arial", 16), text_color="#3498db").pack(anchor ="w", padx=50)
        self.user_entry = ctk.CTkEntry(self.box, placeholder_text="", **field_style)
        self.user_entry.pack(pady=10)

        ctk.CTkLabel(self.box, text="Password", font=("Arial", 16), text_color="#3498db").pack(anchor ="w", padx=50)
        self.pass_entry = ctk.CTkEntry(self.box, placeholder_text="", show="*", **field_style)
        self.pass_entry.pack(pady= (10, 0))
        
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

        # Requirements Helper Text
        ctk.CTkLabel(
            self.box, 
            text="Min 8 chars, 1 Uppercase, 1 Number, 1 Symbol", 
            font=("Arial", 11), 
            text_color="gray50"
        ).pack(pady=5)

        # Sign Up Button
        ctk.CTkButton(
            self.box, 
            text="Sign Up", 
            width=300,
            height=50,
            font=("Arial", 16, "bold"),
            fg_color="#3498db", 
            hover_color="#2980b9",
            command=self.handle_register
        ).pack(pady=(20, 10))
        
        # Back to Login
        ctk.CTkButton(
            self.box, 
            text="Back to Login", 
            fg_color="transparent", 
            text_color="#3498db",
            hover_color="#1a1a1a",
            command=lambda: controller.show_frame("LoginFrame")
        ).pack(pady=5)

        # --- RIGHT SIDE: THE WORDS ---
        self.right_side = ctk.CTkFrame(self, fg_color="#111111", corner_radius=0)
        self.right_side.grid(row=0, column=1, sticky="nsew")
        
        # Centered branding container
        self.brand_container = ctk.CTkFrame(self.right_side, fg_color="transparent")
        self.brand_container.place(relx=0.5, rely=0.5, anchor="center")

        base_path = os.path.dirname(os.path.realpath(__file__))
        logo_path = os.path.join(base_path, "assets", "company_logo.png")
        
        my_logo = ctk.CTkImage(
            light_image=Image.open(logo_path),
            dark_image=Image.open(logo_path),
            size=(150,100) # Adjust dimensions here
        )
        
        logo_label = ctk.CTkLabel(self.brand_container, image=my_logo, text="") # text="" removes the default label text
        logo_label.pack(pady=20)

        ctk.CTkLabel(
            self.brand_container, 
            text="Join the Journey", 
            font=("Arial", 40, "bold"), 
            text_color="#3498db"
        ).pack(pady=10)

        ctk.CTkLabel(
            self.brand_container, 
            text="Take control of your financial future today.\nSet budgets, track habits, and grow.", 
            font=("Arial", 16), 
            text_color="gray60",
            justify="center"
        ).pack()

    def handle_register(self):
        """Processes input and attempts to register a new user via the backend."""
        user = self.user_entry.get().strip()
        pw = self.pass_entry.get().strip()
        
        # 1. Basic validation check
        if not user or not pw:
            messagebox.showwarning("Error", "Fields cannot be empty")
            return

        # 2. Database interaction (Logic from your original file preserved)
        success, message = self.budget_manager.db.register_user(user, pw)
        
        if success:
            messagebox.showinfo("Success", message)
            self.controller.show_frame("LoginFrame") 
        else:
            # Displays specific password complexity errors from PasswordValidation
            messagebox.showerror("Signup Failed", message)
            
    def clear_fields(self):
        """Resets the form to a blank state. Triggered by controller when showing the frame."""
        self.user_entry.delete(0, 'end')
        self.pass_entry.delete(0, 'end')
        
        # Ensure password masking is reset to 'Hidden'
        self.password_visible = True
        self.toggle_password_visibility()
        
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