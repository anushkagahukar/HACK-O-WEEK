document.addEventListener('DOMContentLoaded', () => {
    // Check if already logged in -> redirect to dashboard
    if (localStorage.getItem('token')) {
        window.location.href = 'dashboard.html';
        return;
    }

    // Login Form Logic
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('login-btn');
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            btn.disabled = true;

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                const data = await fetchAPI('/auth/login', {
                    method: 'POST',
                    body: JSON.stringify({ email, password })
                });

                localStorage.setItem('token', data.token);
                showAlert('Login successful!', 'success');
                setTimeout(() => window.location.href = 'dashboard.html', 1000);
            } catch (error) {
                showAlert(error.message, 'error');
                btn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Login';
                btn.disabled = false;
            }
        });
    }

    // Signup Form Logic
    const signupForm = document.getElementById('signup-form');
    let isPasswordStrong = false;

    if (signupForm) {
        // Password Strength Check
        const passwordInput = document.getElementById('password');
        const strengthFill = document.getElementById('strength-fill');
        const strengthText = document.getElementById('strength-text');

        passwordInput.addEventListener('input', (e) => {
            const val = e.target.value;
            let strength = 0;
            
            if (val.length > 5) strength += 1;
            if (val.match(/[a-z]+/)) strength += 1;
            if (val.match(/[A-Z]+/)) strength += 1;
            if (val.match(/[0-9]+/)) strength += 1;
            if (val.match(/[$@#&!]+/)) strength += 1;

            switch(strength) {
                case 0:
                    strengthFill.style.width = '0';
                    strengthText.textContent = 'Enter password';
                    isPasswordStrong = false;
                    break;
                case 1:
                case 2:
                    strengthFill.style.width = '33%';
                    strengthFill.style.background = '#ef4444';
                    strengthText.textContent = 'Weak';
                    isPasswordStrong = false;
                    break;
                case 3:
                case 4:
                    strengthFill.style.width = '66%';
                    strengthFill.style.background = '#f59e0b';
                    strengthText.textContent = 'Medium';
                    isPasswordStrong = true;
                    break;
                case 5:
                    strengthFill.style.width = '100%';
                    strengthFill.style.background = '#10b981';
                    strengthText.textContent = 'Strong';
                    isPasswordStrong = true;
                    break;
            }
        });

        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm-password').value;

            if (password !== confirmPassword) {
                return showAlert('Passwords do not match', 'error');
            }

            if (!isPasswordStrong) {
                return showAlert('Please choose a stronger password', 'error');
            }

            const btn = document.getElementById('signup-btn');
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating...';
            btn.disabled = true;

            const userData = {
                name: document.getElementById('name').value,
                email: document.getElementById('email').value,
                age: document.getElementById('age').value,
                gender: document.getElementById('gender').value,
                phone: document.getElementById('phone').value,
                password: password
            };

            try {
                const data = await fetchAPI('/auth/signup', {
                    method: 'POST',
                    body: JSON.stringify(userData)
                });

                localStorage.setItem('token', data.token);
                showAlert('Account created successfully!', 'success');
                setTimeout(() => window.location.href = 'dashboard.html', 1500);
            } catch (error) {
                showAlert(error.message, 'error');
                btn.innerHTML = '<i class="fas fa-user-plus"></i> Sign Up';
                btn.disabled = false;
            }
        });
    }
});

// Toggle Password Visibility
window.togglePasswordVisibility = function(inputId, iconId) {
    const input = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
};
