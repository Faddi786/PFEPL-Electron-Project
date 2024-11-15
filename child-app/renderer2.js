const { ipcRenderer } = require('electron');

// Add event listener to the form submission
document.getElementById('loginForm').addEventListener('submit', (event) => {
    event.preventDefault(); // Prevent default form submission
    
    // Get the form data
    const formData = {
        id: document.getElementById('idInput').value,
        password: document.getElementById('passwordInput').value
    };

    // Send form data to the main process
    ipcRenderer.send('login-form-submitted', formData);
});

// Listen for response from the main process (if any)
ipcRenderer.on('invalid-login-response', (event, response) => {
    // Handle the response from the main process
    document.getElementById('outputBox').value = response;
    outputBox.style.fontSize = '11px'; // Set the font size

});
