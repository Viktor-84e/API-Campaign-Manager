# API-Campaign-Manager
API Campaign Manager for cisco Cisco Unified Contact Center Enterprise
# Use Case Description
Utility helps to work with outbound option campaigns created via API (create/modify/delete). Because it's impossible to do with standard configuration manager.<BR>
After you entered connections settings in "Connection\Settings" tab, API-Campaign-Manager encrypt this data and store to file. This file could be opened & decrypted only on the same PC and for same user 
# Installation
There are 2 choices:
1) You could install packages:<BR>
	Python: https://www.python.org/downloads/ <BR>
	PyQt5: https://www.riverbankcomputing.com/software/pyqt/download5 <BR>
	requests: https://github.com/psf/requests <BR>
	cryptography: https://github.com/pyca/cryptography <BR>
After that copy Main.py, GUI.py, vi_utils.py and logo.JPG to your local PC and run Main.py <BR>
2) Also there is Main.exe - utility's version compiled for Qindows, you could try to use it. It doesn't need installation.
![Screenshot](screen.jpg?raw=true "Screenshot")