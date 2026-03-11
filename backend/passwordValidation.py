import re

class PasswordValidation:
    """
    A utility class to enforce security standards for user credentials.
    Contains rules for both username formatting and password complexity.
    """

    @staticmethod
    def check_requirements(username, password):
        """
        Validates the username and password against security policies.
        
        Args:
            username (str): The chosen username for registration.
            password (str): The chosen password for registration.
            
        Returns:
            tuple: (bool, str) - Success status and a descriptive feedback message.
        """
        
        # --- 1. USERNAME VALIDATION ---
        # Ensure username is not too short or excessively long
        if not (3 <= len(username) <= 15):
            return False, "Username must be between 3 and 15 characters."
        
        # Prevent special characters or spaces in usernames for database safety
        if not username.isalnum():
            return False, "Username can only contain letters and numbers."

        # --- 2. PASSWORD LENGTH VALIDATION ---
        # Enforce a minimum length to protect against brute-force attacks
        if len(password) < 8:
            return False, "Password must be at least 8 characters long."
        
        # --- 3. PASSWORD COMPLEXITY (REGEX) ---
        # Look for at least one capital letter [A-Z]
        if not re.search(r"[A-Z]", password):
            return False, "Password needs at least one uppercase letter (A-Z)."
        
        # Look for at least one numeric digit [0-9]
        if not re.search(r"\d", password):
            return False, "Password needs at least one number (0-9)."
            
        # Look for at least one character from the special character set
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "Password needs at least one special character (@, #, $, etc.)."

        # If all checks pass
        return True, "Requirements met."