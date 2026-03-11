import customtkinter as ctk # type: ignore
from frontend.loginFrame import LoginFrame
from frontend.dashboardFrame import DashboardFrame
from frontend.registerFrame import RegisterFrame
from frontend.adminFrame import AdminFrame
from frontend.changePasswordFrame import ChangePasswordFrame
import os

class GUI(ctk.CTk):
    """
    The main Window controller for the application.
    Handles frame switching, global user state, and shared resources.
    """
    def __init__(self, budget_manager):
        super().__init__()
        
        # Call the centering method
        window_width = 1100
        window_height = 700
        self.title("SyntaxSpend")
        self.center_window(window_width, window_height)
        self.resizable(False, False)
        self.budget_manager = budget_manager
        
        # Global variable to track who is currently logged in
        self.current_user_id = None
        
        base_path = os.path.dirname(os.path.realpath(__file__))
        icon_path = os.path.join(base_path, "assets", "icon.ico")

        if os.path.exists(icon_path):
            self.after(1000, lambda: self.iconbitmap(icon_path))
        
        # 2. Layout Container
        # This frame acts as the parent 'stack' where all screens will sit
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)
        
        # Grid weights ensure the frames fill the entire window area
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # 3. Frame Initialization
        # We create one instance of every screen at startup and stack them
        self.frames = {}
        
        # Loop through all imported frame classes
        for F in (LoginFrame, RegisterFrame, DashboardFrame, AdminFrame, ChangePasswordFrame):
            page_name = F.__name__
            
            # Create the frame and pass 'self' as the 'controller'
            # This allows child frames to call self.controller.show_frame()
            frame = F(self.container, self, self.budget_manager)
            
            self.frames[page_name] = frame
            
            # Place all frames in the exact same grid coordinates (row 0, col 0)
            # They are now stacked on top of each other like a deck of cards
            frame.grid(row=0, column=0, sticky="nsew")

        # Start the application on the Login Screen
        self.show_frame("LoginFrame")

    def show_frame(self, page_name):
        """
        Brings the requested frame to the top of the stack.
        Also handles 'housekeeping' like clearing sensitive input fields.
        """
        frame = self.frames[page_name]
        
        # --- Housekeeping: Security & UX ---
        # If the frame has a 'clear_fields' method (like the Login or ChangePassword frames),
        # we run it so the user doesn't see their old data when they return to that screen.
        if hasattr(frame, "clear_fields"):
            frame.clear_fields()
            
        if hasattr(frame, "refresh_ui"):
            frame.refresh_ui()
            
        # Move the requested frame to the front of the 'stack'
        frame.tkraise()
        
    def center_window(self, width, height):
        """Calculates screen dimensions and centers the window."""
        # Get screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate x and y coordinates for the Tkinter geometry string
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        # Apply the geometry: "widthxheight+x_offset+y_offset"
        self.geometry(f'{width}x{height}+{x}+{y}')