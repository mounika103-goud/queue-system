/**
 * REGISTRATION FORM MANAGER
 * Handles multi-step form validation, progress tracking, and secure data handling
 * Banking Platform - Enterprise Grade
 */

class RegistrationFormManager {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 4;
        this.formData = {};
        this.validationRules = {};
        this.init();
    }

    init() {
        console.log('🏦 Registration Form Manager initialized');
        this.cacheElements();
        this.setupEventListeners();
        this.initializeValidationRules();
        this.setupBankAutocomplete();
        this.setupPasswordStrength();
        this.setupDOBAge();
    }

    /**
     * Cache frequently used DOM elements
     */
    cacheElements() {
        this.form = document.getElementById('registrationForm');
        this.progressBar = document.getElementById('progressBar');
        this.submitBtn = document.getElementById('submitBtn');
        this.formErrors = document.getElementById('formErrors');
        this.steps = document.querySelectorAll('.form-step');
        this.stepIndicators = document.querySelectorAll('.step');
    }

    /**
     * Setup all event listeners
     */
    setupEventListeners() {
        // Navigation buttons
        document.querySelectorAll('.btn-next').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleNextStep(e));
        });

        document.querySelectorAll('.btn-prev').forEach(btn => {
            btn.addEventListener('click', (e) => this.handlePrevStep(e));
        });

        // Form submission
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));

        // Real-time validation on input
        document.querySelectorAll('.form-control').forEach(input => {
            input.addEventListener('blur', () => this.validateField(input));
            input.addEventListener('change', () => this.validateField(input));
        });

        // Toggle password visibility
        document.querySelectorAll('.toggle-password').forEach(btn => {
            btn.addEventListener('click', (e) => this.togglePasswordVisibility(e));
        });

        // Password strength on input
        const passwordField = document.getElementById('password');
        if (passwordField) {
            passwordField.addEventListener('input', () => this.updatePasswordStrength());
        }

        // Account holder name checking
        const accountHolderName = document.getElementById('accountHolderName');
        const fullName = document.getElementById('fullName');
        if (accountHolderName && fullName) {
            accountHolderName.addEventListener('blur', () => this.checkNameMatch());
        }

        // Role selection
        document.querySelectorAll('.role-card').forEach(card => {
            if (!card.querySelector('input[disabled]')) {
                card.addEventListener('click', () => this.selectRole(card));
            }
        });
    }

    /**
     * Initialize validation rules for all fields
     */
    initializeValidationRules() {
        this.validationRules = {
            name: {
                pattern: /^[a-zA-Z\s]{2,}$/,
                message: 'Please enter a valid name (minimum 2 characters, letters only)'
            },
            email: {
                pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                message: 'Please enter a valid email address'
            },
            phone: {
                pattern: /^[0-9]{7,15}$/,
                message: 'Please enter a valid phone number'
            },
            password: {
                minLength: 8,
                patterns: {
                    length: /.{8,}/,
                    uppercase: /[A-Z]/,
                    lowercase: /[a-z]/,
                    number: /[0-9]/,
                    special: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/
                },
                message: 'Password must meet all requirements'
            },
            accountNumber: {
                pattern: /^[0-9]{10,18}$/,
                message: 'Account number must be 10-18 digits'
            },
            ifsc: {
                pattern: /^[A-Z0-9]{11}$/,
                message: 'IFSC code must be 11 alphanumeric characters (e.g., SBIN0000123)'
            },
            idNumber: {
                validators: {
                    aadhaar: /^[0-9]{12}$/,
                    pan: /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/,
                    passport: /^[A-Z]{1}[0-9]{7}$/,
                    driving_license: /^[A-Z]{2}[0-9]{13}$/
                },
                message: 'Invalid ID number format'
            },
            dob: {
                message: 'You must be at least 18 years old'
            },
            address: {
                pattern: /.{10,}/,
                message: 'Please enter a valid address (minimum 10 characters)'
            },
            postalCode: {
                pattern: /^[0-9]{5,10}$/,
                message: 'Please enter a valid postal code'
            },
            bankName: {
                message: 'Please select a valid bank'
            },
            accountType: {
                message: 'Please select an account type'
            }
        };
    }

    /**
     * Validate a single field
     */
    validateField(input) {
        const validationType = input.dataset.validation;
        const value = input.value.trim();
        const messageEl = input.parentElement.querySelector('.validation-message');

        if (!validationType) return true;

        let isValid = true;
        let errorMessage = '';

        switch (validationType) {
            case 'name':
                isValid = this.validationRules.name.pattern.test(value);
                errorMessage = this.validationRules.name.message;
                break;
            case 'email':
                isValid = this.validationRules.email.pattern.test(value);
                errorMessage = this.validationRules.email.message;
                break;
            case 'phone':
                isValid = this.validationRules.phone.pattern.test(value);
                errorMessage = this.validationRules.phone.message;
                break;
            case 'password':
                isValid = value.length >= this.validationRules.password.minLength &&
                         Object.values(this.validationRules.password.patterns).every(p => p.test(value));
                errorMessage = this.validationRules.password.message;
                break;
            case 'confirmPassword':
                isValid = value === document.getElementById('password').value;
                errorMessage = 'Passwords do not match';
                break;
            case 'accountNumber':
                isValid = this.validationRules.accountNumber.pattern.test(value);
                errorMessage = this.validationRules.accountNumber.message;
                break;
            case 'ifsc':
                isValid = this.validationRules.ifsc.pattern.test(value);
                errorMessage = this.validationRules.ifsc.message;
                break;
            case 'idNumber':
                const idType = document.getElementById('idType').value;
                if (idType && this.validationRules.idNumber.validators[idType]) {
                    isValid = this.validationRules.idNumber.validators[idType].test(value);
                }
                errorMessage = this.validationRules.idNumber.message;
                break;
            case 'dob':
                isValid = this.isValidAge(input.value);
                errorMessage = this.validationRules.dob.message;
                break;
            case 'address':
                isValid = this.validationRules.address.pattern.test(value);
                errorMessage = this.validationRules.address.message;
                break;
            case 'postalCode':
                isValid = this.validationRules.postalCode.pattern.test(value);
                errorMessage = this.validationRules.postalCode.message;
                break;
            case 'text':
                isValid = value.length >= 2;
                errorMessage = 'This field requires at least 2 characters';
                break;
            case 'bankName':
                isValid = value.length > 0;
                errorMessage = this.validationRules.bankName.message;
                break;
            case 'accountType':
                isValid = input.value.length > 0;
                errorMessage = this.validationRules.accountType.message;
                break;
        }

        // Required field check
        if (!value && input.hasAttribute('required')) {
            isValid = false;
            errorMessage = 'This field is required';
        }

        this.updateFieldValidation(input, isValid, errorMessage, messageEl);
        return isValid;
    }

    /**
     * Update field validation UI
     */
    updateFieldValidation(input, isValid, errorMessage, messageEl) {
        if (isValid) {
            input.classList.remove('error');
            input.classList.add('success');
            if (messageEl) {
                messageEl.classList.remove('show');
                messageEl.textContent = '';
            }
        } else {
            input.classList.add('error');
            input.classList.remove('success');
            if (messageEl) {
                messageEl.classList.add('show');
                messageEl.textContent = errorMessage;
            }
        }
    }

    /**
     * Validate all fields in current step
     */
    validateCurrentStep() {
        const currentStepEl = document.querySelector(`.form-step[data-step="${this.currentStep}"]`);
        const inputs = currentStepEl.querySelectorAll('[required]');
        let isStepValid = true;

        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isStepValid = false;
            }
        });

        // Special validation for checkboxes in final step
        if (this.currentStep === 4) {
            const checkboxes = currentStepEl.querySelectorAll('input[type="checkbox"][required]');
            checkboxes.forEach(checkbox => {
                if (!checkbox.checked) {
                    const messageEl = checkbox.parentElement.querySelector('.validation-message');
                    if (messageEl) {
                        messageEl.classList.add('show');
                        messageEl.textContent = 'This must be checked to proceed';
                    }
                    isStepValid = false;
                }
            });
        }

        return isStepValid;
    }

    /**
     * Handle next step button click
     */
    handleNextStep(e) {
        e.preventDefault();
        
        if (this.validateCurrentStep()) {
            this.collectStepData();
            if (this.currentStep < this.totalSteps) {
                this.goToStep(this.currentStep + 1);
            }
        } else {
            this.showStepError('Please correct the errors above before proceeding');
        }
    }

    /**
     * Handle previous step button click
     */
    handlePrevStep(e) {
        e.preventDefault();
        this.collectStepData();
        if (this.currentStep > 1) {
            this.goToStep(this.currentStep - 1);
        }
    }

    /**
     * Navigate to specific step
     */
    goToStep(stepNumber) {
        // Hide all steps
        this.steps.forEach(step => step.classList.remove('active'));

        // Show target step
        const targetStep = document.querySelector(`.form-step[data-step="${stepNumber}"]`);
        if (targetStep) {
            targetStep.classList.add('active');
        }

        // Update progress indicator
        this.updateProgressIndicator(stepNumber);

        // Update current step
        this.currentStep = stepNumber;

        // Populate summary on final step
        if (stepNumber === 4) {
            this.populateSummary();
        }

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });

        console.log(`📍 Moved to step ${stepNumber}`);
    }

    /**
     * Update progress bar and step indicators
     */
    updateProgressIndicator(currentStep) {
        // Update progress bar
        const progressPercentage = (currentStep / this.totalSteps) * 100;
        this.progressBar.style.width = progressPercentage + '%';

        // Update step indicators
        this.stepIndicators.forEach((indicator, index) => {
            const stepNum = index + 1;
            indicator.classList.remove('step-active', 'step-completed');

            if (stepNum === currentStep) {
                indicator.classList.add('step-active');
            } else if (stepNum < currentStep) {
                indicator.classList.add('step-completed');
            }
        });
    }

    /**
     * Collect data from current step
     */
    collectStepData() {
        const currentStepEl = document.querySelector(`.form-step[data-step="${this.currentStep}"]`);
        const inputs = currentStepEl.querySelectorAll('[name]');

        inputs.forEach(input => {
            if (input.type === 'checkbox' || input.type === 'radio') {
                if (input.checked) {
                    this.formData[input.name] = input.value;
                }
            } else {
                this.formData[input.name] = input.value;
            }
        });

        console.log('📝 Form data collected:', this.formData);
    }

    /**
     * Password strength indicator
     */
    updatePasswordStrength() {
        const password = document.getElementById('password').value;
        const requirements = {
            length: /.{8,}/.test(password),
            uppercase: /[A-Z]/.test(password),
            lowercase: /[a-z]/.test(password),
            number: /[0-9]/.test(password),
            special: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)
        };

        // Update requirement indicators
        Object.entries(requirements).forEach(([req, met]) => {
            const reqEl = document.querySelector(`[data-requirement="${req}"]`);
            if (reqEl) {
                if (met) {
                    reqEl.classList.add('met');
                    reqEl.querySelector('.requirement-icon').textContent = '✓';
                } else {
                    reqEl.classList.remove('met');
                    reqEl.querySelector('.requirement-icon').textContent = '✗';
                }
            }
        });

        // Calculate and update strength
        const strengthCount = Object.values(requirements).filter(Boolean).length;
        const progressEl = document.getElementById('strengthProgress');
        const labelEl = document.getElementById('strengthLabel');

        let strength = 'Weak';
        let strengthClass = 'weak';

        if (strengthCount >= 5) {
            strength = 'Strong';
            strengthClass = 'strong';
        } else if (strengthCount >= 4) {
            strength = 'Good';
            strengthClass = 'good';
        } else if (strengthCount >= 3) {
            strength = 'Fair';
            strengthClass = 'fair';
        }

        if (progressEl) {
            progressEl.className = `strength-progress ${strengthClass}`;
        }

        if (labelEl) {
            labelEl.innerHTML = `Password strength: <strong>${strength}</strong>`;
        }
    }

    /**
     * Toggle password visibility
     */
    togglePasswordVisibility(e) {
        e.preventDefault();
        const targetId = e.currentTarget.dataset.target;
        const input = document.getElementById(targetId);
        const icon = e.currentTarget.querySelector('.eye-icon');

        if (input.type === 'password') {
            input.type = 'text';
            icon.textContent = '👁️‍🗨️';
        } else {
            input.type = 'password';
            icon.textContent = '👁️';
        }
    }

    /**
     * Setup bank autocomplete
     */
    setupBankAutocomplete() {
        const bankInput = document.getElementById('bankName');
        const bankList = document.getElementById('bankList');

        const banks = [
            'State Bank of India (SBI)',
            'HDFC Bank',
            'ICICI Bank',
            'Axis Bank',
            'Kotak Mahindra Bank',
            'Bank of Baroda',
            'Federal Bank',
            'IDBI Bank',
            'Punjab National Bank',
            'Union Bank of India',
            'Canara Bank',
            'Indian Bank',
            'IndusInd Bank',
            'RBL Bank',
            'IDFC Bank'
        ];

        if (!bankInput) return;

        bankInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            bankList.innerHTML = '';

            if (query.length === 0) {
                bankList.classList.remove('active');
                return;
            }

            const filtered = banks.filter(bank => bank.toLowerCase().includes(query));

            if (filtered.length === 0) {
                const item = document.createElement('li');
                item.className = 'autocomplete-item';
                item.textContent = 'No banks found';
                item.disabled = true;
                bankList.appendChild(item);
            } else {
                filtered.forEach(bank => {
                    const item = document.createElement('li');
                    item.className = 'autocomplete-item';
                    item.textContent = bank;
                    item.addEventListener('click', () => {
                        bankInput.value = bank;
                        bankList.innerHTML = '';
                        bankList.classList.remove('active');
                        this.validateField(bankInput);
                    });
                    bankList.appendChild(item);
                });
            }

            bankList.classList.add('active');
        });

        // Close on blur
        bankInput.addEventListener('blur', () => {
            setTimeout(() => {
                bankList.classList.remove('active');
            }, 200);
        });
    }

    /**
     * Setup password strength
     */
    setupPasswordStrength() {
        const passwordField = document.getElementById('password');
        if (passwordField) {
            // Initialize with password strength requirements visible
            this.updatePasswordStrength();
        }
    }

    /**
     * Setup DOB to age converter
     */
    setupDOBAge() {
        const dobInput = document.getElementById('dob');
        const ageInput = document.getElementById('age');

        if (!dobInput) return;

        dobInput.addEventListener('change', () => {
            const dob = new Date(dobInput.value);
            const today = new Date();
            let age = today.getFullYear() - dob.getFullYear();
            const monthDiff = today.getMonth() - dob.getMonth();

            if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dob.getDate())) {
                age--;
            }

            if (ageInput) {
                ageInput.value = age + ' years';
            }

            this.validateField(dobInput);
        });
    }

    /**
     * Check if age is valid (18+)
     */
    isValidAge(dobString) {
        const dob = new Date(dobString);
        const today = new Date();
        let age = today.getFullYear() - dob.getFullYear();
        const monthDiff = today.getMonth() - dob.getMonth();

        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dob.getDate())) {
            age--;
        }

        return age >= 18;
    }

    /**
     * Check name match between full name and account holder name
     */
    checkNameMatch() {
        const fullName = document.getElementById('fullName').value.toLowerCase().trim();
        const accountHolderName = document.getElementById('accountHolderName').value.toLowerCase().trim();
        const statusEl = document.getElementById('nameMatchStatus');

        if (!statusEl || !accountHolderName) return;

        statusEl.classList.remove('match', 'mismatch', 'checking');

        // Simple check - both names contain each other's key words
        const fullNameParts = fullName.split(' ');
        const accountNameParts = accountHolderName.split(' ');

        const matchCount = fullNameParts.filter(part => 
            accountNameParts.some(aPart => aPart === part)
        ).length;

        if (matchCount > 0) {
            statusEl.classList.add('match');
            statusEl.textContent = '✓ Name matches your full name';
        } else {
            statusEl.classList.add('mismatch');
            statusEl.textContent = '⚠️ Warning: Name does not match your full name. Please verify with your bank.';
        }
    }

    /**
     * Select role
     */
    selectRole(card) {
        document.querySelectorAll('.role-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        const input = card.querySelector('input[type="radio"]');
        if (input) {
            input.checked = true;
        }
    }

    /**
     * Populate summary card on final step
     */
    populateSummary() {
        const summaryEl = document.getElementById('summaryContent');
        if (!summaryEl) return;

        const summaryData = [
            { label: 'Full Name', key: 'full_name' },
            { label: 'Email', key: 'email' },
            { label: 'Phone', key: 'phone_number' },
            { label: 'Bank Name', key: 'bank_name' },
            { label: 'Account Type', key: 'account_type' },
            { label: 'Account Holder', key: 'account_holder_name' },
            { label: 'ID Type', key: 'id_type' },
            { label: 'Role', key: 'role' }
        ];

        summaryEl.innerHTML = summaryData
            .filter(item => this.formData[item.key])
            .map(item => `
                <div class="summary-item">
                    <span class="summary-item-label">${item.label}</span>
                    <span class="summary-item-value">${this.maskSensitiveData(item.key, this.formData[item.key])}</span>
                </div>
            `)
            .join('');
    }

    /**
     * Mask sensitive data for display
     */
    maskSensitiveData(key, value) {
        if (key === 'account_number') {
            const last4 = value.slice(-4);
            return `****${last4}`;
        }
        if (key === 'id_number') {
            const last3 = value.slice(-3);
            return `***${last3}`;
        }
        if (key === 'phone_number') {
            return value.replace(/(\d{2})(\d)(\d{2})(\d+)/, '$1*$2*$3*****');
        }
        return value;
    }

    /**
     * Handle form submission
     */
    async handleSubmit(e) {
        e.preventDefault();

        if (!this.validateCurrentStep()) {
            this.showStepError('Please correct all errors before submitting');
            return;
        }

        this.collectStepData();

        // Disable submit button
        this.submitBtn.disabled = true;
        this.submitBtn.innerHTML = '<span>⏳ Processing...</span>';

        try {
            // Prepare form data
            const formDataObj = new FormData(this.form);

            // Add CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            // Submit to backend
            const response = await fetch(this.form.action || '/auth/register/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formDataObj
            });

            if (response.ok) {
                this.showSuccess('Registration successful! Redirecting...');
                setTimeout(() => {
                    window.location.href = '/login/';
                }, 2000);
            } else {
                const errorData = await response.json();
                this.showServerErrors(errorData);
                this.submitBtn.disabled = false;
                this.submitBtn.innerHTML = '<span class="btn-icon">✓</span> Complete Registration';
            }
        } catch (error) {
            console.error('Submission error:', error);
            this.showStepError('An error occurred. Please try again.');
            this.submitBtn.disabled = false;
            this.submitBtn.innerHTML = '<span class="btn-icon">✓</span> Complete Registration';
        }
    }

    /**
     * Show step validation error
     */
    showStepError(message) {
        const errorEl = document.getElementById('formErrors');
        if (errorEl) {
            errorEl.innerHTML = `<h4>⚠️ Please fix the following errors:</h4><ul><li>${message}</li></ul>`;
            errorEl.classList.add('show');
        }
    }

    /**
     * Show server errors
     */
    showServerErrors(errorData) {
        const errorEl = document.getElementById('formErrors');
        if (errorEl) {
            let errorHTML = '<h4>Registration Error:</h4><ul>';
            
            if (typeof errorData === 'object') {
                Object.entries(errorData).forEach(([key, value]) => {
                    const message = Array.isArray(value) ? value[0] : value;
                    errorHTML += `<li>${message}</li>`;
                });
            } else {
                errorHTML += `<li>${errorData}</li>`;
            }
            
            errorHTML += '</ul>';
            errorEl.innerHTML = errorHTML;
            errorEl.classList.add('show');
        }
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        const errorEl = document.getElementById('formErrors');
        if (errorEl) {
            errorEl.innerHTML = `<div style="color: #00A86B; padding: 16px; background: #E8F5E9; border-radius: 8px;">✓ ${message}</div>`;
            errorEl.classList.add('show');
        }
    }
}

// Initialize on document ready
document.addEventListener('DOMContentLoaded', () => {
    window.registrationManager = new RegistrationFormManager();
    console.log('✅ Registration system ready');
});
