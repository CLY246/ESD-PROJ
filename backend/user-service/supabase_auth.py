import os
import re
import supabase

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Ensure environment variables are set
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials are missing.")

# Initialize Supabase client
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

def sign_in_user(email, password):
    """Logs in a user with Supabase Auth, ignoring email confirmation status."""
    try:
        response = supabase_client.auth.sign_in_with_password({"email": email, "password": password})

        if hasattr(response, "error") and response.error:
            error_message = response.error.message.lower()

            if "Email not confirmed" in error_message:
                print("Ignoring email confirmation check")

            else:
                return {"error": error_message}

        if not response.user:
            return {"error": "Invalid login credentials"}

        print("Auth Response:", response)

        return {
            "user_id": response.user.id,
            "access_token": response.session.access_token if response.session else None,
            "refresh_token": response.session.refresh_token if response.session else None,
        }

    except Exception as e:
        print("Supabase Auth Error:", str(e))
        return {"error": str(e)}

    
def get_user_info(access_token):
    """Fetch user info using the JWT token"""
    response = supabase_client.auth.get_user(access_token)
    return response

def is_valid_email(email):
    """Validate email format before sending to Supabase."""
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email) is not None

def sign_up_user(email, password):
    """Registers a user with Supabase Auth and prints the full response for debugging."""
    try:
        response = supabase_client.auth.sign_up({"email": email, "password": password})

        print("Supabase Sign-Up Response:", response)

        if hasattr(response, "error") and response.error:
            return {"error": response.error.message}

        if not hasattr(response, "user") or response.user is None:
            return {"error": "User creation failed - User object is missing"}

        print("User object:", response.user)  # Debugging

        return {"user_id": response.user.id}

    except Exception as e:
        print("Supabase Auth Error:", str(e))
        return {"error": str(e)}

