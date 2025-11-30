import re
import string

def check_password_strength(password: str) -> bool:
    
    # 1. Check Minimum Length
    if len(password) < 8:
        return False
    
    # 2. Check for Lowercase letter
    if not re.search(r"[a-z]", password):
        return False
        
    # 3. Check for Uppercase letter
    if not re.search(r"[A-Z]", password):
        return False
        
    # 4. Check for Digit
    if not re.search(r"\d", password):
        return False
        
    # 5. Check for Special Character
    # We use string.punctuation to cover all standard special characters
    # passing the pattern into re.escape ensures regex doesn't break on characters like '[' or '*'
    special_chars_pattern = f"[{re.escape(string.punctuation)}]"
    if not re.search(special_chars_pattern, password):
        return False
        
    return True

def provide_feedback(password: str):
    feedback = []
    if len(password) < 8:
        feedback.append("- Length must be at least 8 characters.")
    if not re.search(r"[a-z]", password):
        feedback.append("- Missing a lowercase letter.")
    if not re.search(r"[A-Z]", password):
        feedback.append("- Missing an uppercase letter.")
    if not re.search(r"\d", password):
        feedback.append("- Missing a numeric digit (0-9).")
    special_chars_pattern = f"[{re.escape(string.punctuation)}]"
    if not re.search(special_chars_pattern, password):
        feedback.append("- Missing a special character (e.g., !, @, #, $).")
        
    return feedback

if __name__ == "__main__":
    print("--- DevOps Password Policy Validator ---")
    print("Criteria: 8+ chars, Upper, Lower, Digit, Special Char")
    print("-" * 40)
    
    try:
        # Taking user input
        user_password = input("Enter your password to validate: ")
        
        # Calling the validation function
        is_valid = check_password_strength(user_password)
        
        if is_valid:
            print("\n✅ Success! Strong password.")
        else:
            print("\n❌ Failed. Weak password.")
            print("Reasons:")
            # Generate detailed feedback to help the user fix it
            issues = provide_feedback(user_password)
            for issue in issues:
                print(f"  {issue}")
                
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")