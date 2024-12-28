from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from .models import Profile
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from allauth.socialaccount.models import SocialAccount


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("A user with this username already exists.")
        return username


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email'
        }),
        error_messages={
            'required': 'Username or Email is required.'
        }
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        }),
        error_messages={
            'required': 'Password is required.'
        }
    )
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        
        # Check if the user exists in the database
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None
        
        # Skip reCAPTCHA validation only for social login users
        if user:
            social_login_attempt = SocialAccount.objects.filter(user=user).exists()
        else:
            social_login_attempt = False

        # Perform reCAPTCHA validation only for non-social logins
        if not social_login_attempt:
            if not cleaned_data.get('captcha'):
                self.add_error('captcha', 'Please complete the reCAPTCHA verification.')

        return cleaned_data


from django import forms
from django.contrib.auth.models import User
from .models import Profile
from django.core.exceptions import ValidationError

# User Update Form
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']  # Only include username for user model
        widgets = {
            'username': forms.TextInput(attrs={'class': 'input-field'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(id=self.instance.id).exists():
            raise ValidationError("This username is already taken. Please choose a different one.")
        return username


# Profile Update Form
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'bio', 'birth_date', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'input-field'}),
            'last_name': forms.TextInput(attrs={'class': 'input-field'}),
            'bio': forms.Textarea(attrs={'class': 'textarea-field', 'rows': 3}),
            'birth_date': forms.DateInput(attrs={'class': 'input-field', 'type': 'date'}),
        }
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if Profile.objects.filter(first_name=first_name).exclude(id=self.instance.id).exists():
            raise ValidationError("This first name is already taken. Please choose a different one.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if Profile.objects.filter(last_name=last_name).exclude(id=self.instance.id).exists():
            raise ValidationError("This last name is already taken. Please choose a different one.")
        return last_name

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date and birth_date.year > 2020:
            raise ValidationError("Please enter a valid birth date.")
        return birth_date




class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Old Password'}),
        error_messages={
            'required': 'Old password is required.'
        }
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'}),
        help_text="Your password must contain at least 8 characters and should not be entirely numeric.",
        error_messages={
            'required': 'New password is required.'
        }
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'}),
        error_messages={
            'required': 'Please confirm your new password.'
        }
    )

    def clean_new_password1(self):
        password1 = self.cleaned_data.get('new_password1')
        if len(password1) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if password1.isdigit():
            raise ValidationError("Password cannot be entirely numeric.")
        return password1

class SubscriptionListForm(forms.Form):
    user_email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'email-field',
            'placeholder': 'Your email address'
        })
    )