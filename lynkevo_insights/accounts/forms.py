from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from .models import Client, Membership


class ClientForm(forms.ModelForm):
    """
    Form for creating and editing clients
    """
    class Meta:
        model = Client
        fields = ['name', 'contact_email']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter client name',
                'required': True
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'client@example.com'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({
            'autofocus': True
        })


class MembershipForm(forms.ModelForm):
    """
    Form for adding users to clients with roles
    """
    class Meta:
        model = Membership
        fields = ['user', 'role']
        widgets = {
            'user': forms.Select(attrs={
                'class': 'form-control'
            }),
            'role': forms.Select(attrs={
                'class': 'form-control'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active users
        self.fields['user'].queryset = User.objects.filter(is_active=True).order_by('username')
        
        # Add help text
        self.fields['role'].help_text = "Owner: Full access, Editor: Can create/edit reports, Viewer: Read-only access"


class UserCreationForm(BaseUserCreationForm):
    """
    Enhanced user creation form with additional fields
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'user@example.com'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )
    is_staff = forms.BooleanField(
        required=False,
        help_text="Staff users can manage clients and other users"
    )
    
    class Meta(BaseUserCreationForm.Meta):
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_staff = self.cleaned_data['is_staff']
        if commit:
            user.save()
        return user


class ClientSearchForm(forms.Form):
    """
    Form for searching clients
    """
    search = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search clients by name or email...',
            'autocomplete': 'off'
        })
    )


class UserSearchForm(forms.Form):
    """
    Form for searching users
    """
    search = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search users by username, name, or email...',
            'autocomplete': 'off'
        })
    )