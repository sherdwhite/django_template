"""
Custom forms for user registration and authentication.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class EmailRequiredUserCreationForm(UserCreationForm):
    """
    User creation form that requires an email address.
    """

    email = forms.EmailField(
        required=True,
        help_text="Required. We'll send you a verification code.",
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        help_text="Optional.",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "email", "password1", "password2")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_email(self):
        """
        Validate that the email is unique.
        """
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            raise ValidationError("A user with that email address already exists.")
        return email

    def save(self, commit=True):
        """
        Save the user with email and mark as inactive until email verification.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data.get("first_name", "")
        # Mark user as inactive until email verification
        user.is_active = False
        if commit:
            user.save()
        return user
