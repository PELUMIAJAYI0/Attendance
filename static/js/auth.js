// static/js/auth.js (CORRECTED VERSION)

// Initialize Firebase
if (typeof firebaseConfig !== 'undefined') {
    firebase.initializeApp(firebaseConfig);
}
document.addEventListener('DOMContentLoaded', () => {
    // --- Form toggling (no changes here) ---
    const loginContainer = document.getElementById('login-form-container');
    const signupContainer = document.getElementById('signup-form-container');
    const forgotContainer = document.getElementById('forgot-form-container');
    document.getElementById('show-signup').addEventListener('click', (e) => { e.preventDefault(); loginContainer.style.display = 'none'; signupContainer.style.display = 'block'; });
    document.getElementById('show-login').addEventListener('click', (e) => { e.preventDefault(); signupContainer.style.display = 'none'; loginContainer.style.display = 'block'; });
    document.getElementById('show-forgot').addEventListener('click', (e) => { e.preventDefault(); loginContainer.style.display = 'none'; forgotContainer.style.display = 'block'; });
    document.getElementById('show-login-from-forgot').addEventListener('click', (e) => { e.preventDefault(); forgotContainer.style.display = 'none'; loginContainer.style.display = 'block'; });

    // --- Dynamic Signup Form (no changes here) ---
    // (This part is fine as it is)
    const roleSelect = document.getElementById('role-select');
    const dynamicFields = document.getElementById('dynamic-fields');
    roleSelect.addEventListener('change', () => {
        const role = roleSelect.value;
        let fieldsHtml = '';
        if (role === 'intern' || role === 'supervisor') {
            fieldsHtml = `<input type="text" name="company" placeholder="Company Name" required>`;
        } else if (role === 'student') {
            fieldsHtml = `<input type="text" name="matricNumber" placeholder="Matric Number" required><input type="text" name="school" placeholder="School Name" required><input type="text" name="programme" placeholder="Programme" required><input type="text" name="level" placeholder="Level (e.g., 400)" required>`;
        } else if (role === 'lecturer') {
             fieldsHtml = `<input type="text" name="school" placeholder="School Name" required><input type="text" name="programme" placeholder="Programme" required>`;
        }
        dynamicFields.innerHTML = fieldsHtml;
    });

    // --- Signup Logic ---
    const signupForm = document.getElementById('signup-form');
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(signupForm);
        const data = Object.fromEntries(formData.entries());
        
        try {
            // Check if the user already exists
            const methods = await firebase.auth().fetchSignInMethodsForEmail(data.email);
            if (methods && methods.length > 0) {
                // User already exists, display an error and stop
                document.getElementById('signup-error').textContent = 'The email address is already in use. Please log in instead.';
                document.getElementById('signup-error').style.display = 'block';
                return; // Stop the signup process
            }

            // User does not exist, proceed with creating the user
             const userCredential = await firebase.auth().createUserWithEmailAndPassword(data.email, data.password);
            
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();

            if (!response.ok) throw new Error(result.message);
            
            alert('Registration successful! Please log in.');
            window.location.href = '/dashboard';

        } catch (error) {
            document.getElementById('signup-error').textContent = error.message;
            document.getElementById('signup-error').style.display = 'block';
        }
    });

    // --- Login Logic ---
    const loginForm = document.getElementById('login-form');
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        try {
            // Use firebase.auth() instead of just auth
            const userCredential = await firebase.auth().signInWithEmailAndPassword(email, password);
            const idToken = await userCredential.user.getIdToken();

            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ idToken: idToken })
            });
            const result = await response.json();

            if (!response.ok) throw new Error(result.message);

            window.location.href = '/dashboard';

        } catch (error) {
            document.getElementById('login-error').textContent = error.message;
            document.getElementById('login-error').style.display = 'block';
        }
    });
    
    // --- Forgot Password Logic ---
    const forgotForm = document.getElementById('forgot-form');
    forgotForm.addEventListener('submit', async(e) => {
        e.preventDefault();
        const email = document.getElementById('forgot-email').value;
        const messageDiv = document.getElementById('forgot-message');
        
        try {
            // Use firebase.auth() instead of just auth
            await firebase.auth().sendPasswordResetEmail(email);
            messageDiv.textContent = 'Success! Check your email for a password reset link.';
            messageDiv.className = 'message';
            messageDiv.style.display = 'block';
        } catch(error) {
            messageDiv.textContent = error.message;
            messageDiv.className = 'error-message';
            messageDiv.style.display = 'block';
        }
    });
}
)