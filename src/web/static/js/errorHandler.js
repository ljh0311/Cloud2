// Global Error Handler

// Setup error handling when the document is ready
document.addEventListener('DOMContentLoaded', function() {
    setupGlobalErrorHandling();
});

function setupGlobalErrorHandling() {
    // Global error handler for uncaught exceptions
    window.onerror = function(message, source, lineno, colno, error) {
        console.error('Global error:', { message, source, lineno, colno, error });
        showErrorNotification(message, source, lineno);
        return true; // Prevents default error handling
    };

    // Handle promise rejections
    window.addEventListener('unhandledrejection', function(event) {
        console.error('Unhandled Promise Rejection:', event.reason);
        showErrorNotification('Async Error', event.reason.message || 'Unknown async error');
    });

    // Add support for reporting API if available
    if ('ReportingObserver' in window) {
        const observer = new ReportingObserver((reports) => {
            for (const report of reports) {
                console.log('Report to server:', report);
            }
        }, {buffered: true});
        observer.observe();
    }

    console.info('Global error handling initialized');
}

function showErrorNotification(message, source, lineno) {
    // Only show error notifications in development environment
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        const errorContainer = document.getElementById('error-container') || createErrorContainer();
        
        const errorElement = document.createElement('div');
        errorElement.className = 'alert alert-danger alert-dismissible fade show';
        errorElement.innerHTML = `
            <strong>JavaScript Error:</strong> ${escapeHtml(message)}
            ${source ? `<br><small>Source: ${escapeHtml(source)}${lineno ? ` (line ${lineno})` : ''}</small>` : ''}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        errorContainer.appendChild(errorElement);
        
        // Auto-remove after 15 seconds
        setTimeout(() => {
            if (errorElement.parentNode) {
                errorElement.classList.remove('show');
                setTimeout(() => errorElement.remove(), 500);
            }
        }, 15000);
        
        // Initialize Bootstrap's alert dismissal
        if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
            new bootstrap.Alert(errorElement);
        }
    }
}

function createErrorContainer() {
    const errorContainer = document.createElement('div');
    errorContainer.id = 'error-container';
    errorContainer.style.cssText = 'position: fixed; bottom: 20px; right: 20px; max-width: 400px; z-index: 9999;';
    document.body.appendChild(errorContainer);
    return errorContainer;
}

function escapeHtml(unsafe) {
    return unsafe
        .toString()
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
} 