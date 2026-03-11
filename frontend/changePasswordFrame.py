import customtkinter as ctk # type: ignore
from tkinter import messagebox
from PIL import Image # type: ignore
import os

class ChangePasswordFrame(ctk.CTkFrame):
    """
    A split-screen UI frame allowing users to update their account password.
    Mimics the visual style of the Login and Registration screens.
    """
    def __init__(self, parent, controller, budget_manager):
        # Initialize the frame with the standard dark theme background
        super().__init__(parent, fg_color="#1a1a1a")
        self.controller = controller
        self.budget_manager = budget_manager
        self.show_pw = False 

        # Configure 1x2 grid for a 50/50 split-screen layout
        self.grid_columnconfigure(0, weight=1) # Left side (Branding)
        self.grid_columnconfigure(1, weight=1) # Right side (Form)
        self.grid_rowconfigure(0, weight=1)

        # --- LEFT SIDE: BRANDING AREA ---
        # Darker background (#111111) to create visual contrast
        self.left_side = ctk.CTkFrame(self, fg_color="#111111", corner_radius=0)
        self.left_side.grid(row=0, column=0, sticky="nsew")
        
        # Centered container for logo and text
        self.brand_container = ctk.CTkFrame(self.left_side, fg_color="transparent")
        self.brand_container.place(relx=0.5, rely=0.5, anchor="center")

        # Dynamic Logo Loading
        try:
            base_path = os.path.dirname(os.path.realpath(__file__))
            logo_path = os.path.join(base_path, "assets", "company_logo.png")
            my_logo = ctk.CTkImage(
                light_image=Image.open(logo_path),
                dark_image=Image.open(logo_path),
                size=(150, 100)
            )
            ctk.CTkLabel(self.brand_container, image=my_logo, text="").pack(pady=20)
        except Exception:
            # Fallback icon if the image file is missing
            ctk.CTkLabel(self.brand_container, text="🛡️", font=("Arial", 80)).pack(pady=20)

        ctk.CTkLabel(self.brand_container, text="SyntaxSpend", font=("Arial", 40, "bold"), text_color="#3498db").pack(pady=10)
        ctk.CTkLabel(self.brand_container, text="Secure your account\nUpdate your credentials", 
                     font=("Arial", 16), text_color="white", justify="center").pack()

        # --- RIGHT SIDE: INPUT FORM AREA ---
        self.right_side = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=0)
        self.right_side.grid(row=0, column=1, sticky="nsew")

        # Centered Card to hold the form fields
        self.box = ctk.CTkFrame(self.right_side, width=380, height=550, fg_color="#111111", corner_radius=15)
        self.box.place(relx=0.5, rely=0.5, anchor="center")
        self.box.pack_propagate(False)

        ctk.CTkLabel(self.box, text="Update Password", font=("Arial", 32, "bold"), text_color="white").pack(pady=(80, 30))

        # Reusable dictionary for consistent entry field styling
        field_style = {
            "width": 300, "height": 50, "fg_color": "#1a1a1a", 
            "border_color": "#2d2d2d", "border_width": 1, 
            "corner_radius": 8, "text_color": "white"
        }

        # --- Current Password Field ---
        ctk.CTkLabel(self.box, text="Current Password", font=("Arial", 14), text_color="#3498db").pack(anchor="w", padx=40)
        self.old_pass = ctk.CTkEntry(self.box, placeholder_text="Type current password", show="*", **field_style)
        self.old_pass.pack(pady=(5, 15))

        # --- New Password Field ---
        ctk.CTkLabel(self.box, text="New Password", font=("Arial", 14), text_color="#3498db").pack(anchor="w", padx=40)
        self.new_pass = ctk.CTkEntry(self.box, placeholder_text="Enter new password", show="*", **field_style)
        self.new_pass.pack(pady=(5, 0))

        # --- Password Visibility Toggle ---
        self.toggle_btn = ctk.CTkButton(
            self.box, text="👁 Show Passwords", font=("Arial", 11),
            fg_color="transparent", text_color="gray60", hover_color="#1a1a1a",
            width=100, height=20, command=self.toggle_passwords
        )
        self.toggle_btn.pack(pady=(5, 10), anchor="e", padx=40)

        # --- Form Action Buttons ---
        ctk.CTkButton(
            self.box, text="Save Changes", width=300, height=50, 
            font=("Arial", 16, "bold"), fg_color="#3498db", 
            hover_color="#2980b9", command=self.handle_save
        ).pack(pady=(20, 10))

        ctk.CTkButton(
            self.box, text="Cancel", fg_color="transparent", 
            text_color="#3498db", hover_color="#1a1a1a",
            command=lambda: controller.show_frame("DashboardFrame")
        ).pack(pady=5)

    def toggle_passwords(self):
        """Switches entry fields between masked (***) and plain text."""
        self.show_pw = not self.show_pw
        mask = "" if self.show_pw else "*"
        self.old_pass.configure(show=mask)
        self.new_pass.configure(show=mask)
        self.toggle_btn.configure(text="👁 Hide Passwords" if self.show_pw else "👁 Show Passwords")

    def handle_save(self):
        """Validates input and communicates with the database to update the password."""
        old_p = self.old_pass.get().strip()
        new_p = self.new_pass.get().strip()
        user_id = self.controller.current_user_id

        # Basic front-end validation
        if not old_p or not new_p:
            messagebox.showwarning("Warning", "All fields are required.")
            return

        # Backend database call
        success, message = self.budget_manager.db.change_password(user_id, old_p, new_p)

        if success:
            messagebox.showinfo("Success", "Password updated successfully!")
            self.controller.show_frame("DashboardFrame")
        else:
            # Display detailed error (e.g., 'incorrect current password' or 'weak new password')
            messagebox.showerror("Error", message)

    def clear_fields(self):
        """Wipes all input data. Triggered automatically by the controller upon navigation."""
        self.old_pass.delete(0, 'end')
        self.new_pass.delete(0, 'end')
        self.show_pw = True
        self.toggle_passwords() # Forces reset to masked text