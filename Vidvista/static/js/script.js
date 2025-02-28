// script.js

// Show login options
function showLoginOptions() {
    document.querySelector('.login-container').style.display = 'none';
    document.getElementById('login-options').style.display = 'block';
    document.getElementById('signup-form').style.display = 'none';
}

// Show signup form
function showSignupForm() {
    document.querySelector('.login-container').style.display = 'none';
    document.getElementById('signup-form').style.display = 'block';
    document.getElementById('login-options').style.display = 'none';
}

// Handle login with email
function loginWithEmail() {
    alert('Login with Email option clicked!');
    // Implement email login functionality here
}

// Handle login with Google
function loginWithGoogle() {
    alert('Login with Google option clicked!');
    // Implement Google login functionality here
}
