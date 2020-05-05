__vi_utils_version__ = "1.0.77"

from os import environ, popen #System
from sys import argv, exit, platform #System
from cryptography.fernet import Fernet #Crypto
from base64 import urlsafe_b64encode, b64encode, b64decode #Crypto
from cryptography.fernet import Fernet #Crypto
from cryptography.hazmat.backends import default_backend #Crypto
from cryptography.hazmat.primitives import hashes #Crypto
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC #Crypto
from xml.etree import ElementTree #Parse XML

#Part 1. Systems functions:	
def getMachine_addr(): #Motherboard's SN
	os_type = platform.lower()
	if "win" in os_type:
		command = "wmic bios get serialnumber"
	elif "linux" in os_type:
		command = "hal-get-property --udi /org/freedesktop/Hal/devices/computer --key system.hardware.uuid"
	elif "darwin" in os_type:
		command = "ioreg -l | grep IOPlatformSerialNumber"
	try:
		Machine_addr = popen(command).read().replace("\n","").replace("	","")
		Machine_addr = Machine_addr.replace(" ","").replace("SerialNumber","").replace("-","")
	except:
		Machine_addr = -1
	return Machine_addr

def getUser_name(): #Get domain\login_Hostname
	return environ['userdomain'] + '\\' + environ['username'] + "_" + environ['COMPUTERNAME']

def fromUserPass2Credentials(username,password): #Get base64 credentials from username & pass
	usrPass = (username + ':' + password).encode()
	usrCredentials = b64encode(usrPass).decode()
	return usrCredentials

def fromCredentials2UserPass(usrCredentials): #Get base64 username & pass from ucredentials
	usrPass = b64decode(usrCredentials)
	usrPass = usrPass.decode()
	username = usrPass[:usrPass.find(':')]
	password = usrPass[usrPass.find(':') + 1:]
	return username, password

def encrypt_data(ucce_credentials,ucce_server): #Encrypt credentials
	User_name = getUser_name()
	Machine_addr = getMachine_addr()
	text = "<connection>\n<credentials>" + ucce_credentials + "</credentials>\n"
	text = text + "<server>" + ucce_server +	"</server>\n" + "</connection>"
	text = text.encode()
	if Machine_addr == -1:
		encrypted_text = -1
	else:
		try:
			password = User_name + '_' + Machine_addr #unique for this Host & User only
			password = password.encode()
			kdf = PBKDF2HMAC(
				algorithm=hashes.SHA256(),
				length=32,
				salt=b"p!d(7U`kefb!'P3,o-qEYC&`/}E@AE",
				iterations=100000,
				backend=default_backend()
				)
			key = urlsafe_b64encode(kdf.derive(password))
			cipher = Fernet(key)
			encrypted_text = cipher.encrypt(text)
			encrypted_text = encrypted_text.decode()
		except:
			encrypted_text = -2
	return encrypted_text
	
def decrypt_data(filedata): #Decrypt credentials
	encrypted_text = filedata.read()
	User_name = getUser_name()
	Machine_addr = getMachine_addr()
	if Machine_addr == -1:
		decrypted_text = -1
	else:
		try:
			password = User_name + '_' + Machine_addr #unique for this Host & User only
			password = password.encode()
			encrypted_text = encrypted_text.encode()
			kdf = PBKDF2HMAC(
				algorithm=hashes.SHA256(),
				length=32,
				salt=b"p!d(7U`kefb!'P3,o-qEYC&`/}E@AE",
				iterations=100000,
				backend=default_backend()
				)
			key = urlsafe_b64encode(kdf.derive(password))
			cipher = Fernet(key)
			decrypted_text = cipher.decrypt(encrypted_text)
			decrypted_text = decrypted_text.decode()
		except:
			decrypted_text = -2
	return decrypted_text
	
def open_file(file_name): #Open file with properties
	try:
		f = open(file_name, "r")
	except FileNotFoundError as exception:
		f = -1
	except:
		f = -2
	return f
	
def save_file(file_name, text): #Save file with properties
	try:
		f = open(file_name, "w+")
		f.write(text)
		f.close()
		return True
	except:
		return False
		
def load_connection_data(filedata): #Load properties from file
	ucce_username = ""
	ucce_pass = ""
	ucce_server = ""
	ucce_credentials = ""
	is_all_fine = True
	error_text = ""
	try:
		root = ElementTree.fromstring(filedata)
		e_ucce_server = root.find('server')
		if not (e_ucce_server is None):
			ucce_server = e_ucce_server.text
		else:
			is_all_fine = False
			error_text = "Could't load server from connection properties."
		e_ucce_credentials = root.find('credentials')
		if not (e_ucce_credentials is None):
			ucce_credentials = e_ucce_credentials.text
		else:
			is_all_fine = False
			error_text = "Could't load credentials connection properties."
		ucce_username,ucce_pass = fromCredentials2UserPass(ucce_credentials)
	except Exception :
		is_all_fine = False
		error_text = "Error loading connection properties"
	return is_all_fine, error_text, ucce_username, ucce_pass, ucce_server
