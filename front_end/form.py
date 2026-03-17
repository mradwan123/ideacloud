from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class RegisterForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'password',
            'description',
            'image'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last name'}),
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'email': forms.TextInput(attrs={'placeholder': 'Email'}),
            'password': forms.PasswordInput(attrs={'placeholder': 'Password'}),
            'description': forms.Textarea(attrs={'placeholder': 'Tell us about yourself'}),
            # image uses a default field
        }

    # def clean(self):
    #     clean_data = super().clean()
    #     first_name = clean_data.get("first_name")
    #     last_name = clean_data.get("last_name")
    #     username = clean_data.get("username")
    #     email = clean_data.get("email")
    #     password = clean_data.get("password")

    #     if not first_name:
    #         self.add_error("first_name", ValidationError("First name required."))
    #     if not last_name:
    #         self.add_error("last_name", ValidationError("Last name required."))
    #     if not username:
    #         self.add_error("username", ValidationError("Username required."))
    #     if not email:
    #         self.add_error("email", ValidationError("Email required."))
    #     if not password:
    #         self.add_error("password", ValidationError("Password required."))
    #     if User.objects.filter(username=username).exists():
    #         self.add_error("username", ValidationError("Username already taken."))
    #     if User.objects.filter(email=email).exists():
    #         self.add_error("email", ValidationError("Email already in use."))