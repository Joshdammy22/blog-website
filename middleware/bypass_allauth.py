from django.shortcuts import redirect

class BypassAllauthForAdmin:
    """
    Middleware to bypass Allauth login for the Django admin.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # If the request is for the admin and the user is logged in, skip Allauth
        if request.path.startswith('/admin/') and request.user.is_authenticated:
            return self.get_response(request)
        return self.get_response(request)
