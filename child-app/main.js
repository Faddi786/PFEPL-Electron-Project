    const { app, BrowserWindow,exec, ipcMain, protocol, dialog, ipcRenderer } = require('electron');
    const { spawn } = require('child_process');
    const path = require('path');
    const fs = require('fs');
    const { CONNREFUSED } = require('dns');


    let id, password,email,name;
    // Function to create a new text file and log errors to it
    let dataString;
    function createWindow() {
        
        const mainWindow = new BrowserWindow({
            width: 800,
            height: 600,
            webPreferences: {
                preload: path.join(__dirname, 'preload2.js'),
                nodeIntegration: true,
                contextIsolation: false,
                userData: app.getPath('temp'),
                webSecurity: true // Setting webSecurity to true for better security
            }
        });
        mainWindow.maximize();
        const loginPath = 'login.html'; // Corrected the login path

        mainWindow.loadURL(`file://${__dirname}/${loginPath}`); // Corrected the loadURL call

        mainWindow.webContents.on('did-finish-load', () => {
            mainWindow.webContents.send('renderer-loaded');
        });

        // Listen for login form submission
        ipcMain.on('login-form-submitted', (event, formData) => {
            // Read data from data.txt file
            fs.readFile(path.join(__dirname, 'data.txt'), 'utf8', (err, data) => {
                if (err) {
                    console.error('Error reading data.txt:', err);
                    //ipcRenderer.send('python-error', `Error reading data.txt: ${err}`);
                    // Send validation failure message to renderer process
                    dialog.showErrorBox('Error', 'An error occurred. Please try again later.');
                    
                    return;
                }

                // Split the data into lines
                const lines = data.split('\n');
                

                // Parse lines to find ID and password
                lines.forEach(line => {
                    const [key, value] = line.split(':');
                    if (key.trim() === 'ID') {
                        id = value.trim();
                    } 
                    if (key.trim() === 'Password') {
                        password = value.trim();
                    }
                    if (key.trim() === 'Email') {
                        email = value.trim();
                    }
                    if (key.trim() === 'Name') {
                        name = value.trim();
                    }
                });

            // Perform validation
            if (id === formData.id && password === formData.password) {
                // Load browse.html into main window
                mainWindow.loadURL(`file://${__dirname}/browse.html`);
            } else {
                // Send invalid login response to renderer process
                event.sender.send('invalid-login-response', 'Invalid credentials. Please try again.');
                }           

                
            });
        });




            

            ipcMain.on('run-application', (event, formData) => {
                const exePath = path.join(__dirname, "..", 'f.py');
                const {droneName, siteName, rootFolder } = formData;
                const root_folder = formData.rootFolder
                console.log(formData);
                const flightNo = "FL123";


            
                const pythonProcess = spawn('python', [
                    exePath,
                    droneName,  
                    siteName,
                    name,
                    id,
                    email,
                    formData.rootFolder

                ]);
            
                pythonProcess.stdout.on('data', (data) => {
                    const output = data.toString().trim();  // Convert data to string and remove leading/trailing whitespace
                    try {
                        const outputData = JSON.parse(output);  // Parse JSON data sent from Python
                        console.log(outputData);  // Output data received from Python
                    } catch (error) {
                        console.error(`Error parsing JSON data: ${error}`);
                        console.log(`Executable output: ${output}`);  // Output the raw data for debugging
                    }
                });
                
                
            pythonProcess.stdout.on('data', (data) => {
                console.log(`Executable output: ${data}`);
            });
        
            pythonProcess.stderr.on('data', (data) => {
                const errorMessage = data.toString();
                console.error(`Error executing executable: ${errorMessage}`);


                
            });
        
            pythonProcess.on('error', (error) => {
                console.error(`Spawn process error: ${error}`);
                dialog.showErrorBox('Error', error.message);
                
            });
            pythonProcess.on('close', (code) => {
                console.log(`child process exited with code ${code}`);
            });
        
        });
    }

    // Register the 'app' protocol to serve files from the application directory
    app.whenReady().then(() => {
        protocol.registerFileProtocol('app', (request, callback) => {
            const filePath = request.url.replace('app://', ''); // Remove protocol
            callback({ path: path.normalize(`${__dirname}/${filePath}`) });
        });
        createWindow();
    });

    app.on('window-all-closed', () => {
        if (process.platform !== 'darwin') {
            app.quit();
        }
    });

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
