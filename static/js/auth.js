// Custom Authentication JavaScript

document.addEventListener('DOMContentLoaded', () => {
    // --- Form toggling ---
    const loginContainer = document.getElementById('login-form-container');
    const signupContainer = document.getElementById('signup-form-container');
    const forgotContainer = document.getElementById('forgot-form-container');
    
    document.getElementById('show-signup').addEventListener('click', (e) => {
        e.preventDefault();
        loginContainer.style.display = 'none';
        signupContainer.style.display = 'block';
    });
    
    document.getElementById('show-login').addEventListener('click', (e) => {
        e.preventDefault();
        signupContainer.style.display = 'none';
        loginContainer.style.display = 'block';
    });
    
    document.getElementById('show-forgot').addEventListener('click', (e) => {
        e.preventDefault();
        loginContainer.style.display = 'none';
        forgotContainer.style.display = 'block';
    });
    
    document.getElementById('show-login-from-forgot').addEventListener('click', (e) => {
        e.preventDefault();
        forgotContainer.style.display = 'none';
        loginContainer.style.display = 'block';
    });

    // --- Dynamic Signup Form ---
    const roleSelect = document.getElementById('role-select');
    const dynamicFields = document.getElementById('dynamic-fields');
    
    roleSelect.addEventListener('change', () => {
        const role = roleSelect.value;
        let fieldsHtml = '';
        
        if (role === 'intern' || role === 'supervisor') {
            fieldsHtml = `<input type="text" name="company" placeholder="Company Name" required>`;
        } else if (role === 'student') {
            fieldsHtml = `
                <input type="text" name="matricNumber" placeholder="Matric Number" required>
                <input type="text" name="school" placeholder="School Name" required>
                <input type="text" name="programme" placeholder="Programme" required>
                <input type="text" name="level" placeholder="Level (e.g., 400)" required>
            `;
        } else if (role === 'lecturer') {
            fieldsHtml = `
                <input type="text" name="school" placeholder="School Name" required>
                <input type="text" name="programme" placeholder="Programme" required>
            `;
        }
        
        dynamicFields.innerHTML = fieldsHtml;
    });

    // --- Signup Logic ---
    const signupForm = document.getElementById('signup-form');
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(signupForm);
        const data = Object.fromEntries(formData.entries());
        
        // Validate password
        if (data.password.length < 6) {
            showError('signup-error', 'Password must be at least 6 characters');
            return;
        }
        
        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                if (result.requires_verification) {
                    window.location.href = '/verify-email';
                } else {
                    window.location.href = '/dashboard';
                }
            } else {
                showError('signup-error', result.message);
            }
        } catch (error) {
            showError('signup-error', 'Registration failed. Please try again.');
        }
    });

    // --- Login Logic ---
    const loginForm = document.getElementById('login-form');
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            
            const result = await response.json();

            if (response.ok) {
                if (result.requires_verification) {
                    window.location.href = '/verify-email';
                } else {
                    window.location.href = '/dashboard';
                }
            } else {
                showError('login-error', result.message);
            }
        } catch (error) {
            showError('login-error', 'Login failed. Please try again.');
        }
    });
    
    // --- Forgot Password Logic ---
    const forgotForm = document.getElementById('forgot-form');
    forgotForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('forgot-email').value;
        
        try {
            const response = await fetch('/api/forgot-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                showSuccess('forgot-message', result.message);
            } else {
                showError('forgot-message', result.message);
            }
        } catch (error) {
            showError('forgot-message', 'Failed to send reset email. Please try again.');
        }
    });
    
    // Helper functions
    function showError(elementId, message) {
        const element = document.getElementById(elementId);
        element.textContent = message;
        element.className = 'error-message';
        element.style.display = 'block';
    }
    
    function showSuccess(elementId, message) {
        const element = document.getElementById(elementId);
        element.textContent = message;
        element.className = 'message';
        element.style.display = 'block';
    }
});