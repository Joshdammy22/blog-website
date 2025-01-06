from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from .models import Profile, CustomUser
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from allauth.socialaccount.models import SocialAccount

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation
from .models import CustomUser

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply 'form-control' class to all form fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data.get('email').strip()  # Trim whitespace
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("This email address is already associated with another account. Please choose a different one.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username').strip()  # Trim whitespace
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken. Please choose another one.")
        return username

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        
        # Check if password1 has already been validated and errors are present
        if not self.errors.get('password1'):  # If no error has been added yet
            try:
                password_validation.validate_password(password1, self.instance)
            except ValidationError as e:
                # Add each error to the 'password1' field with customized messages
                for error in e.messages:
                    # Customize each error message based on specific validation
                    if "too common" in error:
                        self.add_error('password1', "This password is too common. Please choose a stronger password.")
                    elif "too short" in error:
                        self.add_error('password1', "The password must be at least 8 characters long.")
                    elif "entirely numeric" in error:
                        self.add_error('password1', "The password cannot be entirely numeric. Please add letters.")
                    elif "password is too similar" in error:
                        self.add_error('password1', "This password is too similar to your username or personal information.")
                    else:
                        self.add_error('password1', error)
        
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        # Check if password1 and password2 match (only this check is necessary for password2)
        if password1 != password2:
            raise ValidationError("The passwords you entered do not match. Please ensure both passwords are the same.")
        
        return password2


from django import forms
from django.contrib.auth import get_user_model, authenticate


CustomUser = get_user_model()

class UserLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email',
        }),
        error_messages={'required': 'Username or Email is required.'}
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
        }),
        error_messages={'required': 'Password is required.'}
    )
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

    def clean(self):
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if not username_or_email or not password:
            raise forms.ValidationError("Please provide both username/email and password.")

        # Use the custom backend for authentication
        user = authenticate(username=username_or_email, password=password)

        if not user:
            raise forms.ValidationError("Invalid username/email or password.")

        if not user.is_active:
            raise forms.ValidationError("This account is inactive.")

        self.cleaned_data['user'] = user
        return self.cleaned_data



# User Update Form
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username']  # Only include username for user model
        widgets = {
            'username': forms.TextInput(attrs={'class': 'input-field'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exclude(id=self.instance.id).exists():
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
    old_password = None 
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