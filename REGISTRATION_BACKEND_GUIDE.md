# BANKING REGISTRATION SYSTEM - BACKEND INTEGRATION GUIDE

## Overview
This comprehensive guide explains how to integrate the secure, multi-step registration form with your Django backend. The registration system collects banking credentials and identity verification details while maintaining enterprise-grade security standards.

---

## 1. EXTENDED USER MODEL STRUCTURE

### Why Extended User Model?
The default Django User model doesn't include banking and identity verification fields. We need to create a `BankingProfile` model to store sensitive banking information securely.

### Models Implementation

```python
# queueapp/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator
from django.utils.crypto import get_random_string
from encrypt import EncryptedCharField, EncryptedTextField  # django-encrypted-model
import re

class BankingProfile(models.Model):
    """
    Extended user profile for banking system
    Stores sensitive banking and identity information
    """
    
    # Relationships
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='banking_profile')
    
    # Personal Details (Step 1)
    phone_number = models.CharField(
        max_length=20,
        unique=True,
        validators=[RegexValidator(
            regex=r'^\+?[0-9]{7,15}$',
            message='Invalid phone number format'
        )]
    )
    country_code = models.CharField(max_length=5, default='+91')
    
    # Bank Details (Step 2) - ENCRYPTED
    bank_name = models.CharField(max_length=100)
    account_number = EncryptedCharField(
        max_length=50,
        unique=True,
        db_index=False  # Don't index encrypted fields
    )
    account_holder_name = models.CharField(max_length=150)
    account_type = models.CharField(
        max_length=20,
        choices=[
            ('savings', 'Savings Account'),
            ('current', 'Current Account'),
            ('salary', 'Salary Account'),
        ]
    )
    branch_name = models.CharField(max_length=150)
    branch_code = models.CharField(
        max_length=11,
        validators=[RegexValidator(
            regex=r'^[A-Z0-9]{11}$',
            message='Invalid IFSC code'
        )]
    )
    
    # Identity Details (Step 3) - ENCRYPTED
    id_type = models.CharField(
        max_length=20,
        choices=[
            ('aadhaar', 'Aadhaar Card'),
            ('pan', 'PAN'),
            ('passport', 'Passport'),
            ('driving_license', 'Driving License'),
        ]
    )
    id_number = EncryptedCharField(
        max_length=50,
        unique=True,
        db_index=False
    )
    date_of_birth = models.DateField()
    
    # Address Information
    residential_address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    
    # Role Management
    role = models.CharField(
        max_length=20,
        default='customer',
        choices=[
            ('customer', 'Customer'),
            ('staff', 'Staff'),
            ('admin', 'Admin'),
        ]
    )
    
    # Compliance & Verification
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    bank_verified = models.BooleanField(default=False)
    identity_verified = models.BooleanField(default=False)
    
    # Consent & Agreements
    terms_agreed = models.BooleanField(default=False)
    data_processing_agreed = models.BooleanField(default=False)
    agreement_timestamp = models.DateTimeField(auto_now_add=True)
    
    # Security
    registration_token = models.CharField(max_length=100, unique=True, null=True)
    registration_verified = models.BooleanField(default=False)
    
    # Audit Trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        db_table = 'banking_profile'
        verbose_name = 'Banking Profile'
        verbose_name_plural = 'Banking Profiles'
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['phone_number']),
        ]
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.account_type}"
    
    def get_age(self):
        """Calculate age from DOB"""
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    @property
    def is_fully_verified(self):
        """Check if all verifications are complete"""
        return all([
            self.email_verified,
            self.phone_verified,
            self.bank_verified,
            self.identity_verified
        ])


class RegistrationAuditLog(models.Model):
    """
    Audit trail for registration attempts and security events
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='registration_logs')
    action = models.CharField(max_length=50)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ])
    details = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'registration_audit_log'
        verbose_name = 'Registration Audit Log'
        verbose_name_plural = 'Registration Audit Logs'
        indexes = [
            models.Index(fields=['user_id', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.action} - {self.status} - {self.timestamp}"
```

---

## 2. DJANGO FORM WITH VALIDATION

```python
# queueapp/forms.py

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import BankingProfile, RegistrationAuditLog
from datetime import date
import re

class RegistrationForm(forms.Form):
    """
    Multi-step registration form with comprehensive validation
    """
    
    # STEP 1: Personal Details
    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'John Doe',
            'data-validation': 'name'
        }),
        help_text='Enter your full name as per official documents'
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'john.doe@example.com',
            'data-validation': 'email'
        }),
        help_text='We will send a verification link to this email'
    )
    
    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '9876543210',
            'maxlength': '15',
            'data-validation': 'phone'
        }),
        help_text='10-15 digit phone number for OTP verification'
    )
    
    country_code = forms.ChoiceField(
        choices=[
            ('+91', '🇮🇳 +91 (India)'),
            ('+1', '🇺🇸 +1 (USA)'),
            ('+44', '🇬🇧 +44 (UK)'),
            ('+86', '🇨🇳 +86 (China)'),
            ('+81', '🇯🇵 +81 (Japan)'),
        ],
        widget=forms.Select(attrs={'class': 'country-select'})
    )
    
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter secure password',
            'data-validation': 'password'
        }),
        help_text='Minimum 8 characters: uppercase, lowercase, number, special character'
    )
    
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Re-enter password',
            'data-validation': 'confirmPassword'
        })
    )
    
    # STEP 2: Bank Details
    bank_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control autocomplete-input',
            'placeholder': 'Search or select bank...',
            'data-validation': 'bankName'
        }),
        help_text='Your registered bank name'
    )
    
    account_type = forms.ChoiceField(
        choices=[
            ('', '-- Select Account Type --'),
            ('savings', 'Savings Account'),
            ('current', 'Current Account'),
            ('salary', 'Salary Account'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'data-validation': 'accountType'
        })
    )
    
    branch_code = forms.CharField(
        max_length=11,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'SBIN0000123',
            'maxlength': '11',
            'data-validation': 'ifsc'
        }),
        help_text='6-digit IFSC code (e.g., SBIN0000123)'
    )
    
    branch_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Downtown Branch',
            'data-validation': 'text'
        })
    )
    
    account_number = forms.CharField(
        max_length=18,
        widget=forms.TextInput(attrs={
            'class': 'form-control sensitive-field',
            'placeholder': '1234567890123',
            'maxlength': '18',
            'data-validation': 'accountNumber',
            'autocomplete': 'off',
            'onpaste': 'return false;',  # Prevent paste
            'oncopy': 'return false;'    # Prevent copy
        }),
        help_text='11-18 digit account number (will be encrypted)'
    )
    
    account_holder_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'As per bank records',
            'data-validation': 'name'
        }),
        help_text='Must match your bank account holder name'
    )
    
    # STEP 3: Identity & Security
    id_type = forms.ChoiceField(
        choices=[
            ('', '-- Select ID Type --'),
            ('aadhaar', 'Aadhaar Card (12-digit)'),
            ('pan', 'PAN (10-digit)'),
            ('passport', 'Passport'),
            ('driving_license', 'Driving License'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'data-validation': 'idType'
        })
    )
    
    id_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control sensitive-field',
            'placeholder': '123456789012',
            'data-validation': 'idNumber',
            'autocomplete': 'off',
            'onpaste': 'return false;'
        }),
        help_text='Government ID number (encrypted and stored securely)'
    )
    
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'data-validation': 'dob'
        }),
        help_text='Must be at least 18 years old'
    )
    
    address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control textarea',
            'placeholder': 'Enter your complete residential address',
            'rows': 3,
            'data-validation': 'address'
        }),
        help_text='Your current address as per official records'
    )
    
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Bangalore',
            'data-validation': 'text'
        })
    )
    
    state = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Karnataka',
            'data-validation': 'text'
        })
    )
    
    postal_code = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '560001',
            'maxlength': '10',
            'data-validation': 'postalCode'
        })
    )
    
    # STEP 4: Role & Confirmation
    role = forms.ChoiceField(
        choices=[
            ('customer', 'Customer'),
            # ('staff', 'Staff'),  # Only via admin approval
        ],
        widget=forms.RadioSelect(attrs={'class': 'role-radio'}),
        initial='customer'
    )
    
    terms_agreed = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'checkbox-input'}),
        help_text='I agree to Terms & Conditions and Privacy Policy'
    )
    
    data_processing_agreed = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'checkbox-input'}),
        help_text='I consent to processing my personal data for verification'
    )
    
    human_verification = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'checkbox-input'}),
        help_text='I confirm I am human'
    )
    
    def clean_full_name(self):
        """Validate full name format"""
        name = self.cleaned_data.get('full_name', '').strip()
        if not re.match(r'^[a-zA-Z\s]{2,}$', name):
            raise ValidationError('Name must contain only letters and spaces (minimum 2 characters)')
        return name
    
    def clean_email(self):
        """Check for duplicate emails"""
        email = self.cleaned_data.get('email', '').lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email is already registered')
        return email
    
    def clean_phone_number(self):
        """Validate phone number format"""
        phone = self.cleaned_data.get('phone_number', '').strip()
        if not re.match(r'^[0-9]{7,15}$', phone):
            raise ValidationError('Phone number must be 7-15 digits')
        if User.objects.filter(banking_profile__phone_number=phone).exists():
            raise ValidationError('This phone number is already registered')
        return phone
    
    def clean_password(self):
        """Validate password strength"""
        password = self.cleaned_data.get('password', '')
        
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', password):
            raise ValidationError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'"|,.<>\/?]', password):
            raise ValidationError('Password must contain at least one special character')
        
        return password
    
    def clean_confirm_password(self):
        """Check password match"""
        password = self.cleaned_data.get('password', '')
        confirm = self.cleaned_data.get('confirm_password', '')
        
        if password and confirm and password != confirm:
            raise ValidationError('Passwords do not match')
        
        return confirm
    
    def clean_account_number(self):
        """Validate and check duplicate account numbers"""
        account = self.cleaned_data.get('account_number', '').strip()
        if not re.match(r'^[0-9]{10,18}$', account):
            raise ValidationError('Account number must be 10-18 digits')
        
        # Check for duplicate (need to compare encrypted values)
        if BankingProfile.objects.filter(account_number=account).exists():
            raise ValidationError('This account number is already registered')
        
        return account
    
    def clean_branch_code(self):
        """Validate IFSC code format"""
        code = self.cleaned_data.get('branch_code', '').upper().strip()
        if not re.match(r'^[A-Z0-9]{11}$', code):
            raise ValidationError('IFSC code must be 11 alphanumeric characters')
        return code
    
    def clean_id_number(self):
        """Validate ID number format based on type"""
        id_type = self.cleaned_data.get('id_type', '')
        id_number = self.cleaned_data.get('id_number', '').strip().upper()
        
        validators = {
            'aadhaar': (r'^[0-9]{12}$', '12-digit number'),
            'pan': (r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', 'Format: AAAAA0000A'),
            'passport': (r'^[A-Z]{1}[0-9]{7}$', 'Format: A0000000'),
            'driving_license': (r'^[A-Z]{2}[0-9]{13}$', 'Valid DL format'),
        }
        
        if id_type in validators:
            pattern, hint = validators[id_type]
            if not re.match(pattern, id_number):
                raise ValidationError(f'Invalid {id_type}. Expected: {hint}')
        
        # Check for duplicate
        if BankingProfile.objects.filter(id_number=id_number).exists():
            raise ValidationError('This ID number is already registered')
        
        return id_number
    
    def clean_date_of_birth(self):
        """Validate age (18+)"""
        dob = self.cleaned_data.get('date_of_birth')
        if not dob:
            raise ValidationError('Date of birth is required')
        
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        
        if age < 18:
            raise ValidationError('You must be at least 18 years old')
        
        return dob
    
    def clean(self):
        """Overall form validation"""
        cleaned_data = super().clean()
        
        # Check password match at form level
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')
        
        if password and confirm and password != confirm:
            self.add_error('confirm_password', 'Passwords do not match')
        
        return cleaned_data
```

---

## 3. REGISTRATION VIEW WITH SECURITY

```python
# queueapp/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.http import JsonResponse
from .forms import RegistrationForm
from .models import BankingProfile, RegistrationAuditLog
from .permissions import log_audit_event
from datetime import datetime
import json

@csrf_protect
@require_http_methods(["GET", "POST"])
def register(request):
    """
    Secure registration view with multi-step form handling
    """
    
    if request.method == 'POST':
        # Get client IP for audit trail
        client_ip = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Handle AJAX requests (step validation)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return handle_registration_submission(request, client_ip, user_agent)
        
        # Standard form submission
        form = RegistrationForm(request.POST)
        
        if form.is_valid():
            return process_registration(request, form, client_ip, user_agent)
        else:
            # Return form with errors
            return render(request, 'auth/register.html', {
                'form': form,
                'errors': form.errors
            })
    
    else:  # GET request
        form = RegistrationForm()
        return render(request, 'auth/register.html', {'form': form})


def handle_registration_submission(request, client_ip, user_agent):
    """
    Handle AJAX registration submission with validation
    """
    try:
        data = json.loads(request.body)
        form = RegistrationForm(data)
        
        if form.is_valid():
            # Process registration
            return process_registration(request, form, client_ip, user_agent, ajax=True)
        else:
            # Return validation errors
            log_audit_event(
                user=None,
                action='registration_validation_failed',
                ip_address=client_ip,
                user_agent=user_agent,
                status='failed',
                details={'errors': form.errors}
            )
            
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def process_registration(request, form, client_ip, user_agent, ajax=False):
    """
    Process validated registration form and create user with banking profile
    """
    try:
        # Extract form data
        cleaned_data = form.cleaned_data
        
        # Create User account
        user = User.objects.create_user(
            username=cleaned_data['email'],  # Use email as username
            email=cleaned_data['email'],
            first_name=cleaned_data['full_name'].split()[0],
            last_name=' '.join(cleaned_data['full_name'].split()[1:]),
        )
        
        # Set password
        user.set_password(cleaned_data['password'])
        user.save()
        
        # Create banking profile
        profile = BankingProfile.objects.create(
            user=user,
            phone_number=f"{cleaned_data['country_code']}{cleaned_data['phone_number']}",
            country_code=cleaned_data['country_code'],
            bank_name=cleaned_data['bank_name'],
            account_number=cleaned_data['account_number'],  # Encrypted automatically
            account_holder_name=cleaned_data['account_holder_name'],
            account_type=cleaned_data['account_type'],
            branch_name=cleaned_data['branch_name'],
            branch_code=cleaned_data['branch_code'],
            id_type=cleaned_data['id_type'],
            id_number=cleaned_data['id_number'],  # Encrypted automatically
            date_of_birth=cleaned_data['date_of_birth'],
            residential_address=cleaned_data['address'],
            city=cleaned_data['city'],
            state=cleaned_data['state'],
            postal_code=cleaned_data['postal_code'],
            role=cleaned_data['role'],
            terms_agreed=cleaned_data['terms_agreed'],
            data_processing_agreed=cleaned_data['data_processing_agreed'],
            registration_token=get_random_string(50),
            last_login_ip=client_ip
        )
        
        # Log successful registration
        log_audit_event(
            user=user,
            action='registration_completed',
            ip_address=client_ip,
            user_agent=user_agent,
            status='success',
            details={
                'email': user.email,
                'role': profile.role,
                'account_type': profile.account_type
            }
        )
        
        # Send verification email
        send_registration_verification_email(user, profile)
        
        # Auto-login the user
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        
        if ajax:
            return JsonResponse({
                'success': True,
                'message': 'Registration successful! Redirecting...',
                'redirect_url': '/customer/dashboard/'
            })
        else:
            messages.success(request, 'Registration successful! Welcome to Smart Banking System.')
            return redirect('/customer/dashboard/')
    
    except Exception as e:
        log_audit_event(
            user=None,
            action='registration_error',
            ip_address=client_ip,
            user_agent=user_agent,
            status='failed',
            details={'error': str(e)}
        )
        
        if ajax:
            return JsonResponse({
                'success': False,
                'error': 'Registration failed. Please try again.'
            }, status=500)
        else:
            messages.error(request, 'Registration failed. Please try again.')
            return redirect('register')


def get_client_ip(request):
    """Extract real client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
```

---

## 4. FIELD ENCRYPTION & SECURITY

### Install django-encrypted-model:
```bash
pip install django-encrypted-model
```

### settings.py configuration:
```python
# Security settings for banking registration

# Encryption
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')  # Generate with: python manage.py generate_encryption_key

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Session security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_AGE = 3600  # 1 hour

# CSRF protection
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# Security headers
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

---

## 5. VALIDATION SUMMARY

| Field | Frontend Validation | Backend Validation | Storage |
|-------|-------------------|-------------------|---------|
| Full Name | Regex (letters only) | Regex + length | Plain text |
| Email | Email format | Unique check | Plain text |
| Phone | Digit check | Unique + format | Plain text |
| Password | Strength indicator | Complexity rules | Hashed (Django default) |
| Account Number | 10-18 digits | Unique + format | **Encrypted** |
| IFSC Code | 11 alphanumeric | Format validation | Plain text |
| ID Number | Type-specific format | Unique + format | **Encrypted** |
| Date of Birth | Date picker | Age validation (18+) | Plain text |
| Address | Length check | Length validation | Plain text |

---

## 6. SECURITY CHECKLIST

- ✅ CSRF protection on form submission
- ✅ Password hashing (Django default)
- ✅ Sensitive field encryption (account #, ID #)
- ✅ Unique constraints on phone & account number
- ✅ No copy-paste on sensitive fields (frontend)
- ✅ IP logging for audit trail
- ✅ SSL/HTTPS enforcement
- ✅ Secure session cookies (HttpOnly, Secure, SameSite)
- ✅ Input validation on both frontend & backend
- ✅ SQL injection prevention (Django ORM)
- ✅ Audit trail for all registration events

---

## 7. URLS CONFIGURATION

```python
# queueapp/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('auth/register/', views.register, name='register'),
    # ... other URL patterns
]
```

---

## 8. MIGRATION COMMANDS

```bash
# Create migration
python manage.py makemigrations

# Apply migration
python manage.py migrate

# Check migration status
python manage.py showmigrations
```

---

## 9. TESTING THE REGISTRATION

```python
# Test case example
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import BankingProfile

class RegistrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = '/auth/register/'
    
    def test_valid_registration(self):
        """Test successful registration"""
        response = self.client.post(self.register_url, {
            'full_name': 'John Doe',
            'email': 'john@example.com',
            'phone_number': '9876543210',
            'country_code': '+91',
            'password': 'SecurePass123!@',
            'confirm_password': 'SecurePass123!@',
            'bank_name': 'State Bank of India',
            'account_type': 'savings',
            'branch_code': 'SBIN0000123',
            'branch_name': 'Downtown',
            'account_number': '12345678901',
            'account_holder_name': 'John Doe',
            'id_type': 'aadhaar',
            'id_number': '123456789012',
            'date_of_birth': '2000-01-01',
            'address': '123 Main St, City, Country',
            'city': 'Bangalore',
            'state': 'Karnataka',
            'postal_code': '560001',
            'role': 'customer',
            'terms_agreed': True,
            'data_processing_agreed': True,
            'human_verification': True,
        })
        
        # Check user was created
        user = User.objects.filter(email='john@example.com').first()
        self.assertIsNotNone(user)
        
        # Check banking profile was created
        profile = BankingProfile.objects.filter(user=user).first()
        self.assertIsNotNone(profile)
```

---

## 10. DEPLOYMENT CHECKLIST

- [ ] Set `DEBUG = False` in production
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set encryption keys in environment variables
- [ ] Configure email backend (SMTP)
- [ ] Setup database backups
- [ ] Enable HTTPS/SSL certificate
- [ ] Configure logging for audit trail
- [ ] Test all validation rules
- [ ] Setup monitoring & alerts
- [ ] Document API endpoints
- [ ] Train support team on role assignment workflow

This backend integration ensures your registration system is secure, validated, and compliant with banking standards.
