const { ipcRenderer } = require('electron');

// Function to update output box with the provided message
function updateOutputBox(message) {
    const outputBox = document.getElementById('outputBox');
    outputBox.value = message;
}
// Function to update output box with "Please wait" message
function showPleaseWait() {
    const outputBox = document.getElementById('outputBox');
    outputBox.value = 'Please wait...';
}

// Function to update output box with "Please wait" message
function invalid(message) {
    const outputBox = document.getElementById('outputBox');
    outputBox.value = message;
    outputBox.style.color = "red"; // Change text color to green
    outputBox.style.fontSize = '11px'; // Set font size to 14px (adjust as needed)

}

// Function to check if the input value is empty
function isEmpty(inputValue) {
    return !inputValue.trim(); // Return true if the input value is empty or contains only whitespace
}

document.getElementById('generateOptions').addEventListener('click', () => {
    const count = document.getElementById('countInput').valueAsNumber;
    const browseOptionsDiv = document.getElementById('browseOptions');
    browseOptionsDiv.innerHTML = ''; // Clear previous options
    
    for (let i = 0; i < count; i++) {
        const optionLabel = document.createElement('label');
        optionLabel.textContent = `Select Directory ${i + 1}: `;
        optionLabel.classList.add('browse-label'); // Add the browse-label class

        const input = document.createElement('input');
        input.type = 'text';
        input.placeholder = 'Enter browse path...';
        input.classList.add('browse-path-input');
        
        browseOptionsDiv.appendChild(optionLabel);
        browseOptionsDiv.appendChild(input);
        browseOptionsDiv.appendChild(document.createElement('br'));
    }
});




// Listen for click event on the "Run Application" button
document.getElementById('run_application').addEventListener('click', () => {
    // Retrieve form data
    const browsePathInputs = document.querySelectorAll('.browse-path-input');
    let rootFolder = '';
    let valuesSet = new Set(); // Using a Set to store unique values
    let duplicateFound = false; // Flag to track duplicate values

    browsePathInputs.forEach((input, index) => {
        const path = input.value.trim();
        if (valuesSet.has(path)) {
            // If the value is already in the set, set duplicateFound flag to true
            duplicateFound = true;
            return; // Exit the loop early
        } else {
            // Add the value to the set if it's not a duplicate
            valuesSet.add(path);
            if (index === 0) {
                // If it's the first path, don't prepend a comma
                rootFolder += path;
            } else {
                // For subsequent paths, prepend a comma
                rootFolder += ',' + path;
            }
        }
    }); // <-- Added closing bracket for forEach loop

    if (duplicateFound) {
        // If duplicate values are found, set output to 'Duplicate values found'
        const outputBox = document.getElementById('outputBox');
        outputBox.value = 'Duplicate values found';
        outputBox.style.color = "red";
        outputBox.style.fontSize = '11px';
        return; // Exit the function early
    }



    const droneName = document.getElementById('drone_name').value;
    const siteName = document.getElementById('site_name').value;


    // Check if any input field is empty

    if (isEmpty(droneName)) {
        invalid('Please enter drone name.');
        return; // Stop execution if drone name is empty
    }
    if (isEmpty(siteName)) {
        invalid('Please enter site name.');
        return; // Stop execution if site name is empty
    }


    const outputBox = document.getElementById('outputBox');
    outputBox.value = "Please check command prompt";
    outputBox.style.color = "green"; // Change text color to green
    ipcRenderer.send('run-application', {  droneName, siteName, rootFolder });
    outputBox.style.fontSize = '11px'; // Set font size to 14px (adjust as needed)
});


// Listen for 'python-error' event from main process
ipcRenderer.on('python-error', (event, errorMessage) => {
    // Update the output box with the error message
    updateOutputBox(errorMessage);
});
