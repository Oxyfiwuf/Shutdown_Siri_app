The project was implemented for remote shutdown and cancellation of a PC with a specified delay using an iPhone and Siri via the Shortcuts app. 
The system uses a client-server architecture hosted on Railway. 
The FastAPI framework is used on the server to handle HTTP requests and WebSocket connections, while the client uses websocket-client to maintain a persistent connection, pycaw for system volume control, and winotify for notifications. 
The client is compiled into an executable using PyInstaller and runs in the background with automatic startup.

To shut down the PC, send a POST request to the server with the command "sleep" and the desired delay in minutes. 
The server validates the API key and forwards the command to the connected client, which executes the shutdown. 
To cancel the operation, send a request with the command "cancel", which aborts the scheduled shutdown on the client.
However, to use it, you also need to deploy server.py to your server, specify your API_KEY in the server's env, get the URL, and add it as a custom environment variable, and optionally compile client.py into an exe.
