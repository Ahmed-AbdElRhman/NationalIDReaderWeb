 // Global state
 let currentUser = null;
 let subscriptionData = null;
 const API_BASE = 'http://127.0.0.1:5000';
 // DOM elements
 const loginPage = document.getElementById('login-page');
 const dashboardPage = document.getElementById('dashboard-page');
 const loginForm = document.getElementById('login-form');
 const changePasswordForm = document.getElementById('change-password-form');
 const alertContainer = document.getElementById('global-alert-container');

 // Initialize the application
 document.addEventListener('DOMContentLoaded', function() {
     // Check if user is already logged in
     const savedUser = localStorage.getItem('adminUser');
     if (savedUser) {
         currentUser = JSON.parse(savedUser);
         showDashboard();
         loadSubscriptionData();
     }

     // Setup event listeners
     setupEventListeners();
 });

 // Setup event listeners
 function setupEventListeners() {
     // Login form
     loginForm.addEventListener('submit', handleLogin);
     
     // Navigation
     document.querySelectorAll('.nav-link[data-section]').forEach(link => {
         link.addEventListener('click', function(e) {
             e.preventDefault();
             showSection(this.getAttribute('data-section'));
         });
     });
     
     // Logout button
     document.getElementById('logout-btn').addEventListener('click', handleLogout);
     
     // Change password form
     changePasswordForm.addEventListener('submit', handleChangePassword);
     
     // Validate subscription button
     document.getElementById('validate-subscription-btn').addEventListener('click', validateSubscription);
     
     // Renew subscription button
     document.getElementById('renew-subscription-btn').addEventListener('click', renewSubscription);
 }

 // Show alert message
 function showAlert(message, type = 'info') {
     const alert = document.createElement('div');
     alert.className = `alert alert-${type} alert-dismissible fade show`;
     alert.innerHTML = `
         ${message}
         <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
     `;
     
     alertContainer.appendChild(alert);
     
     // Auto remove after 5 seconds
     setTimeout(() => {
         if (alert.parentNode) {
             alert.remove();
         }
     }, 5000);
 }

 // Show a specific section
 function showSection(sectionName) {
     // Hide all sections
     document.querySelectorAll('.content-section').forEach(section => {
         section.classList.add('d-none');
     });
     
     // Remove active class from all nav links
     document.querySelectorAll('.nav-link').forEach(link => {
         link.classList.remove('active');
     });
     
     // Show the selected section
     document.getElementById(`${sectionName}-section`).classList.remove('d-none');
     
     // Activate the corresponding nav link
     document.querySelector(`.nav-link[data-section="${sectionName}"]`).classList.add('active');
     
     // Update page title
     document.getElementById('page-title').textContent = 
         sectionName === 'overview' ? 'Dashboard Overview' :
         sectionName === 'subscription' ? 'Subscription Management' :
         sectionName === 'settings' ? 'Settings' : 'Dashboard';
 }

 // Handle login
 async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const formData = new FormData();
    if (!username || !password) {
        showAlert('Please enter both username and password', 'warning');
        return;
    }
    formData.append('username', username);
    formData.append('password', password);
    try {
        // Simulate API call - replace with actual API call
        // const response = await fakeApiCall('/api/login', {
        //     username,
        //     password
        // });
        const response = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Login failed:', errorText);
            throw new Error(`${errorText}`);
        }
        currentUser = { username };
        localStorage.setItem('adminUser', JSON.stringify(currentUser));
        // authToken = responseData.token || 'dummy-token'; // Replace with actual token field from your API
        // localStorage.setItem('authToken', authToken);
        showDashboard();
        loadSubscriptionData();
        showAlert('Login successful!', 'success');
    } catch (error) {
        showAlert('Login failed. Please try again.'+ error.message, 'danger');
        console.error('Login failed. Please try again.', error);
    }
 }

 // Handle logout
 async function handleLogout(e) {
    e.preventDefault();

    try {
        // Simulate API call - replace with actual API call
        // const response = await fakeApiCall('/api/login', {
        //     username,
        //     password
        // });
        const response = await fetch(`${API_BASE}/logout`, {
            method: 'GET',
        });
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`${errorText}`);
        }
        currentUser = null;
        localStorage.removeItem('adminUser');
        dashboardPage.classList.add('d-none');
        loginPage.classList.remove('d-none');
        
        showAlert('You have been logged out', 'info');
    } catch (error) {
        showAlert('Unable to logout'+ error.message, 'danger');
        console.error('Unable to logout', error);
    }
}
// Handle logout
// function handleLogout(e) {
//     e.preventDefault();
    
//     currentUser = null;
//     localStorage.removeItem('adminUser');
    
//     dashboardPage.classList.add('d-none');
//     loginPage.classList.remove('d-none');
    
//     showAlert('You have been logged out', 'info');
// }

 // Show dashboard
 function showDashboard() {
     loginPage.classList.add('d-none');
     dashboardPage.classList.remove('d-none');
     
     // Show overview section by default
     showSection('overview');
 }
  // Load subscription data
 async function loadSubscriptionData() {
    try {
        // Simulate API call - replace with actual API call
        const response = await fetch(`${API_BASE}/admin/subscription`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                // Add authorization header if needed
                // 'Authorization': `Bearer ${getAuthToken()}`
            }
        });
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`${errorText}`);
        }
       // Parse the JSON response
       const responseData = await response.json();
        
       console.log('Subscription data loaded successfully:', responseData);
       
       // Check if the response has the expected structure
       if (responseData && responseData.data) {
           subscriptionData = responseData.data;
           updateSubscriptionUI();
       } else {
           throw new Error('Invalid response format from server');
       }
    } catch (error) {
        showAlert('Error loading subscription data'+ error.message, 'danger');
        console.error('Error loading subscription data', error);
    }
}

 // Update subscription UI
 function updateSubscriptionUI() {
     if (!subscriptionData) return;
     
     // Update overview cards
     document.getElementById('total-scans').textContent = subscriptionData.total_scans;
     document.getElementById('status').textContent = subscriptionData.is_active ? 'Active' : 'Inactive';
     document.getElementById('status').className = `h5 mb-0 font-weight-bold text-gray-800 ${subscriptionData.is_active ? 'text-success' : 'text-danger'}`;
     
     // Calculate expiry date
     const installDate = new Date(subscriptionData.install_date);
     const expiryDate = new Date(installDate);
     expiryDate.setDate(expiryDate.getDate() + subscriptionData.expiry_days);
     document.getElementById('expiry-date').textContent = expiryDate.toLocaleDateString();
     
     // Calculate remaining scans
     const remainingScans = Math.max(0, subscriptionData.max_scans - subscriptionData.total_scans);
     document.getElementById('scans-remaining').textContent = remainingScans;
     
     // Update subscription status badge
     const statusBadge = document.getElementById('subscription-status');
     statusBadge.classList.remove('d-none');
     
     if (subscriptionData.is_active) {
         if (remainingScans > 0 && new Date() < expiryDate) {
             statusBadge.innerHTML = `<span class="badge bg-success subscription-badge">Active</span>`;
         } else {
             statusBadge.innerHTML = `<span class="badge bg-warning subscription-badge">Expired/Limit Reached</span>`;
         }
     } else {
         statusBadge.innerHTML = `<span class="badge bg-danger subscription-badge">Inactive</span>`;
     }
     
     // Update form values
     document.getElementById('expiry-days').value = subscriptionData.expiry_days;
     document.getElementById('max-scans').value = subscriptionData.max_scans;
 }

 // Handle change password
 async function handleChangePassword(e) {
     e.preventDefault();
     
     const currentPassword = document.getElementById('current-password').value;
     const newPassword = document.getElementById('new-password').value;
     const confirmPassword = document.getElementById('confirm-password').value;
     
     if (newPassword !== confirmPassword) {
         showAlert('New passwords do not match', 'danger');
         return;
     }
     
     try {
         // Simulate API call - replace with actual API call
         const response = await fakeApiCall('/api/change-password', {
             currentPassword,
             newPassword
         });
         
         if (response.success) {
             showAlert('Password changed successfully', 'success');
             changePasswordForm.reset();
             showSection('overview');
         } else {
             showAlert('Failed to change password. Please check your current password.', 'danger');
         }
     } catch (error) {
         showAlert('Error changing password', 'danger');
     }
 }

 // Validate subscription
 async function validateSubscription() {
     try {
         // Simulate API call - replace with actual API call
         const response = await fakeApiCall('/api/validate-subscription');
         
         if (response.success) {
             if (response.valid) {
                 showAlert('Subscription is valid and active', 'success');
             } else {
                 showAlert('Subscription is invalid or expired', 'warning');
             }
         } else {
             showAlert('Failed to validate subscription', 'danger');
         }
     } catch (error) {
         showAlert('Error validating subscription', 'danger');
     }
 }

 // Renew subscription
 async function renewSubscription() {
     const expiryDays = parseInt(document.getElementById('expiry-days').value);
     const maxScans = parseInt(document.getElementById('max-scans').value);

     const formData = new FormData();
     if (!expiryDays || !maxScans) {
         showAlert('Please enter both expiryDays and maxScans', 'warning');
         return;
     }
     formData.append('expiryDays', expiryDays);
     formData.append('maxScans', maxScans);

     if (isNaN(expiryDays) || expiryDays < 1 || isNaN(maxScans) || maxScans < 1) {
         showAlert('Please enter valid values for expiry days and max scans', 'warning');
         return;
     }
     
     try {
         const response = await fetch(`${API_BASE}/admin/renewsubscription`, {
            method: 'GET',
            headers: {'Content-Type': 'application/json'},
            body: formData
            
        });
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`${errorText}`);
        }
       // Parse the JSON response
        const responseData = await response.json();
        showAlert('Subscription renewed successfully', 'success');
        loadSubscriptionData(); // Reload data
        showSection('overview'); // Go back to overview
     } catch (error) {
        console.error('Error renewing subscription', error);
         showAlert('Error renewing subscription', 'danger');
     }
 }

 // Fake API call function (replace with actual API calls)
 async function fakeApiCall(endpoint, data = null) {
     // Simulate network delay
     await new Promise(resolve => setTimeout(resolve, 500));
     
     // Mock responses based on endpoint
     switch(endpoint) {
         case '/api/login':
             if (data.username === 'admin' && data.password === 'password') {
                 return { success: true, user: { username: 'admin' } };
             } else {
                 return { success: false, error: 'Invalid credentials' };
             }
         
         case '/api/subscription':
             return {
                 success: true,
                 data: {
                     id: 1,
                     install_date: new Date().toISOString(),
                     total_scans: 10,
                     is_active: true,
                     expiry_days: 365,
                     max_scans: 15
                 }
             };
         
         case '/api/change-password':
             if (data.currentPassword === 'password') {
                 return { success: true };
             } else {
                 return { success: false, error: 'Current password is incorrect' };
             }
         
         case '/api/validate-subscription':
             return { success: true, valid: true };
         
         case '/api/renew-subscription':
             return { success: true };
         
         default:
             return { success: false, error: 'Unknown endpoint' };
     }
 }