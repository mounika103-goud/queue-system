// UI Enhancement Functions

// Form Validation
class FormValidator {
    static validateForm(formId) {
        const form = document.getElementById(formId);
        if (!form) return true;

        const inputs = form.querySelectorAll('[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!input.value.trim()) {
                this.showError(input, 'This field is required');
                isValid = false;
            } else {
                this.clearError(input);
            }
        });

        return isValid;
    }

    static showError(element, message) {
        element.classList.add('is-invalid');
        
        let errorDiv = element.nextElementSibling;
        if (!errorDiv || !errorDiv.classList.contains('error-message')) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'error-message text-danger small mt-1';
            element.parentNode.insertBefore(errorDiv, element.nextSibling);
        }
        errorDiv.textContent = message;
    }

    static clearError(element) {
        element.classList.remove('is-invalid');
        const errorDiv = element.nextElementSibling;
        if (errorDiv && errorDiv.classList.contains('error-message')) {
            errorDiv.remove();
        }
    }
}

// Table Enhancements
class TableManager {
    static makeSearchable(tableId) {
        const table = document.getElementById(tableId);
        if (!table) return;

        const searchContainer = document.createElement('div');
        searchContainer.className = 'mb-3';
        searchContainer.innerHTML = `
            <input type="text" class="form-control" placeholder="Search table..." id="${tableId}-search">
        `;

        table.parentNode.insertBefore(searchContainer, table);

        const searchInput = document.getElementById(`${tableId}-search`);
        searchInput.addEventListener('keyup', (e) => {
            const searchText = e.target.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr');

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchText) ? '' : 'none';
            });
        });
    }

    static makeSortable(tableId) {
        const table = document.getElementById(tableId);
        if (!table) return;

        const headers = table.querySelectorAll('thead th');
        
        headers.forEach((header, index) => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => {
                this.sortTable(tableId, index);
            });
        });
    }

    static sortTable(tableId, columnIndex) {
        const table = document.getElementById(tableId);
        const rows = Array.from(table.querySelectorAll('tbody tr'));
        
        const isAscending = !table.dataset.sortAscending;
        table.dataset.sortAscending = isAscending;

        rows.sort((a, b) => {
            const aCell = a.cells[columnIndex].textContent;
            const bCell = b.cells[columnIndex].textContent;

            if (!isNaN(aCell) && !isNaN(bCell)) {
                return isAscending ? aCell - bCell : bCell - aCell;
            }

            return isAscending 
                ? aCell.localeCompare(bCell) 
                : bCell.localeCompare(aCell);
        });

        rows.forEach(row => table.querySelector('tbody').appendChild(row));
    }
}

// Modal Helpers
class ModalHelper {
    static openModal(modalId) {
        const modal = new bootstrap.Modal(document.getElementById(modalId));
        modal.show();
    }

    static closeModal(modalId) {
        const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
        if (modal) modal.hide();
    }

    static confirmAction(message, callback) {
        if (confirm(message)) {
            callback();
        }
    }
}

// Toast Notifications
class ToastNotification {
    static show(message, type = 'info', duration = 3000) {
        const toastContainer = document.getElementById('toast-container') || this.createContainer();
        
        const toastId = 'toast-' + Date.now();
        const toast = document.createElement('div');
        toast.id = toastId;
        toast.className = `alert alert-${type} alert-dismissible fade show`;
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        toastContainer.appendChild(toast);

        if (duration) {
            setTimeout(() => {
                const element = document.getElementById(toastId);
                if (element) {
                    const alert = new bootstrap.Alert(element);
                    alert.close();
                }
            }, duration);
        }
    }

    static createContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            width: 300px;
            max-width: 100%;
        `;
        document.body.appendChild(container);
        return container;
    }

    static success(message) {
        this.show(message, 'success');
    }

    static error(message) {
        this.show(message, 'danger');
    }

    static warning(message) {
        this.show(message, 'warning');
    }

    static info(message) {
        this.show(message, 'info');
    }
}

// Loading State Helper
class LoadingState {
    static show(buttonId) {
        const button = document.getElementById(buttonId);
        if (!button) return;

        button.disabled = true;
        button.dataset.originalText = button.innerHTML;
        button.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            Loading...
        `;
    }

    static hide(buttonId) {
        const button = document.getElementById(buttonId);
        if (!button) return;

        button.disabled = false;
        button.innerHTML = button.dataset.originalText || 'Submit';
    }
}

// DateTime Formatter
class DateTimeFormatter {
    static formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    static formatTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }

    static formatDateTime(dateString) {
        return `${this.formatDate(dateString)} ${this.formatTime(dateString)}`;
    }

    static timeAgo(dateString) {
        const date = new Date(dateString);
        const seconds = Math.floor((new Date() - date) / 1000);

        if (seconds < 60) return 'Just now';
        if (seconds < 3600) return `${Math.floor(seconds / 60)} minutes ago`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`;
        return `${Math.floor(seconds / 86400)} days ago`;
    }
}

// Initialize all UI enhancements
document.addEventListener('DOMContentLoaded', function() {
    // Make all tables with class 'searchable' searchable
    document.querySelectorAll('table.searchable').forEach(table => {
        TableManager.makeSearchable(table.id);
    });

    // Make all tables with class 'sortable' sortable
    document.querySelectorAll('table.sortable').forEach(table => {
        TableManager.makeSortable(table.id);
    });

    // Setup form validation
    document.querySelectorAll('form[data-validate]').forEach(form => {
        form.addEventListener('submit', (e) => {
            if (!FormValidator.validateForm(form.id)) {
                e.preventDefault();
            }
        });
    });

    // Format all datetime elements
    document.querySelectorAll('[data-datetime]').forEach(element => {
        const dateString = element.getAttribute('data-datetime');
        element.textContent = DateTimeFormatter.formatDateTime(dateString);
    });

    console.log('UI enhancements initialized');
});
