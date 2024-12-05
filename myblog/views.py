from django.shortcuts import render

from django.shortcuts import render

def home(request):
    print("Accessing home view...")  # Debugging statement
    
    if request.user.is_authenticated:
        print(f"Authenticated user: {request.user.username}")  # Debugging for logged-in user
    else:
        print("No authenticated user.")  # Debugging for unauthenticated user

    # Pass the user instance to the template
    return render(request, 'home.html', {'user': request.user})
