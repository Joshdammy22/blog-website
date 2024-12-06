import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myblog.settings')  # Replace 'myblog.settings' with your settings module
django.setup()

from django.contrib.auth import get_user_model
from users.models import Profile  # Replace 'users' with the app name where Profile is located

def delete_user_by_email(email):
    """
    Deletes a user and their associated profile by email.
    
    Args:
        email (str): The email of the user to delete.

    Returns:
        str: A success or failure message.
    """
    User = get_user_model()  # Get the User model
    try:
        # Fetch the user by email
        user = User.objects.get(email=email)
        username = user.username  # Store username for confirmation message
        
        # Check and delete the user's profile
        if hasattr(user, 'profile'):
            user.profile.delete()
            print(f"Profile for user '{username}' deleted successfully.")

        # Delete the user
        user.delete()
        print(f"User '{username}' with email '{email}' deleted successfully.")
        return f"User '{username}' with email '{email}' and their profile have been deleted."
    except User.DoesNotExist:
        print(f"No user found with email '{email}'.")
        return f"No user found with email '{email}'."
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"An error occurred: {e}"

# Example usage
if __name__ == "__main__":
    email_to_delete = input("Enter the email of the user to delete: ")
    result = delete_user_by_email(email_to_delete)
    print(result)
