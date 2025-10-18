function showForm(formId) {
  const registerForm = document.getElementById('registerForm');
  const loginForm = document.getElementById('loginForm');

  if (formId === 'register') {
    registerForm.classList.remove('hidden');
    loginForm.classList.add('hidden');

    // Fetch default register data if needed
    fetch('/form_data/register')
      .then(response => {
        if (!response.ok) throw new Error('Failed to fetch register data');
        return response.json();
      })
      .then(data => {
        if (data.defaultRole) {
          registerForm.querySelector('select[name="role"]').value = data.defaultRole;
        }
        if (data.defaultName) {
          registerForm.querySelector('input[name="name"]').value = data.defaultName;
        }
        if (data.defaultEmail) {
          registerForm.querySelector('input[name="email"]').value = data.defaultEmail;
        }
      })
      .catch(error => {
        console.error('Error loading register form data:', error);
      });

  } else if (formId === 'login') {
    loginForm.classList.remove('hidden');
    registerForm.classList.add('hidden');

    // Fetch default login data if needed
    fetch('/form_data/login')
      .then(response => {
        if (!response.ok) throw new Error('Failed to fetch login data');
        return response.json();
      })
      .then(data => {
        if (data.defaultEmail) {
          loginForm.querySelector('input[name="email"]').value = data.defaultEmail;
        }
      })
      .catch(error => {
        console.error('Error loading login form data:', error);
      });
  }
}

// Show register form by default on page load
document.addEventListener('DOMContentLoaded', () => {
  showForm('register');
});

// Client-side validation before submit — prevents form submission if invalid
document.getElementById('registerForm').addEventListener('submit', function(event) {
  const role = this.querySelector('select[name="role"]').value;
  const name = this.querySelector('input[name="name"]').value.trim();
  const email = this.querySelector('input[name="email"]').value.trim();
  const password = this.querySelector('input[name="password"]').value;

  if (!role || !name || !email || !password) {
    alert('Please fill in all required registration fields.');
    event.preventDefault();
  }
});

document.getElementById('loginForm').addEventListener('submit', function(event) {
  const email = this.querySelector('input[name="email"]').value.trim();
  const password = this.querySelector('input[name="password"]').value;

  if (!email || !password) {
    alert('Please fill in all required login fields.');
    event.preventDefault();
  }
});
