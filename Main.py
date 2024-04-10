#Define global variables
__version__ = "1.3.2"
is_all_fine = True
error_text = ""
canCreate = False
canUpdate = False
canDelete = False
campaigns_array = []
campaigns_new_array = []
campaigns_del_array = []
timezones_array = []
skillgroups_array = []
ucce_username = "username@domain (with dots)"
ucce_pass = "password"
ucce_server = "server@domain (with dots)"
ucce_sql_username = "domain\\username"
ucce_sql_pass = "password"
ucce_sql_enable = False
ucce_sql_NT_auth = True
ucce_sql_port = "1433"
ucce_instance = ""

#Try to load all necessary libs
from PyQt5 import QtWidgets	#GUI
from PyQt5.QtCore import Qt #id in listWidgetItems
from PyQt5.QtCore import QTimer #make buttons temporary disabled
from copy import deepcopy #deepcopy for nested arrays
from random import randint #Generate name & id for new campaign
from datetime import date, time, datetime, timedelta #compare dates
import requests #HTTP
from pyodbc import connect #SQL
from vi_utils import * #Global functions 4 this project
from GUI import Ui_MainWindow, About_Dialog, Connection_Dialog

class CampaignManagerApp(QtWidgets.QMainWindow, Ui_MainWindow):
	def __init__(self): #Initialize Main Window
		super().__init__()
		self.setupUi(self)  #Initialize main window
		
		global is_all_fine, error_text, ucce_username, ucce_pass, ucce_server
		global ucce_sql_username, ucce_sql_pass, ucce_sql_enable, ucce_sql_NT_auth
		global ucce_instance, ucce_sql_port
		need_fill_connections = False
		
		#Connect About window to menu
		self.action_About.triggered.connect(self.open_about_dialog)
		#Connect Connection window to menu
		self.action_Settings.triggered.connect(self.open_connection_dialog)
		
		print("Try to open connection.bin")
		data_file = open_file("connection.bin")
		if data_file == -1:
			is_all_fine = False
			error_text = 'File "connection.bin" not found'
		elif data_file == -2:
			is_all_fine = False
			error_text = 'Error while opening "connection.bin"'
		else:
			error_text = 'Successfully'
		print(error_text)
		print("========================")
		if data_file == -1 or data_file == -2:
			print("Ask to make new file")
			FileNotFoundMessageBox = QtWidgets.QMessageBox()
			FileNotFoundMessageBox.setIcon(QtWidgets.QMessageBox.Critical)
			FileNotFoundMessageBox.setWindowTitle("File not found")
			FileNotFoundMessageBox.setText(error_text + " Create new empty one?")
			YesButton = FileNotFoundMessageBox.addButton('Yes', QtWidgets.QMessageBox.AcceptRole)
			NoButton = FileNotFoundMessageBox.addButton('No', QtWidgets.QMessageBox.RejectRole)
			FileNotFoundMessageBox.exec()
			if FileNotFoundMessageBox.clickedButton() == YesButton:
				ucce_sql_username = getUser_name()
				ucce_sql_credentials = fromUserPass2Credentials(ucce_sql_username,ucce_sql_pass)
				text = encrypt_data(fromUserPass2Credentials("username@domain (with dots)","password"),
					"server@domain (with dots)",str(ucce_sql_enable),str(ucce_sql_NT_auth),
					ucce_sql_credentials,ucce_instance,ucce_sql_port)
				if text == -1:
					error_text = "Cann't load host's information"
					is_all_fine = False
				elif text == -2:	
					is_all_fine = False
					error_text = "Error encrypt data"
				else:
					is_all_fine = save_file("connection.bin",text)					
				if is_all_fine:
					error_text = 'File "connection.bin" created successfully'
					try:
						data_file = open_file("connection.bin")
						decrypted_text = decrypt_data(data_file)
						connection_data = load_connection_data(decrypted_text)
						is_all_fine = connection_data["is_all_fine"]
						error_text = connection_data["error_text"]						
					except:
						pass
					need_fill_connections = True
				else:
					error_text = 'Error creating file "connection.bin"'
				print(error_text)
			else:
				print("Not accepted by user")
			print("========================")
		else:
			print("Try to decrypt file")
			is_all_fine = True
			decrypted_text = decrypt_data(data_file)
			if decrypted_text == -2:
				is_all_fine = False
				error_text = 'Error opening file "connection.bin". Perhaps it created for different host or user. '
				error_text = error_text + 'You need create new one via "Connection\Settings"'
				print(error_text)
				print("========================")
				print("Ask to make new file")
				FileNotDecryptedMessageBox = QtWidgets.QMessageBox()
				FileNotDecryptedMessageBox.setIcon(QtWidgets.QMessageBox.Critical)
				FileNotDecryptedMessageBox.setWindowTitle("File not found")
				FileNotDecryptedMessageBox.setText('Error opening file "connection.bin".'
					'Perhaps it created for different host or user. Create empty one?')
				YesButton = FileNotDecryptedMessageBox.addButton('Yes', QtWidgets.QMessageBox.AcceptRole)
				NoButton = FileNotDecryptedMessageBox.addButton('No', QtWidgets.QMessageBox.RejectRole)
				FileNotDecryptedMessageBox.exec()
				if FileNotDecryptedMessageBox.clickedButton() == YesButton:
					ucce_sql_username = getUser_name()
					ucce_sql_credentials = fromUserPass2Credentials(ucce_sql_username,ucce_sql_pass)
					text = encrypt_data(fromUserPass2Credentials("username@domain (with dots)","password"),
						"server@domain (with dots)",str(ucce_sql_enable),str(ucce_sql_NT_auth),
						ucce_sql_credentials,ucce_instance,ucce_sql_port)
					if text == -1:
						error_text = "Cann't load host's information"
						is_all_fine = False
					elif text == -2:	
						is_all_fine = False
						error_text = "Error encrypt data"
					else:
						is_all_fine = save_file("connection.bin",text)					
					if is_all_fine:
						error_text = 'File "connection.bin" created successfully'
						try:
							data_file = open_file("connection.bin")
							decrypted_text = decrypt_data(data_file)
							connection_data = load_connection_data(decrypted_text)
							is_all_fine = connection_data["is_all_fine"]
							error_text = connection_data["error_text"]							
						except:
							pass
						need_fill_connections = True
					else:
						error_text = 'Error creating file "connection.bin"'
					print(error_text)
				else:
					print("Not accepted by user")
				print("========================")					
			elif decrypted_text == -1:
				is_all_fine = False
				error_text = "Cann't load this host's information"
				print(error_text)
				print("========================")			
			else:
				print("Successfully")
				print("========================")			
				connection_data = load_connection_data(decrypted_text)
				is_all_fine = connection_data["is_all_fine"]
				error_text = connection_data["error_text"]				
		if is_all_fine:
			ucce_username = connection_data["ucce_username"]
			ucce_pass = connection_data["ucce_pass"]
			ucce_server = connection_data["ucce_server"]
			ucce_sql_enable = connection_data["ucce_sql_enable"]
			ucce_sql_NT_auth = connection_data["ucce_sql_NT_auth"]
			ucce_sql_username = connection_data["ucce_sql_username"]
			ucce_sql_pass = connection_data["ucce_sql_pass"]
			ucce_instance = connection_data["ucce_instance"]
			ucce_sql_port = connection_data["ucce_sql_port"]
			#Filters activation
			self.comboBox_Filter.currentIndexChanged.connect(self.comboFilter_changed)
			self.comboBox_Condition.currentIndexChanged.connect(self.comboCondition_changed)
			#Retrieve button activation
			self.pushButton_Retrieve.clicked.connect(self.clicked_retrieve)
			self.pushButton_Retrieve.setEnabled(True)
			self.statusbar.setStyleSheet("color:green;font-weight:bold;")
			self.statusbar.showMessage("All's fine. Current version of application: " + __version__)
		else:
			self.statusbar.setStyleSheet("color:red;font-weight:bold;")
			self.statusbar.showMessage(error_text)
		if need_fill_connections:
			self.statusbar.showMessage("File created successfully. Current version of application: " + __version__)
			self.open_connection_dialog()

	def closeEvent(self,event): #Try to close dialogs windows if main one closed with cross
		print("Main window closed with cross")
		try:
			self.dialog_connect.close()
			print("dialog_connect closed successfully")	
		except:
			pass
		try:
			self.dialog_about.close()
			print("dialog_about closed successfully")
		except:
			pass
		print("========================")

#Part 1. HTTP functions:
	def ucce_http_request(self,url): #HTTP GET request
		global ucce_username,ucce_pass,ucce_server, is_all_fine,error_text
		response = None
		is_all_fine = False
		try:
			response = requests.get("https://" + ucce_server + url, 
				auth=(ucce_username, ucce_pass), verify=False)
			error_text = "Successfull"
			is_all_fine = True
		except requests.exceptions.Timeout:
			# Maybe set up for a retry, or continue in a retry loop
			error_text = "Timeout"
		except requests.exceptions.TooManyRedirects:
			# Tell the user their URL was bad and try a different one
			error_text = "TooManyRedirects"
		except requests.exceptions.HTTPError:
			error_text = "HTTPError"
		except requests.exceptions.SSLError:
			# Certificate
			error_text = "SSLError"
		except:
			# catastrophic error.
			error_text = "Other error"
		return response

	def get_timezones(self,url): #Get Timezones
		global is_all_fine, error_text, timezones_array, ucce_username,ucce_pass,ucce_server
		timezone_array = []
		timezones_array = []
		is_all_fine = True
		error_text = ""
		
		try:
			response = self.ucce_http_request(url) #make http request
			if response.status_code == 401:   #unauthorized
				error_text = str(response.status_code) + " - " + response.reason
				error_text = error_text + ". Please, check connections properties (Connection\Settings)"
				is_all_fine = False
			elif response.status_code == 200: #all's fine
				error_text = "Data recieved successfully"
			else:
				is_all_fine = False
				error_text = str(response.status_code) + " - " + response.reason
		except Exception:
			is_all_fine = False
			error_text = "Error while calling 'ucce_http_request': " + error_text
			
		if is_all_fine: 
			try:
				root = ElementTree.fromstring(response.content)
				timeZones = root.find('timeZones')
				#get timeZones list					
				for timeZone in timeZones:
					refURL = timeZone.find('refURL').text
					displayName = timeZone.find('displayName').text
					#fill array of timeZones
					timezone_array = [displayName,refURL]
					timezones_array.append(timezone_array)
			except Exception:
				error_text = "Error while parsing timeZones data"
				is_all_fine = False
		return is_all_fine, error_text, timezones_array

	def get_campaigns(self,url): #Get Campaigns
		global ucce_username,ucce_pass,ucce_server, canCreate, canUpdate, canDelete
		global is_all_fine, error_text, campaigns_array
		canCreate = False
		canUpdate = False
		canDelete = False
		campaing_array = []
		campaign_sg_array = []
		sg_array = []
		campaigns_array = []
		is_all_fine = True
		error_text = ""

		while not (url is None):
			try:
				response = self.ucce_http_request(url) #make http request
				url = None #And clear url for loop avoid
				if response.status_code == 401:   #unauthorized
					error_text = str(response.status_code) + " - " + response.reason
					error_text = error_text + ". Please, check connections properties (Connection\Settings)"
					is_all_fine = False
				elif response.status_code == 200: #all's fine
					error_text = "Data recieved successfully"
				else:
					is_all_fine = False
					error_text = str(response.status_code) + " - " + response.reason
			except Exception:
				is_all_fine = False
				error_text = "Error while calling 'ucce_http_request'"
				
			if is_all_fine: 
				try:
					root = ElementTree.fromstring(response.content)
					campaigns = root.find('campaigns')
					nextPage = root.find('pageInfo').find('nextPage')
					e_canCreate = root.find('permissionInfo').find('canCreate')
					e_canUpdate = root.find('permissionInfo').find('canUpdate')
					e_canDelete = root.find('permissionInfo').find('canDelete')
					#has user additional rights for delete/update/create?
					if not (e_canCreate is None):
						if e_canCreate.text == "true":
							canCreate = True
					if not (e_canUpdate is None):
						if e_canUpdate.text == "true":
							canUpdate = True
					if not (e_canDelete is None):
						if e_canDelete.text == "true":
							canDelete = True
					#get campaigns list					
					for campaign in campaigns:
						campaign_sg_array = []
						campaing_array = []
						campaign_id = campaign.find('refURL').text
						campaign_id = campaign_id[campaign_id.find('/campaign/') + len('/campaign/'):]
						refURL = campaign.find('refURL').text
						changeStamp = campaign.find('changeStamp').text
						abandonEnabled = campaign.find('abandonEnabled').text
						abandonPercent = campaign.find('abandonPercent').text
						amdTreatmentMode = campaign.find('amdTreatmentMode').text
						e_campaignPrefix = campaign.find('campaignPrefix')
						if not (e_campaignPrefix is None):
							campaignPrefix = e_campaignPrefix.text
						else:
							campaignPrefix = ""
						campaignPurposeType = campaign.find('campaignPurposeType').text
						cpa_enabled = campaign.find('callProgressAnalysis').find('enabled').text
						cpa_record = campaign.find('callProgressAnalysis').find('record').text
						cpa_minSilencePeriod = campaign.find('callProgressAnalysis').find('minSilencePeriod').text
						cpa_analysisPeriod = campaign.find('callProgressAnalysis').find('analysisPeriod').text
						cpa_minimumValidSpeech = campaign.find('callProgressAnalysis').find('minimumValidSpeech').text
						cpa_maxTimeAnalysis = campaign.find('callProgressAnalysis').find('maxTimeAnalysis').text
						cpa_maxTermToneAnalysis = campaign.find('callProgressAnalysis').find('maxTermToneAnalysis').text
						e_description = campaign.find('description')
						if not (e_description is None):
							description = e_description.text
						else:
							description = ""
						e_dialingMode = campaign.find('dialingMode')
						if not (e_dialingMode is None):
							dialingMode = e_dialingMode.text
						else:
							dialingMode = "INBOUND"						
						enabled = campaign.find('enabled').text
						endDate = campaign.find('endDate').text
						endTime = campaign.find('endTime').text
						ipAmdEnabled = campaign.find('ipAmdEnabled').text
						ipTerminatingBeepDetect = campaign.find('ipTerminatingBeepDetect').text
						linesPerAgent = campaign.find('linesPerAgent').text
						maxAttempts = campaign.find('maxAttempts').text
						maximumLinesPerAgent = campaign.find('maximumLinesPerAgent').text
						minimumCallDuration = campaign.find('minimumCallDuration').text
						name = campaign.find('name').text
						noAnswerRingLimit = campaign.find('noAnswerRingLimit').text
						personalizedCallbackEnabled = campaign.find('personalizedCallbackEnabled').text
						predictiveCorrectionPace = campaign.find('predictiveCorrectionPace').text
						predictiveGain = campaign.find('predictiveGain').text
						rescheduleCallbackMode = campaign.find('rescheduleCallbackMode').text
						e_reservationPercentage = campaign.find('reservationPercentage')
						if not (e_reservationPercentage is None):
							reservationPercentage = e_reservationPercentage.text
						else:
							reservationPercentage = "0"	
						answeringMachineDelay = campaign.find('retries').find('answeringMachineDelay').text
						busySignalDelay = campaign.find('retries').find('busySignalDelay').text
						customerAbandonedDelay = campaign.find('retries').find('customerAbandonedDelay').text
						customerNotHomeDelay = campaign.find('retries').find('customerNotHomeDelay').text
						dialerAbandonedDelay = campaign.find('retries').find('dialerAbandonedDelay').text
						noAnswerDelay = campaign.find('retries').find('noAnswerDelay').text
						startDate = campaign.find('startDate').text
						startTime = campaign.find('startTime').text
						timeZone_URL = campaign.find('timeZone').find('refURL').text
						timeZone_Name = campaign.find('timeZone').find('displayName').text
						skillgroups = campaign.find('skillGroupInfos')
						for skillgroup in skillgroups:
							sg_array = []					
							dialedNumber = skillgroup.find('dialedNumber').text
							ivrPorts = skillgroup.find('ivrPorts').text
							e_ivrRoutePoint = skillgroup.find('ivrRoutePoint')
							if not (e_ivrRoutePoint is None):
								ivrRoutePoint = e_ivrRoutePoint.text
							else:
								ivrRoutePoint = ""
							e_abandonedRoutePoint = skillgroup.find('abandonedRoutePoint')					
							if not (e_abandonedRoutePoint is None):
								abandonedRoutePoint = e_abandonedRoutePoint.text
							else:
								abandonedRoutePoint = ""
							overflowAgents = skillgroup.find('overflowAgents').text
							recordsToCache = skillgroup.find('recordsToCache').text
							sg_refURL = skillgroup.find('skillGroup').find('refURL').text
							sg_name = skillgroup.find('skillGroup').find('name').text
							sg_id = skillgroup.find('skillGroup').find('refURL').text
							sg_id = sg_id[sg_id.find('/skillgroup/') + len('/skillgroup/'):]
							sg_array = [sg_id,sg_name,sg_refURL,dialedNumber,ivrPorts,overflowAgents,
							recordsToCache,ivrRoutePoint,abandonedRoutePoint]
							campaign_sg_array.append(sg_array)
						#fill array of campaigns
						campaing_array = [campaign_id,name,refURL,changeStamp,abandonEnabled,abandonPercent,
						amdTreatmentMode,campaignPrefix,campaignPurposeType,cpa_enabled,cpa_record,cpa_minSilencePeriod,
						cpa_analysisPeriod,cpa_minimumValidSpeech,cpa_maxTimeAnalysis,cpa_maxTermToneAnalysis,
						description,dialingMode,enabled,endDate,endTime,ipAmdEnabled,ipTerminatingBeepDetect,
						linesPerAgent,maxAttempts,maximumLinesPerAgent,minimumCallDuration,noAnswerRingLimit,
						predictiveCorrectionPace,predictiveGain,rescheduleCallbackMode,reservationPercentage,
						answeringMachineDelay,busySignalDelay,customerAbandonedDelay,customerNotHomeDelay,
						dialerAbandonedDelay,noAnswerDelay,startDate,startTime,timeZone_URL,timeZone_Name,
						personalizedCallbackEnabled,campaign_sg_array]
						campaigns_array.append(campaing_array)
					#is there more campaigns?
					if not (nextPage is None):
						url = nextPage.text
						url = url[url.find('/unifiedconfig'):]
						#get_campaigns (nextPage_url) #if yes, recieve them data too
				except Exception:
					error_text = "Error while parsing campaigns data"
					is_all_fine = False

	def get_skillgroups(self,url): #Get Skill-groups
		global ucce_username,ucce_pass,ucce_server, is_all_fine, error_text, skillgroups_array
		is_all_fine = True
		error_text = ""
		skillgroups_array = []
		
		while not (url is None):
			try:
				response = self.ucce_http_request(url) #make http request
				url = None #And clear url for loop avoid
				if response.status_code == 401:   #unauthorized
					error_text = str(response.status_code) + " - " + response.reason
					error_text = error_text + ". Please, check connections properties (Connection\Settings)"
					is_all_fine = False
				elif response.status_code == 200: #all's fine
					error_text = "Data recieved successfully"
				else:
					is_all_fine = False
					error_text = str(response.status_code) + " - " + response.reason
			except Exception:
				is_all_fine = False
				error_text = "Error while calling 'ucce_http_request'"
			
			if is_all_fine: 
				try:
					root = ElementTree.fromstring(response.content)
					skillGroups = root.find('skillGroups')
					nextPage = root.find('pageInfo').find('nextPage')
					#get SG list					
					for skillGroup in skillGroups:
						sg_array = []
						refURL = skillGroup.find('refURL').text
						name = skillGroup.find('name').text
						sg_id = skillGroup.find('refURL').text
						sg_id = sg_id[sg_id.find('/skillgroup/') + len('/skillgroup/'):]					
						#fill array of skillgroups
						sg_array = [name,refURL,sg_id]
						skillgroups_array.append(sg_array)
					#is there more skillgroups?
					if not (nextPage is None):
						url = nextPage.text
						url = url[url.find('/unifiedconfig'):]
				except Exception:
					error_text = "Error while parsing skillgroups data"
					is_all_fine = False

	def ucce_http_update(self,url,value): #Update campaign
		global ucce_username,ucce_pass,ucce_server
		update_result = ""
		try:
			response = requests.put("https://" + ucce_server + url, 
				auth=(ucce_username, ucce_pass), headers = {"Content-Type": "application/xml"}, 
				data = value, verify=False)
			if response.status_code == 200: 	#All's fine
				update_result = "200 - successful"
			elif response.status_code == 400:	#Need to parse body
				try:
					update_result = str(response.status_code) + " - " + response.reason + ":"
					root = ElementTree.fromstring(response.content)
					for apiError in root:
						error_text = apiError.find('errorMessage').text
						error_text = ' '.join(error_text.strip().split('\n'))
						update_result += "\n\t" + error_text
				except:
					update_result = str(response.status_code) + " - " + response.reason		
			else:								#Another error
				update_result = str(response.status_code) + " - " + response.reason
		except requests.exceptions.Timeout:
			# Maybe set up for a retry, or continue in a retry loop
			update_result = "Timeout"
		except requests.exceptions.TooManyRedirects:
			# Tell the user their URL was bad and try a different one
			update_result = "TooManyRedirects"
		except requests.exceptions.HTTPError:
			update_result = "HTTPError"
		except requests.exceptions.SSLError:
			# Certificate
			update_result = "SSLError"
		except:
			# catastrophic error.
			update_result = "Other error"
		return update_result
		
	def ucce_http_add(self,value):		#Add campaign
		global ucce_username,ucce_pass,ucce_server
		add_result = ""
		refURL = ""
		campaign_id = ""
		try:
			response = requests.post("https://" + ucce_server + "/unifiedconfig/config/campaign", 
				auth=(ucce_username, ucce_pass), headers = {"Content-Type": "application/xml"}, 
				data = value, verify=False)
			if response.status_code == 201: 	#All's fine
				add_result = "201 - successful"
				try:
					refURL = response.headers['Location']
					refURL = refURL[refURL.find('/unifiedconfig/'):]
					campaign_id = refURL[refURL.find('/campaign/') + len('/campaign/'):]
				except:
					pass
			elif response.status_code == 400:	#Need to parse body
				try:
					add_result = str(response.status_code) + " - " + response.reason + ":"
					root = ElementTree.fromstring(response.content)
					for apiError in root:
						error_text = apiError.find('errorMessage').text
						error_text = ' '.join(error_text.strip().split('\n'))
						add_result += "\n\t" + error_text
				except:
					add_result = str(response.status_code) + " - " + response.reason		
			else:								#Another error
				add_result = str(response.status_code) + " - " + response.reason
		except requests.exceptions.Timeout:
			# Maybe set up for a retry, or continue in a retry loop
			add_result = "Timeout"
		except requests.exceptions.TooManyRedirects:
			# Tell the user their URL was bad and try a different one
			add_result = "TooManyRedirects"
		except requests.exceptions.HTTPError:
			add_result = "HTTPError"
		except requests.exceptions.SSLError:
			# Certificate
			add_result = "SSLError"
		except:
			# catastrophic error.
			add_result = "Other error"
		return add_result, refURL, campaign_id
		
	def ucce_http_del(self,value):		#Delete campaign
		global ucce_username,ucce_pass,ucce_server
		del_result = ""
		try:
			response = requests.delete("https://" + ucce_server + value, 
				auth=(ucce_username, ucce_pass), verify=False)
			if response.status_code == 200: 	#All's fine
				del_result = "200 - successful"
			elif response.status_code == 400:	#Need to parse body
				try:
					del_result = str(response.status_code) + " - " + response.reason + ":"
					root = ElementTree.fromstring(response.content)
					for apiError in root:
						error_text = apiError.find('errorMessage').text
						error_text = ' '.join(error_text.strip().split('\n'))
						del_result += "\n\t" + error_text
				except:
					del_result = str(response.status_code) + " - " + response.reason		
			else:								#Another error
				del_result = str(response.status_code) + " - " + response.reason
		except requests.exceptions.Timeout:
			# Maybe set up for a retry, or continue in a retry loop
			del_result = "Timeout"
		except requests.exceptions.TooManyRedirects:
			# Tell the user their URL was bad and try a different one
			del_result = "TooManyRedirects"
		except requests.exceptions.HTTPError:
			del_result = "HTTPError"
		except requests.exceptions.SSLError:
			# Certificate
			del_result = "SSLError"
		except:
			# catastrophic error.
			del_result = "Other error"
		return del_result

#Part 2. SQL functions:
	def rem_sg_sql(self): #Filter Skill-groups, assigned to non-API campaigns
		global ucce_server, ucce_sql_username, ucce_sql_pass
		global ucce_sql_NT_auth, ucce_instance, ucce_sql_port
		global skillgroups_array, error_text
		sgs_na = []
		#SQL select:
		sql = "select tS.PeripheralName, tS.SkillTargetID"  
		sql += " from t_Campaign_Skill_Group tCS,"
		sql += " t_Skill_Group tS"
		sql += " where tCS.SkillTargetID = tS.SkillTargetID"
		#Connection String:
		connection_string = "Driver={ODBC Driver 17 for SQL Server};"
		connection_string += "SERVER=" + ucce_server + "," + ucce_sql_port + ";"
		connection_string += "DATABASE=" + ucce_instance + "_awdb;"
		if ucce_sql_NT_auth:
			connection_string += "Trusted_Connection=yes;"
		else:
			connection_string += "Trusted_Connection=no;"
			connection_string += "UID=" + ucce_sql_username + ";"
			connection_string += "PWD=" + ucce_sql_pass + ";"
		try:
			cursor = connect(connection_string).cursor()
			cursor.execute(sql)
			for row in cursor.fetchall():
				row_to_list = [elem for elem in row]
				sgs_na.append(row_to_list)
			for skillgroup in deepcopy(skillgroups_array): #Go through copy of list
				sg_name = skillgroup[0]
				for skillgroup_na in sgs_na:
					if sg_name == skillgroup_na[0]:
						skillgroups_array.remove(skillgroup) #And delete - from original
			error_text = "Non-API campaign's skill-groups filtered successfully"
			is_all_fine = True
		except Exception as err:
			error_text = str(err)
			is_all_fine = False
		
#Part 3. Business logic functions:
	def check_filter_campaigns(self): #Validate campaign's filters
			is_filter_fine = True
			error_text = "Successfully"
			CurrentText_Filter = str(self.comboBox_Filter.currentText())
			CurrentText_Value = str(self.comboBox_Value.currentText())
			if CurrentText_Filter in ["Campaign Name"]:
				if len(CurrentText_Value) > 32:
					is_filter_fine = False
					error_text = "Length of Campaign's Name in filter"
					error_text += " couldn't be greater than 32 symbols."
				else:
					is_filter_fine = True
			elif CurrentText_Filter in ["Campaign Description"]:
				if len(CurrentText_Value) > 255:
					is_filter_fine = False
					error_text = "Length of Campaign's Description in filter"
					error_text += " couldn't be greater than 255 symbols."
				elif len(CurrentText_Value) == 0:
					is_filter_fine = False
					error_text = "Please type a valid value in the filter"
				else:
					is_filter_fine = True				
			elif CurrentText_Filter in ["Campaign Prefix Digits"]:
				if len(CurrentText_Value) > 15:
					is_filter_fine = False
					error_text = "Length of Campaign's Prefix in filter"
					error_text += " couldn't be greater than 15 symbols."
				elif len(CurrentText_Value) == 0:
					is_filter_fine = False
					error_text = "Please type a valid value in the filter"
				elif CurrentText_Value.isnumeric() == False:
					is_filter_fine = False
					error_text = "Only numeric symbols are allowed in"
					error_text += " Campaign's Prefix in filter."
				else:
					is_filter_fine = True				
			elif CurrentText_Filter in ["Lines Per Agent","Maximum Lines Per Agent"]:
				try:
					CurrentText_Value = CurrentText_Value.replace(",",".")
					CurrentText_Value = float(CurrentText_Value)
					is_filter_fine = True
				except:
					is_filter_fine = False
					error_text = "Lines and Maximum Lines Per Agent in filter"
					error_text += " could contain only numeric symbols, dot and comma."	
				if is_filter_fine:
					if CurrentText_Value > 100 or CurrentText_Value < 1:
						is_filter_fine = False
						error_text = "Lines and Maximum Per Agent in filter"
						error_text += " could be in range 1 - 100."	
					else:
						is_filter_fine = True
			elif CurrentText_Filter in ["Minimum Call Duration"]:
				if CurrentText_Value.isnumeric() == False:
					is_filter_fine = False
					error_text = "Only numeric symbols are allowed in Minimum Call Duration in filter."
				else:
					if int(CurrentText_Value) > 10 or int(CurrentText_Value) < 0:
						is_filter_fine = False
						error_text = "Minimum Call Duration in filter could be in range 0 - 10."					
					else:
						is_filter_fine = True			
			elif CurrentText_Filter in ["Abandon Calls Limit Percent"]:
				try:
					CurrentText_Value = CurrentText_Value.replace(",",".")
					CurrentText_Value = float(CurrentText_Value)
					is_filter_fine = True
				except:
					is_filter_fine = False
					error_text = "Abandon Calls Limit Percent in filter could"
					error_text += " contain only numeric symbols, dot and comma."	
				if is_filter_fine:
					if CurrentText_Value > 100 or CurrentText_Value < 0:
						is_filter_fine = False
						error_text = "Abandon Calls Limit Percent in filter could be in range 0 - 100."	
					else:
						is_filter_fine = True			
			elif CurrentText_Filter in ["No Answer Ring Limit"]:
				if CurrentText_Value.isnumeric() == False:
					is_filter_fine = False
					error_text = "Only numeric symbols are allowed in No Answer Ring Limit in filter."
				else:
					if int(CurrentText_Value) > 10 or int(CurrentText_Value) < 2:
						is_filter_fine = False
						error_text = "No Answer Ring Limit in filter could be in range 2 - 10."					
					else:
						is_filter_fine = True	
			elif CurrentText_Filter in ["Maximum Attempts"]:
				if CurrentText_Value.isnumeric() == False:
					is_filter_fine = False
					error_text = "Only numeric symbols are allowed in Maximum Attempts in filter."
				else:
					if int(CurrentText_Value) > 100 or int(CurrentText_Value) < 1:
						is_filter_fine = False
						error_text = "Maximum Attempts in filter could be in range 1 - 100."					
					else:
						is_filter_fine = True
			elif CurrentText_Filter in ["No Answer Delay","Busy Signal Delay"]:
				if CurrentText_Value.isnumeric() == False:
					is_filter_fine = False
					error_text = "Only numeric symbols are allowed in Time Delay fields in filter."
				else:
					if int(CurrentText_Value) > 999999 or int(CurrentText_Value) < 1:
						is_filter_fine = False
						error_text = "No Answer and Busy Signal Delays in filter could be in range 1 - 999999."					
					else:
						is_filter_fine = True
			elif CurrentText_Filter in ["Dialer Abandoned Delay","Customer Abandoned Delay","Answering Machine Delay"]:
				if CurrentText_Value.isnumeric() == False:
					is_filter_fine = False
					error_text = "Only numeric symbols are allowed in Time Delay fields in filter."
				else:
					if int(CurrentText_Value) > 99999 or int(CurrentText_Value) < 1:
						is_filter_fine = False
						error_text = "Dialer Abandoned, Customer Abandoned and Answering Machine"
						error_text += " Delays in filter could be in range 1 - 99999."					
					else:
						is_filter_fine = True			
			elif CurrentText_Filter in ["Start Date","End Date"]:
				try:
					year,month,day = CurrentText_Value.split('-')
					date(int(year),int(month),int(day))
					is_filter_fine = True
				except:
					is_filter_fine = False
					error_text = "Incorrect Start or End Date. Correct format is YYYY-MM-DD."					
			elif CurrentText_Filter in ["Start Hours","End Hours"]:
				if CurrentText_Value.isnumeric() == False:
					is_filter_fine = False
					error_text = "Only numeric symbols could be in Hours in filter."
				else:
					if int(CurrentText_Value) > 23 or int(CurrentText_Value) < 0:
						is_filter_fine = False
						error_text = "Hours in filter could be in range 0 - 23."					
					else:
						is_filter_fine = True
			elif CurrentText_Filter in ["Start Minutes","End Minutes"]:
				if CurrentText_Value.isnumeric() == False:
					is_filter_fine = False
					error_text = "Only numeric symbols could be in Minutes in filter."
				else:
					if int(CurrentText_Value) > 59 or int(CurrentText_Value) < 0:
						is_filter_fine = False
						error_text = "Minutes in filter could be in range 0 - 59."					
					else:
						is_filter_fine = True
			if not is_filter_fine:
				#Error message
				FilterErrorMessageBox = QtWidgets.QMessageBox()
				FilterErrorMessageBox.setIcon(QtWidgets.QMessageBox.Critical)
				FilterErrorMessageBox.setWindowTitle("Incorrect filter")
				FilterErrorMessageBox.setText(error_text)
				YesButton = FilterErrorMessageBox.addButton('OK', QtWidgets.QMessageBox.AcceptRole)
				FilterErrorMessageBox.exec()
			return is_filter_fine, error_text

	def filter_skillgroups(self): #Filter Skill-group's list
		global campaigns_array, skillgroups_array
		for skillgroup in deepcopy(skillgroups_array): #Go through copy of list
			sg_name = skillgroup[0]				
			for campaign in campaigns_array:
				for campaign_SG in campaign[43]:
					campaign_SG_name = campaign_SG[1]
					if sg_name == campaign_SG_name:
						skillgroups_array.remove(skillgroup) #And delete - from original

	def filter_campaigns(self): #Apply campaign's filter
		global campaigns_array
		CurrentText_Filter = str(self.comboBox_Filter.currentText())
		CurrentText_Condition = str(self.comboBox_Condition.currentText())
		CurrentText_Value = str(self.comboBox_Value.currentText())
		if CurrentText_Filter in ["Campaign Enable","Abandon Calls Limit Enable","Personalized Callback",
			"Enable CPA","Enable IP AMD"]:
			if CurrentText_Filter == "Campaign Enable":
				index = 18
			elif CurrentText_Filter == "Abandon Calls Limit Enable":
				index = 4
			elif CurrentText_Filter == "Personalized Callback":
				index = 42
			elif CurrentText_Filter == "Enable CPA":
				index = 9
			elif CurrentText_Filter == "Enable IP AMD":
				index = 21
			if CurrentText_Condition == "Equal":
				if CurrentText_Value == "Checked":
					for campaign in deepcopy(campaigns_array):
						if campaign[index] != "true":
							campaigns_array.remove(campaign)
				elif CurrentText_Value == "Not Checked":
					for campaign in deepcopy(campaigns_array):
						if campaign[index] == "true":
							campaigns_array.remove(campaign)				
			elif CurrentText_Condition == "Not Equal":
				if CurrentText_Value == "Checked":
					for campaign in deepcopy(campaigns_array):
						if campaign[index] == "true":
							campaigns_array.remove(campaign)	
				elif CurrentText_Value == "Not Checked":
					for campaign in deepcopy(campaigns_array):
						if campaign[index] != "true":
							campaigns_array.remove(campaign)							
		elif CurrentText_Filter in ["Campaign Name","Campaign Description","Campaign Prefix Digits"]:
			if CurrentText_Filter == "Campaign Name":
				index = 1
			elif CurrentText_Filter == "Campaign Description":
				index = 16
			elif CurrentText_Filter == "Campaign Prefix Digits":
				index = 7
			if CurrentText_Condition == "Contains":
				for campaign in deepcopy(campaigns_array):
					if CurrentText_Value not in campaign[index]:
						campaigns_array.remove(campaign)				
			elif CurrentText_Condition == "Ends With":
				for campaign in deepcopy(campaigns_array):
					if  campaign[index][-len(CurrentText_Value):] != CurrentText_Value:
						campaigns_array.remove(campaign)
			elif CurrentText_Condition == "Starts With":
				for campaign in deepcopy(campaigns_array):
					if  campaign[index][:len(CurrentText_Value)] != CurrentText_Value:
						campaigns_array.remove(campaign)
			elif CurrentText_Condition == "Is Blank":
				for campaign in deepcopy(campaigns_array):
					if  campaign[index] != "":
						campaigns_array.remove(campaign)
		elif CurrentText_Filter in ["Dialing Mode","Campaign Type"]:
			if CurrentText_Filter == "Dialing Mode":
				index = 17
			elif CurrentText_Filter == "Campaign Type":
				index = 8
			if CurrentText_Condition == "Equal":		
				for campaign in deepcopy(campaigns_array):
					if campaign[index] != CurrentText_Value:
						campaigns_array.remove(campaign)				
			elif CurrentText_Condition == "Not Equal":
				for campaign in deepcopy(campaigns_array):
					if campaign[index] == CurrentText_Value:
						campaigns_array.remove(campaign)
		elif CurrentText_Filter in ["Lines Per Agent","Maximum Lines Per Agent","Minimum Call Duration",
			"Abandon Calls Limit Percent","No Answer Ring Limit","Maximum Attempts","Dialer Abandoned Delay",
			"No Answer Delay","Busy Signal Delay","Customer Abandoned Delay","Answering Machine Delay"]:
			CurrentText_Value = float(CurrentText_Value.replace(',', '.'))
			if CurrentText_Filter == "Lines Per Agent":
				index = 23
			elif CurrentText_Filter == "Maximum Lines Per Agent":
				index = 25
			elif CurrentText_Filter == "Minimum Call Duration":
				index = 26
			elif CurrentText_Filter == "Abandon Calls Limit Percent":
				index = 5
			elif CurrentText_Filter == "No Answer Ring Limit":
				index = 27
			elif CurrentText_Filter == "Maximum Attempts":
				index = 24
			elif CurrentText_Filter == "Dialer Abandoned Delay":
				index = 36
			elif CurrentText_Filter == "No Answer Delay":
				index = 37
			elif CurrentText_Filter == "Busy Signal Delay":
				index = 33
			elif CurrentText_Filter == "Customer Abandoned Delay":
				index = 34
			elif CurrentText_Filter == "Answering Machine Delay":
				index = 32
			if CurrentText_Condition == "Equal":
				for campaign in deepcopy(campaigns_array):
					if float(campaign[index]) != CurrentText_Value:
						campaigns_array.remove(campaign)				
			elif CurrentText_Condition == "Greater Then":
				for campaign in deepcopy(campaigns_array):
					if  float(campaign[index]) <= CurrentText_Value:
						campaigns_array.remove(campaign)
			elif CurrentText_Condition == "Less Then":
				for campaign in deepcopy(campaigns_array):
					if  float(campaign[index]) >= CurrentText_Value:
						campaigns_array.remove(campaign)
			elif CurrentText_Condition == "Not Equal":
				for campaign in deepcopy(campaigns_array):
					if  CurrentText_Value == float(campaign[index]):
						campaigns_array.remove(campaign)		
		elif CurrentText_Filter in ["Start Date","End Date"]:
			CurrentText_Value = date(int(CurrentText_Value[:4]),int(CurrentText_Value[5:7]),int(CurrentText_Value[8:]))
			if CurrentText_Filter == "Start Date":
				index = 38
			elif CurrentText_Filter == "End Date":
				index = 19
			if CurrentText_Condition == "Equal":
				for campaign in deepcopy(campaigns_array):
					campaign_Date = date(int(campaign[index][:4]),int(campaign[index][5:7]),int(campaign[index][8:]))
					if campaign_Date != CurrentText_Value:
						campaigns_array.remove(campaign)				
			elif CurrentText_Condition == "Greater Then":
				for campaign in deepcopy(campaigns_array):
					campaign_Date = date(int(campaign[index][:4]),int(campaign[index][5:7]),int(campaign[index][8:]))
					if  campaign_Date <= CurrentText_Value:
						campaigns_array.remove(campaign)
			elif CurrentText_Condition == "Less Then":
				for campaign in deepcopy(campaigns_array):
					campaign_Date = date(int(campaign[index][:4]),int(campaign[index][5:7]),int(campaign[index][8:]))
					if  campaign_Date >= CurrentText_Value:
						campaigns_array.remove(campaign)
			elif CurrentText_Condition == "Not Equal":
				for campaign in deepcopy(campaigns_array):
					campaign_Date = date(int(campaign[index][:4]),int(campaign[index][5:7]),int(campaign[index][8:]))
					if  campaign_Date == CurrentText_Value:
						campaigns_array.remove(campaign)
		elif CurrentText_Filter in ["Start Hours","End Hours"]:
			CurrentText_Value = int(float(CurrentText_Value.replace(',', '.')))
			if CurrentText_Filter == "Start Hours":
				index = 39
			elif CurrentText_Filter == "End Hours":
				index = 20
			if CurrentText_Condition == "Equal":
				for campaign in deepcopy(campaigns_array):
					if int(campaign[index][:campaign[index].find(":")]) != CurrentText_Value:
						campaigns_array.remove(campaign)				
			elif CurrentText_Condition == "Greater Then":
				for campaign in deepcopy(campaigns_array):
					if  int(campaign[index][:campaign[index].find(":")]) <= CurrentText_Value:
						campaigns_array.remove(campaign)
			elif CurrentText_Condition == "Less Then":
				for campaign in deepcopy(campaigns_array):
					if  int(campaign[index][:campaign[index].find(":")]) >= CurrentText_Value:
						campaigns_array.remove(campaign)
			elif CurrentText_Condition == "Not Equal":
				for campaign in deepcopy(campaigns_array):
					if  int(campaign[index][:campaign[index].find(":")]) == CurrentText_Value:
						campaigns_array.remove(campaign)
		elif CurrentText_Filter in ["Start Minutes","End Minutes"]:
			CurrentText_Value = int(float(CurrentText_Value.replace(',', '.')))
			if CurrentText_Filter == "Start Minutes":
				index = 39
			elif CurrentText_Filter == "End Minutes":
				index = 20
			if CurrentText_Condition == "Equal":
				for campaign in deepcopy(campaigns_array):
					if int(campaign[index][campaign[index].find(":")+1:]) != CurrentText_Value:
						campaigns_array.remove(campaign)				
			elif CurrentText_Condition == "Greater Then":
				for campaign in deepcopy(campaigns_array):
					if  int(campaign[index][campaign[index].find(":")+1:]) <= CurrentText_Value:
						campaigns_array.remove(campaign)
			elif CurrentText_Condition == "Less Then":
				for campaign in deepcopy(campaigns_array):
					if  int(campaign[index][campaign[index].find(":")+1:]) >= CurrentText_Value:
						campaigns_array.remove(campaign)
			elif CurrentText_Condition == "Not Equal":
				for campaign in deepcopy(campaigns_array):
					if  int(campaign[index][campaign[index].find(":")+1:]) == CurrentText_Value:
						campaigns_array.remove(campaign)

	def campaign_selected(self, item = None): #Campaign is selected in Campaign's list
		global campaigns_new_array, campaigns_array, timezones_array, skillgroups_array, campaigns_del_array
		global canDelete, canUpdate, ucce_username, ucce_pass, ucce_server
		is_not_deleted = True
		print('Clear fields')
		self.selected_CampaignClear()
		print("========================")
		if item is None:
			item = self.listWidget_Campaigns_List.currentItem()
		for list_item in self.listWidget_Campaigns_List.findItems("*", Qt.MatchWildcard):
			font = list_item.font() #Current font
			font.setBold(False)
			list_item.setFont(font) #Clear bold for all elements
		font = self.listWidget_Campaigns_List.currentItem().font()
		font.setBold(True)
		self.listWidget_Campaigns_List.currentItem().setData(Qt.FontRole, font) #And add to current
		selected_campaign_id = item.data(Qt.UserRole)
		print('Campaign with id ' + selected_campaign_id + ' selected')
		print("========================")
		self.statusbar.showMessage("")
		#unblock buttons
		if canDelete and ("New" not in selected_campaign_id):
			print('Admin has "canDelete" role. Unblocking Delete button')
			self.pushButton_Delete.setEnabled(True)
			print("========================")
		else:
			self.pushButton_Delete.setEnabled(False)
		#find what Campaign is selected
		for campaign in campaigns_new_array:		
			if campaign[0] == selected_campaign_id:
				#and save data to temp variables
				campaign_id = campaign[0]
				name = campaign[1]
				refURL = campaign[2]
				changeStamp = campaign[3]
				abandonEnabled = campaign[4]
				abandonPercent = campaign[5]
				amdTreatmentMode = campaign[6]
				campaignPrefix = campaign[7]
				campaignPurposeType = campaign[8]
				cpa_enabled = campaign[9]
				cpa_record = campaign[10]
				cpa_minSilencePeriod = campaign[11]
				cpa_analysisPeriod = campaign[12]
				cpa_minimumValidSpeech = campaign[13]
				cpa_maxTimeAnalysis = campaign[14]
				cpa_maxTermToneAnalysis = campaign[15]
				description = campaign[16]
				dialingMode = campaign[17]
				enabled = campaign[18]
				endDate = campaign[19]
				endTime = campaign[20]
				ipAmdEnabled = campaign[21]
				ipTerminatingBeepDetect = campaign[22]
				linesPerAgent = campaign[23]
				maxAttempts = campaign[24]
				maximumLinesPerAgent = campaign[25]
				minimumCallDuration = campaign[26]
				noAnswerRingLimit = campaign[27]
				predictiveCorrectionPace = campaign[28]
				predictiveGain = campaign[29]
				rescheduleCallbackMode = campaign[30]
				reservationPercentage = campaign[31]
				answeringMachineDelay = campaign[32]
				busySignalDelay = campaign[33]
				customerAbandonedDelay = campaign[34]
				customerNotHomeDelay = campaign[35]
				dialerAbandonedDelay = campaign[36]
				noAnswerDelay = campaign[37]
				startDate = campaign[38]
				startTime = campaign[39]
				timeZone_URL = campaign[40]
				timeZone_Name = campaign[41]
				personalizedCallbackEnabled = campaign[42]
				campaign_sg_array = deepcopy(campaign[43])
		print('Checks if current campaign (' + campaign_id + ') was modified & deleted. Enable Revert or Delete button')
		self.isCampaignChanged(campaign_id)	
		for campaign in campaigns_del_array:
			if campaign[0] == selected_campaign_id:
				is_not_deleted = False
				self.pushButton_Revert.setEnabled(True)
				self.pushButton_Delete.setEnabled(False)
		print("========================")
		if canUpdate and is_not_deleted:
			print('Admin has "canUpdate" role and campaign is not deleted. Unblocking elements')
			self.lineEdit_Name.setEnabled(True)
			self.checkBox_Campaign_Enabled.setEnabled(True)
			self.comboBox_Dialing_Mode.setEnabled(True)
			self.comboBox_Campaign_Type.setEnabled(True)
			self.lineEdit_Description.setEnabled(True)
			self.lineEdit_Lines.setEnabled(True)
			self.lineEdit_Max_Lines.setEnabled(True)
			self.lineEdit_Prefix.setEnabled(True)
			self.checkBox_Aban_Call_Limit.setEnabled(True)
			self.lineEdit_Calls_Per_Adjustment.setEnabled(True)
			self.lineEdit_Max_Gain.setEnabled(True)
			self.lineEdit_No_Answe_Rin_Limit.setEnabled(True)
			self.lineEdit_Attempts.setEnabled(True)
			self.lineEdit_Min_Call_Duration.setEnabled(True)
			self.checkBox_Pers_Callback.setEnabled(True)
			self.lineEdit_No_Answer_Delay.setEnabled(True)
			self.lineEdit_Busy_Delay.setEnabled(True)
			self.lineEdit_Customer_Aban_Delay.setEnabled(True)
			self.lineEdit_Dialer_Aban_Delay.setEnabled(True)
			self.lineEdit_AMD_Delay.setEnabled(True)
			self.lineEdit_Customer_Home_Delay.setEnabled(True)
			self.checkBox_CPA_Enable.setEnabled(True)
			self.lineEdit_Minimum_Silence_Period.setEnabled(True)
			self.lineEdit_Analysis_Period.setEnabled(True)
			self.lineEdit_Minimum_Valid_Speech.setEnabled(True)
			self.lineEdit_Maximum_Analysis_Time.setEnabled(True)
			self.lineEdit_Maximum_Term_Tone_Analysis.setEnabled(True)
			self.comboBox_TimeZone.setEnabled(True)
			self.lineEdit_StartDate.setEnabled(True)
			self.lineEdit_StartTime.setEnabled(True)
			self.lineEdit_EndDate.setEnabled(True)
			self.lineEdit_EndTime.setEnabled(True)
			self.lineEdit_Reserv_Percentage.setEnabled(True)
			self.pushButton_Add_SG.setEnabled(True)
			if personalizedCallbackEnabled == "true":
				self.comboBox_Pers_Callback.setEnabled(True)
			else:
				self.comboBox_Pers_Callback.setEnabled(False)				
			if abandonEnabled == "true":
				self.lineEdit_Aban_Call_Limit.setEnabled(True)
			else:
				self.lineEdit_Aban_Call_Limit.setEnabled(False)
			if cpa_enabled == "true":
				self.checkBox_Record_CPA.setEnabled(True)
				self.checkBox_IP_AMD_Enable.setEnabled(True)
			else:
				self.checkBox_Record_CPA.setEnabled(False)
				self.checkBox_IP_AMD_Enable.setEnabled(False)				
			if ipAmdEnabled == "true":
				self.radioButton_Aban_Call.setEnabled(True)
				self.radioButton_Transfer_IVR.setEnabled(True)
				if campaignPurposeType == "agentCampaign":
					self.radioButton_Transfer_Agent.setEnabled(True)
				else:
					self.radioButton_Transfer_Agent.setEnabled(False)
			else:
				self.radioButton_Aban_Call.setEnabled(False)
				self.radioButton_Transfer_IVR.setEnabled(False)
			if amdTreatmentMode == "transferToIVRRoutePoint":
				self.checkBox_Terminate_Tone_Detect.setEnabled(True)
			else:
				self.checkBox_Terminate_Tone_Detect.setEnabled(False)					
		else:
			print('Admin has not "canUpdate" role or campaign is deleted. Blocking elements')
			self.lineEdit_Name.setEnabled(False)
			self.checkBox_Campaign_Enabled.setEnabled(False)
			self.comboBox_Dialing_Mode.setEnabled(False)
			self.comboBox_Campaign_Type.setEnabled(False)
			self.lineEdit_Description.setEnabled(False)
			self.lineEdit_Lines.setEnabled(False)
			self.lineEdit_Max_Lines.setEnabled(False)
			self.lineEdit_Prefix.setEnabled(False)
			self.checkBox_Aban_Call_Limit.setEnabled(False)
			self.lineEdit_Calls_Per_Adjustment.setEnabled(False)
			self.lineEdit_Max_Gain.setEnabled(False)
			self.lineEdit_No_Answe_Rin_Limit.setEnabled(False)
			self.lineEdit_Attempts.setEnabled(False)
			self.lineEdit_Min_Call_Duration.setEnabled(False)
			self.checkBox_Pers_Callback.setEnabled(False)
			self.lineEdit_No_Answer_Delay.setEnabled(False)
			self.lineEdit_Busy_Delay.setEnabled(False)
			self.lineEdit_Customer_Aban_Delay.setEnabled(False)
			self.lineEdit_Dialer_Aban_Delay.setEnabled(False)
			self.lineEdit_AMD_Delay.setEnabled(False)
			self.lineEdit_Customer_Home_Delay.setEnabled(False)
			self.checkBox_CPA_Enable.setEnabled(False)
			self.lineEdit_Minimum_Silence_Period.setEnabled(False)
			self.lineEdit_Analysis_Period.setEnabled(False)
			self.lineEdit_Minimum_Valid_Speech.setEnabled(False)
			self.lineEdit_Maximum_Analysis_Time.setEnabled(False)
			self.lineEdit_Maximum_Term_Tone_Analysis.setEnabled(False)
			self.comboBox_TimeZone.setEnabled(False)
			self.lineEdit_StartDate.setEnabled(False)
			self.lineEdit_StartTime.setEnabled(False)
			self.lineEdit_EndDate.setEnabled(False)
			self.lineEdit_EndTime.setEnabled(False)
			self.lineEdit_Reserv_Percentage.setEnabled(False)
			self.pushButton_Add_SG.setEnabled(False)
			self.comboBox_Pers_Callback.setEnabled(False)
			self.lineEdit_Aban_Call_Limit.setEnabled(False)
			self.checkBox_Record_CPA.setEnabled(False)
			self.checkBox_IP_AMD_Enable.setEnabled(False)
			self.radioButton_Aban_Call.setEnabled(False)
			self.radioButton_Transfer_IVR.setEnabled(False)
			self.radioButton_Transfer_Agent.setEnabled(False)
			self.checkBox_Terminate_Tone_Detect.setEnabled(False)			
		print("========================")					
		print('Fill fields')
		if personalizedCallbackEnabled == "true":
			self.checkBox_Pers_Callback.setChecked(True)
		else:
			self.checkBox_Pers_Callback.setChecked(False)
		self.lineEdit_Name.setText(name)
		self.lineEdit_Name.textEdited.connect(lambda: self.lineEdit_Name_Edited(selected_campaign_id))
		if enabled == "true":
			self.checkBox_Campaign_Enabled.setChecked(True)
		else:
			self.checkBox_Campaign_Enabled.setChecked(False)
		self.checkBox_Campaign_Enabled.stateChanged.connect(lambda: self.checkBox_Campaign_Enabled_Changed(
			selected_campaign_id))
		self.comboBox_Dialing_Mode.setCurrentText(dialingMode)
		self.comboBox_Dialing_Mode.currentIndexChanged.connect(lambda: self.comboDialing_Mode_changed(
			selected_campaign_id))
		self.comboBox_Campaign_Type.setCurrentText(campaignPurposeType)
		self.comboBox_Campaign_Type.currentIndexChanged.connect(lambda: self.comboCampaign_Type_changed(
			selected_campaign_id))
		self.lineEdit_Description.setText(description)
		self.lineEdit_Description.textEdited.connect(lambda: self.lineEdit_Description_Edited(
			selected_campaign_id))
		self.lineEdit_Lines.setText(linesPerAgent)
		self.lineEdit_Lines.textEdited.connect(lambda: self.lineEdit_Lines_Edited(selected_campaign_id))
		self.lineEdit_Max_Lines.setText(maximumLinesPerAgent)
		self.lineEdit_Max_Lines.textEdited.connect(lambda: self.lineEdit_MaxLines_Edited(selected_campaign_id))
		self.lineEdit_Prefix.setText(campaignPrefix)
		self.lineEdit_Prefix.textEdited.connect(lambda: self.lineEdit_Prefix_Edited(selected_campaign_id))
		self.lineEdit_Aban_Call_Limit.setText(abandonPercent)
		if abandonEnabled == "true":
			self.checkBox_Aban_Call_Limit.setChecked(True)
		else:
			self.checkBox_Aban_Call_Limit.setChecked(False)
		self.checkBox_Aban_Call_Limit.stateChanged.connect(lambda: self.checkAban_Call_Limit_Changed(
			selected_campaign_id))
		self.lineEdit_Aban_Call_Limit.textEdited.connect(lambda: self.lineEdit_Aban_Call_Limit_Edited(
			campaign_id))
		self.lineEdit_Calls_Per_Adjustment.setText(predictiveCorrectionPace)
		self.lineEdit_Calls_Per_Adjustment.textEdited.connect(lambda: self.lineEdit_Calls_Per_Adj_Edited(
			campaign_id))
		self.lineEdit_Max_Gain.setText(predictiveGain)
		self.lineEdit_Max_Gain.textEdited.connect(lambda: self.lineEdit_Max_Gain_Edited(campaign_id))
		self.lineEdit_No_Answe_Rin_Limit.setText(noAnswerRingLimit)
		self.lineEdit_No_Answe_Rin_Limit.textEdited.connect(lambda: self.lineEdit_NoAnsRingLimit_Edited(
			campaign_id))
		self.lineEdit_Attempts.setText(maxAttempts)
		self.lineEdit_Attempts.textEdited.connect(lambda: self.lineEdit_Attempts_Edited(campaign_id))
		self.lineEdit_Min_Call_Duration.setText(minimumCallDuration)
		self.lineEdit_Min_Call_Duration.textEdited.connect(lambda: self.lineEdit_MinCallDur_Edited(
			campaign_id))
		self.comboBox_Pers_Callback.setCurrentText(rescheduleCallbackMode)
		self.checkBox_Pers_Callback.stateChanged.connect(lambda: self.checkPers_CB_Changed(campaign_id))
		self.comboBox_Pers_Callback.currentIndexChanged.connect(lambda: self.comboPers_CB_changed(
			campaign_id))
		self.lineEdit_No_Answer_Delay.setText(noAnswerDelay)
		self.lineEdit_No_Answer_Delay.textEdited.connect(lambda: self.lineEdit_NoAnsDelay_Edited(
			campaign_id))
		self.lineEdit_Busy_Delay.setText(busySignalDelay)
		self.lineEdit_Busy_Delay.textEdited.connect(lambda: self.lineEdit_BusyDelay_Edited(campaign_id))
		self.lineEdit_Customer_Aban_Delay.setText(customerAbandonedDelay)
		self.lineEdit_Customer_Aban_Delay.textEdited.connect(lambda: self.lineEdit_CustAbanDelay_Edited(
			campaign_id))
		self.lineEdit_Dialer_Aban_Delay.setText(dialerAbandonedDelay)
		self.lineEdit_Dialer_Aban_Delay.textEdited.connect(lambda: self.lineEdit_DialerAbanDelay_Edited(
			campaign_id))
		self.lineEdit_AMD_Delay.setText(answeringMachineDelay)
		self.lineEdit_AMD_Delay.textEdited.connect(lambda: self.lineEdit_AMDDelay_Edited(campaign_id))
		self.lineEdit_Customer_Home_Delay.setText(customerNotHomeDelay)
		self.lineEdit_Customer_Home_Delay.textEdited.connect(lambda: self.lineEdit_CustNotHomeDelay_Edited(
			campaign_id))	
		if cpa_enabled == "true":
			self.checkBox_CPA_Enable.setChecked(True)
		else:
			self.checkBox_CPA_Enable.setChecked(False)
		self.checkBox_CPA_Enable.stateChanged.connect(lambda: self.checkCPA_Enable_Changed(campaign_id))
		if cpa_record == "true":
			self.checkBox_Record_CPA.setChecked(True)
		else:
			self.checkBox_Record_CPA.setChecked(False)
		self.checkBox_Record_CPA.stateChanged.connect(lambda: self.checkRecord_CPA_Changed(campaign_id))
		if ipAmdEnabled == "true":
			self.checkBox_IP_AMD_Enable.setChecked(True)
		else:
			self.checkBox_IP_AMD_Enable.setChecked(False)
		self.checkBox_IP_AMD_Enable.stateChanged.connect(lambda: self.checkAMD_Enable_Changed(campaign_id))
		if amdTreatmentMode == "transferToIVRRoutePoint":
			self.radioButton_Aban_Call.setChecked(False)
			self.radioButton_Transfer_IVR.setChecked(True)
			self.radioButton_Transfer_Agent.setChecked(False)
		elif amdTreatmentMode == "transferToAgent":
			self.radioButton_Aban_Call.setChecked(False)
			self.radioButton_Transfer_IVR.setChecked(False)
			self.radioButton_Transfer_Agent.setChecked(True)
		else:
			self.radioButton_Aban_Call.setChecked(True)
			self.radioButton_Transfer_IVR.setChecked(False)
			self.radioButton_Transfer_Agent.setChecked(False)
		self.radioButton_Aban_Call.toggled.connect(lambda: self.radioButtons_Changed(campaign_id))
		self.radioButton_Transfer_Agent.toggled.connect(lambda: self.radioButtons_Changed(campaign_id))
		self.radioButton_Transfer_IVR.toggled.connect(lambda: self.radioButtons_Changed(campaign_id))
		if ipTerminatingBeepDetect == "true":
			self.checkBox_Terminate_Tone_Detect.setChecked(True)
		else:
			self.checkBox_Terminate_Tone_Detect.setChecked(False)
		self.checkBox_Terminate_Tone_Detect.stateChanged.connect(lambda: self.checkTerm_Tone_Detect_Changed(
			campaign_id))
		self.lineEdit_Minimum_Silence_Period.setText(cpa_minSilencePeriod)
		self.lineEdit_Minimum_Silence_Period.textEdited.connect(lambda: self.lineEdit_MinSilPer_Edited(
			campaign_id))
		self.lineEdit_Analysis_Period.setText(cpa_analysisPeriod)
		self.lineEdit_Analysis_Period.textEdited.connect(lambda: self.lineEdit_AnalysPer_Edited(campaign_id))		
		self.lineEdit_Minimum_Valid_Speech.setText(cpa_minimumValidSpeech)
		self.lineEdit_Minimum_Valid_Speech.textEdited.connect(lambda: self.lineEdit_MinValSpeech_Edited(
			campaign_id))	
		self.lineEdit_Maximum_Analysis_Time.setText(cpa_maxTimeAnalysis)
		self.lineEdit_Maximum_Analysis_Time.textEdited.connect(lambda: self.lineEdit_MaxAnalysTime_Edited(
			campaign_id))
		self.lineEdit_Maximum_Term_Tone_Analysis.setText(cpa_maxTermToneAnalysis)
		self.lineEdit_Maximum_Term_Tone_Analysis.textEdited.connect(lambda: self.lineEdit_MaxTermTone_Edited(
			campaign_id))
		self.comboBox_TimeZone.clear()
		for timezone in timezones_array:
			self.comboBox_TimeZone.addItem(timezone[0])		
		self.comboBox_TimeZone.setCurrentText(timeZone_Name)
		self.comboBox_TimeZone.currentIndexChanged.connect(lambda: self.comboTimeZone_changed(campaign_id))
		self.lineEdit_StartDate.setText(startDate)
		self.lineEdit_StartDate.textEdited.connect(lambda: self.lineEdit_StartDate_Edited(campaign_id))		   
		self.lineEdit_StartTime.setText(startTime)
		self.lineEdit_StartTime.textEdited.connect(lambda: self.lineEdit_StartTime_Edited(campaign_id))
		self.lineEdit_EndDate.setText(endDate)
		self.lineEdit_EndDate.textEdited.connect(lambda: self.lineEdit_EndDate_Edited(campaign_id))		   
		self.lineEdit_EndTime.setText(endTime)
		self.lineEdit_EndTime.textEdited.connect(lambda: self.lineEdit_EndTime_Edited(campaign_id))
		self.lineEdit_Reserv_Percentage.setText(reservationPercentage)
		self.lineEdit_Reserv_Percentage.textEdited.connect(lambda: self.lineEdit_Reserv_Perc_Edited(campaign_id))

		TableWidgetRow = 0
		self.tableWidget_SG.setRowCount(len(campaign_sg_array))
		for skillgroup in campaign_sg_array:
			#Drop-down skill-group's list
			globals()["self.comboBox_CampSG" + str(TableWidgetRow)] = QtWidgets.QComboBox() 
			if skillgroup[1] != "": #Add SGs from new config for this campaign selected_campaign_id
				globals()["self.comboBox_CampSG" + str(TableWidgetRow)].addItem(skillgroup[1])
				globals()["self.comboBox_CampSG" + str(TableWidgetRow)].setCurrentText(skillgroup[1])
			for campaign_old in campaigns_array: #Add SGs from current config for other campaigns
				if campaign_old[0] == selected_campaign_id:
					campaign_old_sg_array = deepcopy(campaign_old[43])
					for skillgroup_old in campaign_old_sg_array:
						if skillgroup_old[1] != skillgroup[1]:
							globals()["self.comboBox_CampSG" + str(TableWidgetRow)].addItem(skillgroup_old[1])
			for all_skillgroup in skillgroups_array: #Add non assigned free SGs from current config
				if all_skillgroup[0] != skillgroup[1]:
					globals()["self.comboBox_CampSG" + str(TableWidgetRow)].addItem(all_skillgroup[0])
			if True: #Connect comboBox_CampSG_changed. Lambda works incorrectly otherwise
				if TableWidgetRow == 0:
					globals()["self.comboBox_CampSG" + str(TableWidgetRow)].currentIndexChanged.connect(
						lambda: self.comboBox_CampSG_changed(selected_campaign_id,0))
				elif TableWidgetRow == 1:
					globals()["self.comboBox_CampSG" + str(TableWidgetRow)].currentIndexChanged.connect(
						lambda: self.comboBox_CampSG_changed(selected_campaign_id,1))
				elif TableWidgetRow == 2:
					globals()["self.comboBox_CampSG" + str(TableWidgetRow)].currentIndexChanged.connect(
						lambda: self.comboBox_CampSG_changed(selected_campaign_id,2))
				elif TableWidgetRow == 3:
					globals()["self.comboBox_CampSG" + str(TableWidgetRow)].currentIndexChanged.connect(
						lambda: self.comboBox_CampSG_changed(selected_campaign_id,3))
				elif TableWidgetRow == 4:
					globals()["self.comboBox_CampSG" + str(TableWidgetRow)].currentIndexChanged.connect(
						lambda: self.comboBox_CampSG_changed(selected_campaign_id,4))
				elif TableWidgetRow == 5:
					globals()["self.comboBox_CampSG" + str(TableWidgetRow)].currentIndexChanged.connect(
						lambda: self.comboBox_CampSG_changed(selected_campaign_id,5))
				elif TableWidgetRow == 6:
					globals()["self.comboBox_CampSG" + str(TableWidgetRow)].currentIndexChanged.connect(
						lambda: self.comboBox_CampSG_changed(selected_campaign_id,6))
				elif TableWidgetRow == 7:
					globals()["self.comboBox_CampSG" + str(TableWidgetRow)].currentIndexChanged.connect(
						lambda: self.comboBox_CampSG_changed(selected_campaign_id,7))
				elif TableWidgetRow == 8:
					globals()["self.comboBox_CampSG" + str(TableWidgetRow)].currentIndexChanged.connect(
						lambda: self.comboBox_CampSG_changed(selected_campaign_id,8))
				elif TableWidgetRow == 9:
					globals()["self.comboBox_CampSG" + str(TableWidgetRow)].currentIndexChanged.connect(
						lambda: self.comboBox_CampSG_changed(selected_campaign_id,9))
				elif TableWidgetRow == 10:
					globals()["self.comboBox_CampSG" + str(TableWidgetRow)].currentIndexChanged.connect(
						lambda: self.comboBox_CampSG_changed(selected_campaign_id,10))
				elif TableWidgetRow == 11:
					globals()["self.comboBox_CampSG" + str(TableWidgetRow)].currentIndexChanged.connect(
						lambda: self.comboBox_CampSG_changed(selected_campaign_id,11))
				elif TableWidgetRow == 12:
					globals()["self.comboBox_CampSG" + str(TableWidgetRow)].currentIndexChanged.connect(
						lambda: self.comboBox_CampSG_changed(selected_campaign_id,12))
				elif TableWidgetRow == 13:
					globals()["self.comboBox_CampSG" + str(TableWidgetRow)].currentIndexChanged.connect(
						lambda: self.comboBox_CampSG_changed(selected_campaign_id,13))
				elif TableWidgetRow == 14:
					globals()["self.comboBox_CampSG" + str(TableWidgetRow)].currentIndexChanged.connect(
						lambda: self.comboBox_CampSG_changed(selected_campaign_id,14))
				elif TableWidgetRow == 15:
					globals()["self.comboBox_CampSG" + str(TableWidgetRow)].currentIndexChanged.connect(
						lambda: self.comboBox_CampSG_changed(selected_campaign_id,15))
				elif TableWidgetRow == 16:
					globals()["self.comboBox_CampSG" + str(TableWidgetRow)].currentIndexChanged.connect(
						lambda: self.comboBox_CampSG_changed(selected_campaign_id,16))
				elif TableWidgetRow == 17:
					globals()["self.comboBox_CampSG" + str(TableWidgetRow)].currentIndexChanged.connect(
						lambda: self.comboBox_CampSG_changed(selected_campaign_id,17))
				elif TableWidgetRow == 18:
					globals()["self.comboBox_CampSG" + str(TableWidgetRow)].currentIndexChanged.connect(
						lambda: self.comboBox_CampSG_changed(selected_campaign_id,18))	
				elif TableWidgetRow == 19:
					globals()["self.comboBox_CampSG" + str(TableWidgetRow)].currentIndexChanged.connect(
						lambda: self.comboBox_CampSG_changed(selected_campaign_id,19))
			if canUpdate and is_not_deleted:
				globals()["self.comboBox_CampSG" + str(TableWidgetRow)].setEnabled(True)
			else:
				globals()["self.comboBox_CampSG" + str(TableWidgetRow)].setEnabled(False)
			self.tableWidget_SG.setCellWidget(			 #Insert SG list
				TableWidgetRow,0, globals()["self.comboBox_CampSG" + str(TableWidgetRow)])
			TableWidgetItem = QtWidgets.QTableWidgetItem()
			TableWidgetItem.setText(skillgroup[5])		#skillgroup[5] = overflowAgents
			self.tableWidget_SG.setItem(TableWidgetRow,1, TableWidgetItem)
			TableWidgetItem = QtWidgets.QTableWidgetItem()
			TableWidgetItem.setText(skillgroup[3])		#skillgroup[3] = dialedNumber
			self.tableWidget_SG.setItem(TableWidgetRow,2, TableWidgetItem)
			TableWidgetItem = QtWidgets.QTableWidgetItem()
			TableWidgetItem.setText(skillgroup[6])		#skillgroup[6] = recordsToCache
			self.tableWidget_SG.setItem(TableWidgetRow,3, TableWidgetItem)
			TableWidgetItem = QtWidgets.QTableWidgetItem()
			TableWidgetItem.setText(skillgroup[4])		#skillgroup[4] = ivrPorts
			self.tableWidget_SG.setItem(TableWidgetRow,4, TableWidgetItem)
			TableWidgetItem = QtWidgets.QTableWidgetItem()
			TableWidgetItem.setText(skillgroup[7])		#skillgroup[7] = ivrRoutePoint
			self.tableWidget_SG.setItem(TableWidgetRow,5, TableWidgetItem)
			TableWidgetItem = QtWidgets.QTableWidgetItem()
			TableWidgetItem.setText(skillgroup[8])		#skillgroup[8] = abandonedRoutePoint
			self.tableWidget_SG.setItem(TableWidgetRow,6, TableWidgetItem)
			TableWidgetRow += 1
		if canUpdate and is_not_deleted:
			self.tableWidget_SG.setEnabled(True)
		else:
			self.tableWidget_SG.setEnabled(False)		
		self.tableWidget_SG.itemChanged.connect(lambda: self.tableWidget_SG_ItemChanged(campaign_id))
		self.tableWidget_SG.itemClicked.connect(lambda: self.tableWidget_SG_ItemClicked(campaign_id))
		self.pushButton_Revert.clicked.connect(lambda: self.clicked_revert(selected_campaign_id))
		self.pushButton_Delete.clicked.connect(lambda: self.clicked_delete(campaign_id))
		self.pushButton_Add_SG.clicked.connect(lambda: self.clicked_add_sg(campaign_id))		
		print("========================")
				
	def check_new_campaign_data(self): #Validate campaign's data (after change ot for new)
		global campaigns_array, campaigns_new_array, campaigns_del_array
		is_validation_success_sum = True
		validation_error_sum = ""
		campaign_updates = {}
		campaign_adds = {}
		campaign_dels = {}
		for cindex in range(0,len(campaigns_new_array)):
			validation_error = ""
			sg_validation_error = ""
			sg_validation_error_sum = ""			
			is_validation_success = True
			is_SG_empty = False
			update_need = False
			campaign_update = ""
			if True: #Fill variables from campaigns_new_array
				campaign_id = campaigns_new_array[cindex][0]
				name = campaigns_new_array[cindex][1]
				refURL = campaigns_new_array[cindex][2]
				changeStamp = campaigns_new_array[cindex][3]
				abandonEnabled = campaigns_new_array[cindex][4]
				abandonPercent = campaigns_new_array[cindex][5]
				amdTreatmentMode = campaigns_new_array[cindex][6]
				campaignPrefix = campaigns_new_array[cindex][7]
				campaignPurposeType = campaigns_new_array[cindex][8]
				cpa_enabled = campaigns_new_array[cindex][9]
				cpa_record = campaigns_new_array[cindex][10]
				cpa_minSilencePeriod = campaigns_new_array[cindex][11]
				cpa_analysisPeriod = campaigns_new_array[cindex][12]
				cpa_minimumValidSpeech = campaigns_new_array[cindex][13]
				cpa_maxTimeAnalysis = campaigns_new_array[cindex][14]
				cpa_maxTermToneAnalysis = campaigns_new_array[cindex][15]
				description = campaigns_new_array[cindex][16]
				dialingMode = campaigns_new_array[cindex][17]
				enabled = campaigns_new_array[cindex][18]
				endDate = campaigns_new_array[cindex][19]
				endTime = campaigns_new_array[cindex][20]
				ipAmdEnabled = campaigns_new_array[cindex][21]
				ipTerminatingBeepDetect = campaigns_new_array[cindex][22]
				linesPerAgent = campaigns_new_array[cindex][23]
				maxAttempts = campaigns_new_array[cindex][24]
				maximumLinesPerAgent = campaigns_new_array[cindex][25]
				minimumCallDuration = campaigns_new_array[cindex][26]
				noAnswerRingLimit = campaigns_new_array[cindex][27]
				predictiveCorrectionPace = campaigns_new_array[cindex][28]
				predictiveGain = campaigns_new_array[cindex][29]
				rescheduleCallbackMode = campaigns_new_array[cindex][30]
				reservationPercentage = campaigns_new_array[cindex][31]
				answeringMachineDelay = campaigns_new_array[cindex][32]
				busySignalDelay = campaigns_new_array[cindex][33]
				customerAbandonedDelay = campaigns_new_array[cindex][34]
				customerNotHomeDelay = campaigns_new_array[cindex][35]
				dialerAbandonedDelay = campaigns_new_array[cindex][36]
				noAnswerDelay = campaigns_new_array[cindex][37]
				startDate = campaigns_new_array[cindex][38]
				startTime = campaigns_new_array[cindex][39]
				timeZone_URL = campaigns_new_array[cindex][40]
				timeZone_Name = campaigns_new_array[cindex][41]
				personalizedCallbackEnabled = campaigns_new_array[cindex][42]
				campaign_sg_array = deepcopy(campaigns_new_array[cindex][43])

			if (cindex < len(campaigns_array)) and (campaigns_array[cindex] == campaigns_new_array[cindex]) and ("New" not in campaigns_new_array[cindex][0]):
				update_need = False
			else:
				update_need = True
				for delcampaign in campaigns_del_array: #check if campaign is modified & deleted - do delete only
					if campaigns_new_array[cindex][0] == delcampaign[0]:
						update_need = False				
				if cindex < len(campaigns_array):		#if modified campaign is without SGs 
					if len(deepcopy(campaigns_array[cindex][43])) == 0:
						is_SG_empty = True
				#Validate new data:
				#Campaign name
				if len(name) == 0:
					is_validation_success = False
					validation_error += ", Campaign name is empty"
				elif len(name) > 32:
					is_validation_success = False
					validation_error += ", Maximum campaign name's length is 32"
				elif name[0:1].isalnum() == False:
					is_validation_success = False
					validation_error += ", First character in campaign name should be alphanumeric"
				elif name.replace(".","").replace("_","").isalnum() == False:
					is_validation_success = False
					validation_error += ", Only alphanumeric character, dots (.) and undercovers (_) are allowed in campaign name"
				else:
					try:
						name.encode(encoding='utf-8').decode('ascii')
					except UnicodeDecodeError:
						is_validation_success = False
						validation_error += ", Internationalized characters not allowed in campaign name"
						
				#Campaign description
				if len(description) > 255:
					is_validation_success = False
					validation_error += ", Maximum campaign description's length is 255"			

				#Prefix
				if len(campaignPrefix) > 15:
					is_validation_success = False
					validation_error += ", Maximum campaign's prefix length is 255"
				elif campaignPrefix.isnumeric() == False and campaignPrefix != "":
					is_validation_success = False
					validation_error += ", Only numeric symbols are allowed in campaign's Prefix"

				#Lines & Maximum lines per agent
				try:
					if float(linesPerAgent) > 100 or float(linesPerAgent) < 1 or float(
						maximumLinesPerAgent) > 100 or float(maximumLinesPerAgent) < 1:
						is_validation_success = False
						validation_error += ", Lines & Maximum lines per agent should be in range 1 - 100"
					elif float(maximumLinesPerAgent) < float(linesPerAgent):
						is_validation_success = False
						validation_error += ", Maximum lines should be same or greater than Lines per agent"
				except :
					is_validation_success = False
					validation_error += ", Only numbers could be in Lines & Maximum lines per agent fields"
				
				#Minimum call duration
				if minimumCallDuration.isnumeric() == False:
					is_validation_success = False
					validation_error += ", Only numeric symbols are allowed in Minimum Call Duration"
				elif int(minimumCallDuration) > 10 or int(minimumCallDuration) < 0:
					is_validation_success = False
					validation_error += ", Minimum Call Duration should be in range 0 - 10"				
				
				#Reservation Percentage
				if reservationPercentage.isnumeric() == False:
					is_validation_success = False
					validation_error += ", Only numeric symbols are allowed in Reservation Percentage"
				elif int(reservationPercentage) > 100 or int(reservationPercentage) < 0:
					is_validation_success = False
					validation_error += ", Reservation Percentage should be in range 0 - 100"											
				
				#Abandon call limit percent
				try:
					if float(abandonPercent) > 100 or float(abandonPercent) < 0:
						is_validation_success = False
						validation_error += ", Abandon call limit percent should be in range 0 - 100"
				except :
					is_validation_success = False
					validation_error += ", Only numbers could be in Abandon call limit percent field"
				
				#No answer ring limit
				if noAnswerRingLimit.isnumeric() == False:
					is_validation_success = False
					validation_error += ", Only numeric symbols are allowed in No Answer Ring Limit"
				elif int(noAnswerRingLimit) > 10 or int(noAnswerRingLimit) < 2:
					is_validation_success = False
					validation_error += ", No Answer Ring Limit should be in range 2 - 10"				

				#Maximum Attempts
				if maxAttempts.isnumeric() == False:
					is_validation_success = False
					validation_error += ", Only numeric symbols are allowed in Maximum Attempts"
				elif int(maxAttempts) > 100 or int(maxAttempts) < 1:
					is_validation_success = False
					validation_error += ", No Answer Ring Limit should be in range 1 - 100"				

				#No Answer Delay, Busy Signal Delay
				if noAnswerDelay.isnumeric() == False or busySignalDelay.isnumeric() == False:
					is_validation_success = False
					validation_error += ", Only numeric symbols are allowed in No Answer & Busy Signal Delays"
				elif int(noAnswerDelay) > 999999 or int(noAnswerDelay) < 1 or int(
					busySignalDelay) > 999999 or int(busySignalDelay) < 1:
					is_validation_success = False
					validation_error += ", No Answer & Busy Signal Delays should be in range 1 - 999999"				
				
				#Dialer Abandoned Delay, Answering Machine Delay
				if answeringMachineDelay.isnumeric() == False or dialerAbandonedDelay.isnumeric() == False:
					is_validation_success = False
					validation_error += ", Only numeric symbols are allowed in Dialer Abandoned & Answering Machine Delays"
				elif int(answeringMachineDelay) > 99999 or int(answeringMachineDelay) < 1 or int(
					dialerAbandonedDelay) > 99999 or int(dialerAbandonedDelay) < 1:
					is_validation_success = False
					validation_error += ", Dialer Abandoned & Answering Machine Delays should be in range 1 - 99999"				
				
				#Customer Abandoned Delay, Customer Not Home Delay
				if customerAbandonedDelay.isnumeric() == False or customerNotHomeDelay.isnumeric() == False:
					is_validation_success = False
					validation_error += ", Only numeric symbols are allowed in Customer Abandoned & Not Home Delays"
				elif int(customerAbandonedDelay) > 99999 or int(customerAbandonedDelay) < 1 or int(
					customerNotHomeDelay) > 99999 or int(customerNotHomeDelay) < 1:
					is_validation_success = False
					validation_error += ", Customer Abandoned & Not Home Delays should be in range 1 - 99999"				

				#Start & End Dates
				try:
					year,month,day = startDate.split('-')
					date(int(year),int(month),int(day))
					year,month,day = endDate.split('-')
					date(int(year),int(month),int(day))				
				except:
					is_validation_success = False
					validation_error +="Incorrect Start or End Date. Correct format is YYYY-MM-DD"

				#Start & End Times
				try:
					hours,minutes = startTime.split(':')
					time(int(hours),int(minutes))
					hours,minutes = startTime.split(':')
					time(int(hours),int(minutes))				
				except:
					is_validation_success = False
					validation_error +="Incorrect Start or End Time. Correct format is HH:MM"

				#Predictive Gain
				try:
					if float(predictiveGain) > 3 or float(predictiveGain) < 0.1:
						is_validation_success = False
						validation_error += ", Predictive Gain 0.1 - 3.0"
				except :
					is_validation_success = False
					validation_error += ", Only numbers could be in Predictive Gain field"

				#Voice calls per adjustment
				if predictiveCorrectionPace.isnumeric() == False:
					is_validation_success = False
					validation_error += ", Only numeric symbols are allowed in Voice Calls Per Adjustment field"
				elif int(predictiveCorrectionPace) > 5000 or int(predictiveCorrectionPace) < 10:
					is_validation_success = False
					validation_error += ", Voice Calls Per Adjustment should be in range 10 - 5000"				
				
				#Assigned skill-groups
				for skillgroup in campaign_sg_array:
					sg_validation_error = ""
					#dialedNumber
					if len(skillgroup[3]) > 10:
						is_validation_success = False
						sg_validation_error += ", Maximum Dialed Number's length is 10"
					elif skillgroup[3].replace(".","").replace("_","").isalnum() == False:
						is_validation_success = False
						sg_validation_error += ", Only alphanumeric character, dots (.) and undercovers (_) are allowed in Dialed Number"
					else:
						try:
							skillgroup[3].encode(encoding='utf-8').decode('ascii')
						except UnicodeDecodeError:
							is_validation_success = False
							sg_validation_error += ", Internationalized characters not allowed in Dialed Number"				
					
					#ivrPorts
					if skillgroup[4].isnumeric() == False:
						is_validation_success = False
						sg_validation_error += ", Only numeric symbols are allowed in IVR Ports field"
					elif int(skillgroup[4]) > 99999 or int(skillgroup[4]) < 0:
						is_validation_success = False
						sg_validation_error += ", IVR Ports should be in range 0 - 99999"				
					
					#overflowAgents
					if skillgroup[5].isnumeric() == False:
						is_validation_success = False
						sg_validation_error += ", Only numeric symbols are allowed in Overflow Agents field"
					elif int(skillgroup[5]) > 100 or int(skillgroup[5]) < 0:
						is_validation_success = False
						sg_validation_error += ", Overflow Agents should be in range 0 - 100"

					#recordsToCache
					if skillgroup[6].isnumeric() == False:
						is_validation_success = False
						sg_validation_error += ", Only numeric symbols are allowed in Records to Cache field"
					elif int(skillgroup[6]) > 400 or int(skillgroup[6]) < 1:
						is_validation_success = False
						sg_validation_error += ", Records to Cache should be in range 1 - 400"
					
					#ivrRoutePoint
					if skillgroup[7].isnumeric() == False and skillgroup[7]!="":
						is_validation_success = False
						sg_validation_error += ", IVR Route Point can only be numeric or blank"
					elif len(skillgroup[7]) > 32:
						is_validation_success = False
						sg_validation_error += ", Maximum IVR Route Point's length is 32"
					
					#abandonedRoutePoint
					if skillgroup[8].isnumeric() == False and skillgroup[8]!="":
						is_validation_success = False
						sg_validation_error += ", Abandoned Route Point can only be numeric or blank"
					elif len(skillgroup[8]) > 10:
						is_validation_success = False
						sg_validation_error += ", Maximum Abandoned Route Point's length is 10"
					
					if is_validation_success == False:
						is_validation_success_sum = False
						update_need = False
						if len(sg_validation_error) > 1 and sg_validation_error[0:2] == ", ":
							sg_validation_error = sg_validation_error [2:]
							sg_validation_error_sum = " " + skillgroup[1] + " (" + sg_validation_error + "); "
				
			if is_validation_success == False:
				is_validation_success_sum = False
				update_need = False
				if len(validation_error) > 1 and validation_error[0:1] == ",":
					validation_error = validation_error [1:]
					if len(sg_validation_error) > 1:
						validation_error += ","
					
				validation_error_sum += "\n" + name + ":" + validation_error + sg_validation_error_sum

			if update_need and is_validation_success_sum:
				campaign_update = "<campaign>\n"
				if not "New" in campaigns_new_array[cindex][0]: #For new campaign Change Stamp & URL is empty
					campaign_update = campaign_update + "	<refURL>" + refURL + "</refURL>\n"				
					campaign_update = campaign_update + "	<changeStamp>" + changeStamp + "</changeStamp>\n"
				campaign_update = campaign_update + "	<abandonEnabled>" + abandonEnabled + "</abandonEnabled>\n"
				campaign_update = campaign_update + "	<abandonPercent>" + abandonPercent + "</abandonPercent>\n"
				campaign_update = campaign_update + "	<amdTreatmentMode>" + amdTreatmentMode + "</amdTreatmentMode>\n"
				campaign_update = campaign_update + "	<campaignPrefix>" + campaignPrefix + "</campaignPrefix>\n"
				campaign_update = campaign_update + "	<campaignPurposeType>" + campaignPurposeType + "</campaignPurposeType>\n"
				campaign_update = campaign_update + "	<callProgressAnalysis>\n"
				campaign_update = campaign_update + "		<enabled>" + cpa_enabled + "</enabled>\n"
				campaign_update = campaign_update + "		<record>" + cpa_record + "</record>\n"
				campaign_update = campaign_update + "		<minSilencePeriod>" + cpa_minSilencePeriod + "</minSilencePeriod>\n"
				campaign_update = campaign_update + "		<analysisPeriod>" + cpa_analysisPeriod + "</analysisPeriod>\n"
				campaign_update = campaign_update + "		<minimumValidSpeech>" + cpa_minimumValidSpeech + "</minimumValidSpeech>\n"
				campaign_update = campaign_update + "		<maxTimeAnalysis>" + cpa_maxTimeAnalysis + "</maxTimeAnalysis>\n"
				campaign_update = campaign_update + "		<maxTermToneAnalysis>" + cpa_maxTermToneAnalysis + "</maxTermToneAnalysis>\n"
				campaign_update = campaign_update + "	</callProgressAnalysis>\n"
				campaign_update = campaign_update + "	<description>" + description + "</description>\n"
				campaign_update = campaign_update + "	<dialingMode>" + dialingMode + "</dialingMode>\n"
				campaign_update = campaign_update + "	<enabled>" + enabled + "</enabled>\n"
				campaign_update = campaign_update + "	<endDate>" + endDate + "</endDate>\n"
				campaign_update = campaign_update + "	<endTime>" + endTime + "</endTime>\n"
				campaign_update = campaign_update + "	<ipAmdEnabled>" + ipAmdEnabled + "</ipAmdEnabled>\n"
				campaign_update = campaign_update + "	<ipTerminatingBeepDetect>" + ipTerminatingBeepDetect + "</ipTerminatingBeepDetect>\n"
				campaign_update = campaign_update + "	<linesPerAgent>" + linesPerAgent + "</linesPerAgent>\n"
				campaign_update = campaign_update + "	<maxAttempts>" + maxAttempts + "</maxAttempts>\n"
				campaign_update = campaign_update + "	<maximumLinesPerAgent>" + maximumLinesPerAgent + "</maximumLinesPerAgent>\n"
				campaign_update = campaign_update + "	<minimumCallDuration>" + minimumCallDuration + "</minimumCallDuration>\n"
				campaign_update = campaign_update + "	<name>" + name + "</name>\n"
				campaign_update = campaign_update + "	<noAnswerRingLimit>" + noAnswerRingLimit + "</noAnswerRingLimit>\n"
				campaign_update = campaign_update + "	<personalizedCallbackEnabled>" + personalizedCallbackEnabled + "</personalizedCallbackEnabled>\n"
				campaign_update = campaign_update + "	<predictiveCorrectionPace>" + predictiveCorrectionPace + "</predictiveCorrectionPace>\n"
				campaign_update = campaign_update + "	<predictiveGain>" + predictiveGain + "</predictiveGain>\n"
				campaign_update = campaign_update + "	<rescheduleCallbackMode>" + rescheduleCallbackMode + "</rescheduleCallbackMode>\n"
				campaign_update = campaign_update + "	<reservationPercentage>" + reservationPercentage + "</reservationPercentage>\n"
				campaign_update = campaign_update + "	<retries>\n"
				campaign_update = campaign_update + "		<answeringMachineDelay>" + answeringMachineDelay + "</answeringMachineDelay>\n"
				campaign_update = campaign_update + "		<busySignalDelay>" + busySignalDelay + "</busySignalDelay>\n"
				campaign_update = campaign_update + "		<customerAbandonedDelay>" + customerAbandonedDelay + "</customerAbandonedDelay>\n"
				campaign_update = campaign_update + "		<customerNotHomeDelay>" + customerNotHomeDelay + "</customerNotHomeDelay>\n"
				campaign_update = campaign_update + "		<dialerAbandonedDelay>" + dialerAbandonedDelay + "</dialerAbandonedDelay>\n"
				campaign_update = campaign_update + "		<noAnswerDelay>" + noAnswerDelay + "</noAnswerDelay>\n"
				campaign_update = campaign_update + "	</retries>\n"
				if is_SG_empty:		#if modified campaign is without SGs
					campaign_update = campaign_update + "	<skillGroupInfosAdded>\n"
				else:
					campaign_update = campaign_update + "	<skillGroupInfos>\n"
				for skillgroup in campaign_sg_array:
					campaign_update = campaign_update + "		<skillGroupInfo>\n"
                    if campaignPurposeType == "ivrCampaign" and len(skillgroup[3]) == 0:
                    else:
                        campaign_update = campaign_update & "			<dialedNumber>" + skillgroup[3] + "</dialedNumber>\n"
					campaign_update = campaign_update + "			<ivrPorts>" + skillgroup[4]  + "</ivrPorts>\n"
					campaign_update = campaign_update + "			<overflowAgents>" + skillgroup[5]  + "</overflowAgents>\n"
					campaign_update = campaign_update + "			<recordsToCache>" + skillgroup[6]  + "</recordsToCache>\n"
					campaign_update = campaign_update + "			<ivrRoutePoint>" + skillgroup[7]  + "</ivrRoutePoint>\n"
					campaign_update = campaign_update + "			<abandonedRoutePoint>" + skillgroup[8]  + "</abandonedRoutePoint>\n"
					campaign_update = campaign_update + "			<skillGroup>\n"
					campaign_update = campaign_update + "				<refURL>" + skillgroup[2]  + "</refURL>\n"
					campaign_update = campaign_update + "				<name>" + skillgroup[1]  + "</name>\n"
					campaign_update = campaign_update + "			</skillGroup>\n"
					campaign_update = campaign_update + "		</skillGroupInfo>\n"
				if is_SG_empty:		#if modified campaign is without SGs
					campaign_update = campaign_update + "	</skillGroupInfosAdded>\n"
				else:
					campaign_update = campaign_update + "	</skillGroupInfos>\n"
				campaign_update = campaign_update + "	<startDate>" + startDate + "</startDate>\n"
				campaign_update = campaign_update + "	<startTime>" + startTime + "</startTime>\n"
				campaign_update = campaign_update + "	<timeZone>\n"
				campaign_update = campaign_update + "		<refURL>" + timeZone_URL + "</refURL>\n"
				campaign_update = campaign_update + "		<displayName>" + timeZone_Name + "</displayName>\n"
				campaign_update = campaign_update + "	</timeZone>\n"
				campaign_update = campaign_update + "</campaign>"
				if not "New" in campaigns_new_array[cindex][0]: #For old campaign
					campaign_updates[name + ":::" + refURL] = campaign_update
				else: #For new campaign
					campaign_adds[name] = campaign_update
			else:	#check if is in deleted campaigns
				for delcampaign in campaigns_del_array:
					if delcampaign[0] == campaign_id:
						campaign_dels[delcampaign[1]] = delcampaign[2]
		if len (validation_error_sum) > 0:
			validation_error_sum = "There are errors in new config!!!" + validation_error_sum
		else:
			validation_error_sum = "New config is valid"
		return is_validation_success_sum, validation_error_sum, campaign_updates, campaign_adds, campaign_dels

#Part 4. GUI functions:
#=============Modal Windows=============================#
	def open_about_dialog(self):
		self.dialog_about = AboutDialogNew()
		Text = "API Campaign Manager\n"
		Text += "Developed by Viktor84e\n"
		Text += "E-mail for contact or donate: Viktor84e@gmail.com\n\n"
		Text += "Libraries used and licensing information:\n"
		Text += "==================================\n"
		Text += "|  Module:                         |  Version: |         License:        |\n"
		Text += "|------------------------------------------------------------------|\n"
		Text += "|  Python                          |  3.8.1     |           PSFL            |\n"
		Text += "|  PyQt5                           |  5.13.2   |      GNU GPL v3      |\n"
		Text += "|  requests                       |  2.23.0   | Apache License v2 |\n"
		Text += "|  cryptography               |  2.8        | Apache License v2 |\n"
		Text += "|  pyodbc                         |  4.0.30   |             MIT             |\n"
		Text += "|------------------------------------------------------------------|\n"
		Text += "| API Campaign Manager |  " + __version__ + "  |       GNU GPL v3     |\n"
		Text += "==================================\n\n"
		Text += "Sourсe url: "
		self.dialog_about.label.setText(Text)
		Text = '<a href="https://github.com/Viktor-84e/API-Campaign-Manager">https://github.com/Viktor-84e/API-Campaign-Manager</a>'		
		self.dialog_about.label2.setText(Text)
		self.dialog_about.label2.setOpenExternalLinks(True)
		self.dialog_about.show()

	def open_connection_dialog(self):
		global ucce_username, ucce_pass, ucce_server, ucce_sql_port, ucce_instance
		global ucce_sql_username, ucce_sql_pass, ucce_sql_enable, ucce_sql_NT_auth
		self.dialog_connect = ConnectionDialogNew()

		try:
			self.dialog_connect.buttonBox.clicked.disconnect()
		except:
			pass
		try:
			self.dialog_connect.checkBox_SQL_Enable.stateChanged.disconnect()
		except:
			pass
		try:
			self.dialog_connect.checkBox_Integrated_Auth.stateChanged.disconnect()
		except:
			pass
		
		if ucce_username is None:
			ucce_username = ""
		if ucce_username is None:
			ucce_pass = ""	
		if ucce_server is None:
			ucce_pass = ""						
		if ucce_sql_username is None:
			ucce_pass = ""	
		if ucce_sql_pass is None:
			ucce_pass = ""
		if ucce_sql_port is None:
			ucce_sql_port = ""
		if ucce_instance is None:
			ucce_instance = ""
		if ucce_username.find('@') > 0:
			self.dialog_connect.lineEdit_username.setText(ucce_username[:ucce_username.find('@')])
			self.dialog_connect.lineEdit_domain.setText(ucce_username[ucce_username.find('@') + 1:])
		else:
			self.dialog_connect.lineEdit_username.setText(ucce_username)
			self.dialog_connect.lineEdit_domain.setText("")			
		if ucce_sql_NT_auth == True:
			self.dialog_connect.checkBox_Integrated_Auth.setChecked(True)
		else:
			self.dialog_connect.checkBox_Integrated_Auth.setChecked(False)

		if ucce_sql_enable == True:
			self.dialog_connect.checkBox_SQL_Enable.setChecked(True)
			self.dialog_connect.checkBox_Integrated_Auth.setEnabled(True)
			self.dialog_connect.lineEdit_ucce_inst.setEnabled(True)
			self.dialog_connect.lineEdit_sql_port.setEnabled(True)
			if ucce_sql_NT_auth == True:
				self.dialog_connect.lineEdit_sql_username.setEnabled(False)
				self.dialog_connect.lineEdit_sql_pass.setEnabled(False)
			else:
				self.dialog_connect.lineEdit_sql_username.setEnabled(True)
				self.dialog_connect.lineEdit_sql_pass.setEnabled(True)			
		else:
			self.dialog_connect.checkBox_SQL_Enable.setChecked(False)
			self.dialog_connect.checkBox_Integrated_Auth.setEnabled(False)
			self.dialog_connect.lineEdit_sql_username.setEnabled(False)
			self.dialog_connect.lineEdit_sql_pass.setEnabled(False)
			
		self.dialog_connect.lineEdit_pass.setText(ucce_pass)
		self.dialog_connect.lineEdit_server.setText(ucce_server)
		self.dialog_connect.lineEdit_sql_username.setText(ucce_sql_username)
		self.dialog_connect.lineEdit_sql_pass.setText(ucce_sql_pass)
		self.dialog_connect.lineEdit_ucce_inst.setText(ucce_instance)
		self.dialog_connect.lineEdit_sql_port.setText(ucce_sql_port)				
		self.dialog_connect.buttonBox.clicked.connect(self.clicked_save_connect)
		self.dialog_connect.checkBox_SQL_Enable.stateChanged.connect(
			self.clicked_SQL_Enable_connect)
		self.dialog_connect.checkBox_Integrated_Auth.stateChanged.connect(
			self.clicked_Integrated_Auth_connect)
		self.dialog_connect.show()
		
	def clicked_save_connect(self):
		global ucce_username, ucce_pass, ucce_server, is_all_fine, error_text
		global ucce_sql_username, ucce_sql_pass, ucce_sql_enable, ucce_sql_NT_auth
		global ucce_sql_port, ucce_instance
		print("Save connection settings")
		newusername = self.dialog_connect.lineEdit_username.text()
		newdomain = self.dialog_connect.lineEdit_domain.text()
		ucce_pass = self.dialog_connect.lineEdit_pass.text()
		ucce_server = self.dialog_connect.lineEdit_server.text()		
		ucce_sql_username = self.dialog_connect.lineEdit_sql_username.text()
		ucce_sql_pass = self.dialog_connect.lineEdit_sql_pass.text()
		ucce_instance = self.dialog_connect.lineEdit_ucce_inst.text()
		ucce_sql_port = self.dialog_connect.lineEdit_sql_port.text()		
		if self.dialog_connect.checkBox_SQL_Enable.isChecked():
			ucce_sql_enable = True
		else:
			ucce_sql_enable = False
		if self.dialog_connect.checkBox_Integrated_Auth.isChecked():
			ucce_sql_NT_auth = True
		else:
			ucce_sql_NT_auth = False
		if len(newdomain) > 0:
			ucce_username = newusername + "@" + newdomain
		else:
			ucce_username = newusername
		ucce_credentials = fromUserPass2Credentials(ucce_username,ucce_pass)
		ucce_sql_credentials = fromUserPass2Credentials(ucce_sql_username,ucce_sql_pass)
		text = encrypt_data(ucce_credentials,ucce_server,str(ucce_sql_enable),
			str(ucce_sql_NT_auth),ucce_sql_credentials,ucce_instance,ucce_sql_port)
		if text == -1:
			error_text = "Cann't load host's information"
			is_all_fine = False
		elif text == -2:	
			is_all_fine = False
			error_text = "Error encrypt data"
		else:
			is_all_fine = save_file("connection.bin",text)					
		if is_all_fine:
			error_text = "Data saved successfully."
			self.pushButton_Retrieve.setEnabled(True)
			try:
				self.pushButton_Retrieve.clicked.disconnect()
			except:
				pass
			self.pushButton_Retrieve.clicked.connect(self.clicked_retrieve)
			self.statusbar.setStyleSheet("color:green;font-weight:bold;")
		else:
			error_text = 'Error while saving "connection.bin"'
			self.statusbar.setStyleSheet("color:red;font-weight:bold;")
		self.statusbar.showMessage(error_text)
		print(error_text)
		print("========================")

	def clicked_SQL_Enable_connect(self, state):
		global ucce_sql_enable, ucce_sql_NT_auth
		if state == 0:
			self.dialog_connect.checkBox_Integrated_Auth.setEnabled(False)
			self.dialog_connect.lineEdit_sql_username.setEnabled(False)
			self.dialog_connect.lineEdit_sql_pass.setEnabled(False)
			self.dialog_connect.lineEdit_ucce_inst.setEnabled(False)
			self.dialog_connect.lineEdit_sql_port.setEnabled(False)
		else:
			self.dialog_connect.checkBox_Integrated_Auth.setEnabled(True)
			self.dialog_connect.lineEdit_ucce_inst.setEnabled(True)
			self.dialog_connect.lineEdit_sql_port.setEnabled(True)				
			if self.dialog_connect.checkBox_Integrated_Auth.isChecked() == True:
				self.dialog_connect.lineEdit_sql_username.setEnabled(False)
				self.dialog_connect.lineEdit_sql_pass.setEnabled(False)
			else:
				self.dialog_connect.lineEdit_sql_username.setEnabled(True)
				self.dialog_connect.lineEdit_sql_pass.setEnabled(True)						
		
	def clicked_Integrated_Auth_connect(self, state):
		global ucce_sql_username, ucce_sql_pass, ucce_sql_enable, ucce_sql_NT_auth
		if state == 0:
			self.dialog_connect.lineEdit_sql_username.setEnabled(True)
			self.dialog_connect.lineEdit_sql_pass.setEnabled(True)
			self.dialog_connect.lineEdit_sql_username.setText(ucce_sql_username)
			self.dialog_connect.lineEdit_sql_pass.setText(ucce_sql_pass)			
		else:
			self.dialog_connect.lineEdit_sql_username.setText(getUser_name())
			self.dialog_connect.lineEdit_sql_pass.setText("")			
			self.dialog_connect.lineEdit_sql_username.setEnabled(False)
			self.dialog_connect.lineEdit_sql_pass.setEnabled(False)					
#=======================================================#
	def selected_CampaignClear(self): #Clear Campaign Detail window
		global campaigns_array, campaigns_new_array, campaigns_del_array
		try:
			self.lineEdit_Name.textEdited.disconnect()
		except:
			pass
		try:
			self.checkBox_Campaign_Enabled.stateChanged.disconnect()
		except:
			pass		
		try:
			self.comboBox_Dialing_Mode.currentIndexChanged.disconnect()
		except:
			pass					
		try:
			self.comboBox_Campaign_Type.currentIndexChanged.disconnect()
		except:
			pass
		try:
			self.lineEdit_Description.textEdited.disconnect()
		except:
			pass
		try:
			self.lineEdit_Lines.textEdited.disconnect()
		except:
			pass
		try:
			self.lineEdit_Max_Lines.textEdited.disconnect()
		except:
			pass
		try:
			self.lineEdit_Prefix.textEdited.disconnect()
		except:
			pass
		try:
			self.checkBox_Aban_Call_Limit.stateChanged.disconnect()
		except:
			pass
		try:
			self.lineEdit_Aban_Call_Limit.textEdited.disconnect()
		except:
			pass		
		try:
			self.lineEdit_Calls_Per_Adjustment.textEdited.disconnect()
		except:
			pass
		try:
			self.lineEdit_Max_Gain.textEdited.disconnect()
		except:
			pass
		try:
			self.lineEdit_No_Answe_Rin_Limit.textEdited.disconnect()
		except:
			pass
		try:
			self.lineEdit_Attempts.textEdited.disconnect()
		except:
			pass
		try:
			self.lineEdit_Min_Call_Duration.textEdited.disconnect()
		except:
			pass
		try:
			self.checkBox_Pers_Callback.stateChanged.disconnect()
		except:
			pass
		try:
			self.comboBox_Pers_Callback.currentIndexChanged.disconnect()
		except:
			pass
		try:
			self.lineEdit_No_Answer_Delay.textEdited.disconnect()
		except:
			pass
		try:
			self.lineEdit_Busy_Delay.textEdited.disconnect()
		except:
			pass
		try:
			self.lineEdit_Customer_Aban_Delay.textEdited.disconnect()
		except:
			pass
		try:
			self.lineEdit_Dialer_Aban_Delay.textEdited.disconnect()
		except:
			pass
		try:
			self.lineEdit_AMD_Delay.textEdited.disconnect()
		except:
			pass
		try:
			self.lineEdit_Customer_Home_Delay.textEdited.disconnect()
		except:
			pass
		try:
			self.checkBox_CPA_Enable.stateChanged.disconnect()
		except:
			pass
		try:
			self.checkBox_Record_CPA.stateChanged.disconnect()
		except:
			pass
		try:
			self.checkBox_IP_AMD_Enable.stateChanged.disconnect()
		except:
			pass
		try:
			self.checkBox_Terminate_Tone_Detect.stateChanged.disconnect()
		except:
			pass		
		try:
			self.radioButton_Aban_Call.toggled.disconnect()
		except:
			pass
		try:
			self.radioButton_Transfer_IVR.toggled.disconnect()
		except:
			pass
		try:
			self.radioButton_Transfer_Agent.toggled.disconnect()
		except:
			pass	
		try:
			self.lineEdit_Minimum_Silence_Period.textEdited.disconnect()
		except:
			pass
		try:
			self.lineEdit_Analysis_Period.textEdited.disconnect()
		except:
			pass
		try:
			self.lineEdit_Minimum_Valid_Speech.textEdited.disconnect()
		except:
			pass
		try:
			self.lineEdit_Maximum_Analysis_Time.textEdited.disconnect()
		except:
			pass
		try:
			self.lineEdit_Maximum_Term_Tone_Analysis.textEdited.disconnect()
		except:
			pass
		try:
			self.comboBox_TimeZone.currentIndexChanged.disconnect()
		except:
			pass
		try:
			self.lineEdit_StartDate.textEdited.disconnect()
		except:
			pass
		try:
			self.lineEdit_StartTime.textEdited.disconnect()
		except:
			pass
		try:
			self.lineEdit_EndDate.textEdited.disconnect()
		except:
			pass
		try:
			self.lineEdit_EndTime.textEdited.disconnect()
		except:
			pass
		try:
			self.lineEdit_Reserv_Percentage.textEdited.disconnect()
		except:
			pass
		try:
			self.tableWidget_SG.itemChanged.disconnect()
		except:
			pass
		try:
			self.tableWidget_SG.itemClicked.disconnect()
		except:
			pass			
		try:
			self.pushButton_Revert.clicked.disconnect()
		except:
			pass
		try:
			self.pushButton_Delete.clicked.disconnect()
		except:
			pass
		try:
			self.pushButton_Add_SG.clicked.disconnect()
		except:
			pass			
		try:
			self.pushButton_Remove_SG.clicked.disconnect()
		except:
			pass						
		
		self.pushButton_Delete.setEnabled(False)
		self.pushButton_Revert.setEnabled(False)
		self.pushButton_Add_SG.setEnabled(False)
		self.pushButton_Remove_SG.setEnabled(False)		
		if campaigns_array != campaigns_new_array or len(campaigns_del_array) > 0:
			self.pushButton_Save.setEnabled(True)
		else:
			self.pushButton_Save.setEnabled(False)
		self.lineEdit_Name.setText("")
		self.lineEdit_Name.setEnabled(False)
		self.checkBox_Campaign_Enabled.setEnabled(False)
		self.checkBox_Campaign_Enabled.setChecked(False)
		self.comboBox_Dialing_Mode.setCurrentText("INBOUND")
		self.comboBox_Dialing_Mode.setEnabled(False)
		self.comboBox_Campaign_Type.setCurrentText("agentCampaign")
		self.comboBox_Campaign_Type.setEnabled(False)
		self.lineEdit_Description.setText("")
		self.lineEdit_Description.setEnabled(False)
		self.lineEdit_Lines.setText("")
		self.lineEdit_Lines.setEnabled(False)
		self.lineEdit_Max_Lines.setText("")
		self.lineEdit_Max_Lines.setEnabled(False)
		self.lineEdit_Prefix.setText("")
		self.lineEdit_Prefix.setEnabled(False)
		self.checkBox_Aban_Call_Limit.setChecked(False)
		self.checkBox_Aban_Call_Limit.setEnabled(False)
		self.lineEdit_Aban_Call_Limit.setText("")		
		self.lineEdit_Aban_Call_Limit.setEnabled(False)
		self.lineEdit_Calls_Per_Adjustment.setText("")
		self.lineEdit_Calls_Per_Adjustment.setEnabled(False)
		self.lineEdit_Max_Gain.setText("")
		self.lineEdit_Max_Gain.setEnabled(False)
		self.lineEdit_No_Answe_Rin_Limit.setText("")
		self.lineEdit_No_Answe_Rin_Limit.setEnabled(False)
		self.lineEdit_Attempts.setText("")
		self.lineEdit_Attempts.setEnabled(False)
		self.lineEdit_Min_Call_Duration.setText("")
		self.lineEdit_Min_Call_Duration.setEnabled(False)
		self.checkBox_Pers_Callback.setChecked(False)
		self.checkBox_Pers_Callback.setEnabled(False)
		self.comboBox_Pers_Callback.setEnabled(False)
		self.comboBox_Pers_Callback.setCurrentText("useCampaignDN")
		self.lineEdit_No_Answer_Delay.setText("")
		self.lineEdit_No_Answer_Delay.setEnabled(False)
		self.lineEdit_Busy_Delay.setText("")
		self.lineEdit_Busy_Delay.setEnabled(False)
		self.lineEdit_Customer_Aban_Delay.setText("")
		self.lineEdit_Customer_Aban_Delay.setEnabled(False)
		self.lineEdit_Dialer_Aban_Delay.setText("")
		self.lineEdit_Dialer_Aban_Delay.setEnabled(False)
		self.lineEdit_AMD_Delay.setText("")
		self.lineEdit_AMD_Delay.setEnabled(False)
		self.lineEdit_Customer_Home_Delay.setText("")
		self.lineEdit_Customer_Home_Delay.setEnabled(False)
		self.checkBox_CPA_Enable.setChecked(False)
		self.checkBox_CPA_Enable.setEnabled(False)
		self.checkBox_Record_CPA.setEnabled(False)
		self.checkBox_IP_AMD_Enable.setEnabled(False)
		self.checkBox_IP_AMD_Enable.setChecked(False)
		self.checkBox_Record_CPA.setChecked(False)
		self.checkBox_Record_CPA.setEnabled(False)
		self.checkBox_IP_AMD_Enable.setChecked(False)
		self.checkBox_IP_AMD_Enable.setEnabled(False)
		self.radioButton_Aban_Call.setEnabled(False)
		self.radioButton_Aban_Call.setChecked(True)
		self.radioButton_Transfer_IVR.setEnabled(False)
		self.radioButton_Transfer_IVR.setChecked(False)
		self.radioButton_Transfer_Agent.setEnabled(False)
		self.radioButton_Transfer_Agent.setChecked(False)
		self.checkBox_Terminate_Tone_Detect.setEnabled(False)
		self.checkBox_Terminate_Tone_Detect.setChecked(False)
		self.radioButton_Transfer_Agent.setChecked(False)
		self.radioButton_Transfer_Agent.setEnabled(False)
		self.radioButton_Aban_Call.setChecked(True)
		self.radioButton_Aban_Call.setEnabled(False)
		self.checkBox_Terminate_Tone_Detect.setChecked(False)
		self.checkBox_Terminate_Tone_Detect.setEnabled(False)
		self.lineEdit_Minimum_Silence_Period.setText("")
		self.lineEdit_Minimum_Silence_Period.setEnabled(False)
		self.lineEdit_Analysis_Period.setText("")
		self.lineEdit_Analysis_Period.setEnabled(False)
		self.lineEdit_Minimum_Valid_Speech.setText("")
		self.lineEdit_Minimum_Valid_Speech.setEnabled(False)
		self.lineEdit_Maximum_Analysis_Time.setText("")
		self.lineEdit_Maximum_Analysis_Time.setEnabled(False)
		self.lineEdit_Maximum_Term_Tone_Analysis.setText("")
		self.lineEdit_Maximum_Term_Tone_Analysis.setEnabled(False)
		self.comboBox_TimeZone.clear()
		self.comboBox_TimeZone.setEnabled(False)
		self.lineEdit_StartDate.setText("")
		self.lineEdit_StartDate.setEnabled(False)
		self.lineEdit_StartTime.setText("")
		self.lineEdit_StartTime.setEnabled(False)
		self.lineEdit_EndDate.setText("")
		self.lineEdit_EndDate.setEnabled(False)
		self.lineEdit_EndTime.setText("")
		self.lineEdit_EndTime.setEnabled(False)
		self.lineEdit_Reserv_Percentage.setEnabled(False)
		self.lineEdit_Reserv_Percentage.setText("")
		self.tableWidget_SG.setRowCount(0)
		self.pushButton_Add_SG.setEnabled(False)
		self.pushButton_Remove_SG.setEnabled(False)
		
	def fill_ListWidgetItem(self, campaign_id = ""): #Fill campaign list with names & ids
		global campaigns_array, campaigns_new_array, timezones_array, skillgroups_array, campaigns_del_array
		global canDelete, canUpdate, ucce_username, ucce_pass, ucce_server
		for campaignnew in campaigns_new_array:
			ListWidgetItem = QtWidgets.QListWidgetItem(campaignnew[1])
			ListWidgetItem.setData(Qt.UserRole,campaignnew[0])
			self.listWidget_Campaigns_List.addItem(ListWidgetItem)
			font = ListWidgetItem.font() 
			#font.setBold(True)							#Add Bold always
			for campaignold in campaigns_array: 		#If it's modified campaign,
				if campaignold[0] == campaignnew[0] and campaignold != campaignnew:		
					font.setItalic(True)				#Add Italic	
			if "New" in campaignnew[0]:					#If it's new campaign,	
				font.setItalic(True)					#Add Italic					
			for campaigndel in campaigns_del_array: 	#If it's deleted campaign,
				if campaigndel[0] == campaignnew[0]:		
					font.setStrikeOut(True)				#Add setStrikeOut too
			ListWidgetItem.setFont(font)		
			if campaign_id == campaignnew[0]: 				#If selected element is predefined
				self.listWidget_Campaigns_List.setCurrentItem(ListWidgetItem)
				self.campaign_selected(ListWidgetItem)

#============Clicked campaign's buttons=================#
	def clicked_retrieve(self): #Retrieve button clicked. Step one. Clear & disable Retrieve button
		is_filter_fine = True
		error_text = ""
		print("Validate campaign's filters")
		is_filter_fine, error_text = self.check_filter_campaigns()
		print(error_text)
		print("========================")
		if is_filter_fine:
			self.pushButton_Retrieve.setEnabled(False)
		self.setCursor(Qt.WaitCursor)
		QTimer.singleShot(300, lambda: self.clicked_retrieve2(is_filter_fine,error_text))

	def clicked_retrieve2(self,is_filter_fine,error_text_temp): #Retrieve button clicked. Step two. Get new data
		global is_all_fine, error_text, campaigns_array, campaigns_new_array, skillgroups_array,timezones_array
		global canCreate, canUpdate, canDelete, campaigns_del_array
		if  is_all_fine and is_filter_fine:
			error_text = error_text_temp
			#Clear arrays:
			campaigns_array = []
			campaigns_new_array = []
			campaigns_del_array = []
			timezones_array = []
			skillgroups_array = []
			print("Clear current campaigns list")
			self.listWidget_Campaigns_List.clear()
			self.selected_CampaignClear()
			print("========================")
		if  is_all_fine and is_filter_fine:
			print("Get timezones list")
			self.get_timezones("/unifiedconfig/config/timezone")
			print(error_text)
			print("========================")
		if  is_all_fine and is_filter_fine:
			print("Get campaigns list")
			self.get_campaigns("/unifiedconfig/config/campaign?sort=name%20asc&resultsPerPage=100")
			print(error_text)
			print("========================")			
			#unblock Create button				
			try:
				self.pushButton_Add.clicked.disconnect()
			except:
				pass
			if canCreate and is_all_fine:
				print('Admin has "canCreate" role. Unblocking Add button')
				self.pushButton_Add.setEnabled(True)
				self.pushButton_Add.clicked.connect(self.clicked_add)
				print("========================")
			else:
				self.pushButton_Add.setEnabled(False)
			#for Save button				
			try:
				self.pushButton_Save.clicked.disconnect()
			except:
				pass
			if canUpdate and is_all_fine:
				print('Admin has "canUpdate" role. Unblocking Save button')
				self.pushButton_Save.clicked.connect(self.clicked_save)
				print("========================")				
		if  is_all_fine and is_filter_fine:
			print("Get skill-groups list")
			self.get_skillgroups("/unifiedconfig/config/skillgroup?sort=name%20asc&resultsPerPage=100")
			print(error_text)
			print("========================")		
		if  is_all_fine and is_filter_fine:
			print("Filter skill-groups #1 (delete assigned to other API campaigns)")
			self.filter_skillgroups()
			print("========================")
			if ucce_sql_enable:
				print("Filter skill-groups #2 (delete assigned to other non-API campaigns)")
				self.rem_sg_sql()
				print(error_text)
				print("========================")
		if  is_all_fine and is_filter_fine:
			print("Apply campaigns filter")
			self.filter_campaigns()
			print("========================")
		if  is_all_fine and is_filter_fine:
			#campaigns_new_array = campaigns_array [:] #doesn't work because of nested array
			self.statusbar.setStyleSheet("color:green;font-weight:bold;")			
			campaigns_new_array = deepcopy(campaigns_array)
			print("Fill campaigns list")			
			self.fill_ListWidgetItem()
			self.listWidget_Campaigns_List.itemClicked.connect(self.campaign_selected)
			print("========================")
		else:
			self.statusbar.setStyleSheet("color:red;font-weight:bold;")
		self.setCursor(Qt.ArrowCursor)
		self.statusbar.showMessage(error_text)
		self.pushButton_Retrieve.setEnabled(True)

	def clicked_add(self): #Add campaign button clicked. Add empty campaign
		global campaigns_array, campaigns_new_array, timezones_array, skillgroups_array, canDelete, canUpdate
		global campaigns_del_array, ucce_username, ucce_pass, ucce_server
		campaign_sg_array = []
		if len(skillgroups_array) > 0:
			sg_array = [skillgroups_array[0][2],skillgroups_array[0][0],skillgroups_array[0][1],"","0","0","1","",""]
		elif len(campaigns_array) > 0:
			sg_array = [campaigns_array[0][43][0][0],campaigns_array[0][43][0][1],campaigns_array[0][43][0][2],
				"0","0","1","","",""]
		else:
			sg_array = ["","Not Found","","0","0","1","","",""]
		campaign_sg_array.append(sg_array)
		EndDate = (datetime.today() + timedelta(days=365)).strftime('%Y-%m-%d')
		StartDate = datetime.today().strftime('%Y-%m-%d')
		strrandom = ""		
		for i in range(0,10):
			strrandom += str(randint(0,9))
		if ["(UTC+00:00) Monrovia, Reykjavik","/unifiedconfig/config/timezone/Greenwich%20Standard%20Time"] in timezones_array:
			timezoneName = "(UTC+00:00) Monrovia, Reykjavik"
			timezoneURL = "/unifiedconfig/config/timezone/Greenwich%20Standard%20Time"
		else:
			timezoneName = timezones_array[int(len(timezones_array)/randint(1,10) - 1)][0]
			timezoneURL = timezones_array[int(len(timezones_array)/randint(1,10) - 1)][1]	
		campaing_array = ["New_" + strrandom,"New_" + strrandom,"","","true","3.0","abandonCall","","agentCampaign",
			"true","false","608","2500","112","5000","30000","New_" + strrandom,"PREDICTIVEONLY","true",EndDate,
			"18:00","true","false","1.50","3","2.00","1","4","70","1.00","useCampaignDN","100","60","60","30",
			"60","60","60",StartDate,"09:00",timezoneURL,timezoneName,"false",campaign_sg_array]
		print("Add campaign button clicked. Add empty campaign with id New_" + strrandom)
		campaigns_new_array.append(campaing_array)
		print("========================")
		print("And refill campaigns list with selected id New_" + strrandom)
		print("========================")		
		self.listWidget_Campaigns_List.clear()
		self.fill_ListWidgetItem("New_" + strrandom)

	def clicked_delete(self, campaign_id):  #Delete campaign button clicked
		global campaigns_array, campaigns_new_array, timezones_array, skillgroups_array, campaigns_del_array
		global canDelete, canUpdate, ucce_username, ucce_pass, ucce_server
		print("Delete campaign button clicked. Mark campaign with id " + campaign_id + " as deleted")		
		for campaign in campaigns_new_array:
			if campaign[0] == campaign_id:
				campaing_array = [campaign[0],campaign[1],campaign[2]]
				campaigns_del_array.append(campaing_array)
		print("========================")
		print("And refill campaigns list with selected id " + campaign_id)
		print("========================")				
		self.listWidget_Campaigns_List.clear()
		self.fill_ListWidgetItem(campaign_id)

	def clicked_save(self): #Save button clicked. Step one. Disable Save button
		self.pushButton_Save.setEnabled(False)
		self.setCursor(Qt.WaitCursor)
		QTimer.singleShot(300, lambda: self.clicked_save2())

	def clicked_save2(self): #Save campaign button clicked. Step two
		global is_all_fine, campaigns_array,campaigns_new_array,campaigns_del_array,ucce_username,ucce_pass,ucce_server
		print("Save button clicked")
		print("========================")
		is_all_fine = True
		result = ""
		print("Validate new configuration")
		is_validation, validation_error, camp_upd, camp_add, camp_del = self.check_new_campaign_data()
		print(validation_error)
		print("========================")
		if is_validation == False:
			#Error message
			err_check_new_data = QtWidgets.QMessageBox()
			err_check_new_data.setIcon(QtWidgets.QMessageBox.Critical)
			err_check_new_data.setWindowTitle("New data is incorrect")
			err_check_new_data.setText(validation_error)
			YesButton = err_check_new_data.addButton('OK', QtWidgets.QMessageBox.AcceptRole)
			err_check_new_data.exec()
		else:
			print("Start saving. First step - update")
			for key, value in camp_upd.items():
				name,url = key.split(":::")
				update_result = self.ucce_http_update(url,value)
				print(name + ": " + update_result)
				if update_result == "200 - successful": #update from campaigns_new_array to campaigns_array
					for campaign_new in campaigns_new_array:
						if campaign_new[1] == name:
							campaign_index = 0
							for campaign in campaigns_array:
								if campaign[0] == campaign_new[0]: #Check id
									try:
										campaign_new[3] = str(int(campaign_new[3]) + 2) #Update changeStamp
									except:
										pass
									campaigns_array [campaign_index] = deepcopy(campaign_new) #Copy but not link
								campaign_index += 1
							self.listWidget_Campaigns_List.clear()  #Clear campaign's list
							self.selected_CampaignClear()
							self.fill_ListWidgetItem()
				else:
					is_all_fine = False
				result += "Updating " + name + "...\tResult: " + update_result + "\n"
			print("========================")
			print("Second step - add")
			for name, value in camp_add.items():
				add_result, refURL, campaign_id = self.ucce_http_add(value)
				print(name + ": " + add_result)
				if add_result == "201 - successful": #Mark campaign as not new and copy to campaigns_array
					for campaign_new in campaigns_new_array:
						if campaign_new[1] == name:
							if len(campaign_id) > 0 and len(refURL) > 0:
								campaign_new[0] = campaign_id 	#Update id
								campaign_new[2] = refURL 		#Set url
							else:
								campaign_new[0] = campaign_new[0].replace("New_", "")
							campaign_new[3] = "12" #Set changeStamp
							campaigns_array.append(deepcopy(campaign_new)) #Copy but not link
							self.listWidget_Campaigns_List.clear()  #Clear campaign's list
							self.selected_CampaignClear()
							self.fill_ListWidgetItem()
				else:
					is_all_fine = False							
				result += "Adding " + name + "...\tResult: " + add_result + "\n"
			print("========================")
			print("Third step - delete")
			for name, value in camp_del.items():
				del_result = self.ucce_http_del(value)
				print(name + ": " + del_result)
				if del_result == "200 - successful": 
					for campaign_del in campaigns_del_array: #remove from campaigns_del_array
						if campaign_del[1] == name:
							campaigns_del_array.remove(campaign_del)
					for campaign_new in campaigns_new_array: #remove from campaigns_new_array
						if campaign_new[1] == name:
							campaigns_new_array.remove(campaign_new)
					for campaign in campaigns_array: #remove from campaigns_array
						if campaign[1] == name:
							campaigns_array.remove(campaign)							
					self.listWidget_Campaigns_List.clear()  #Clear campaign's list
					self.selected_CampaignClear()
					self.fill_ListWidgetItem()
				else:
					is_all_fine = False
				result += "Deleting " + name + "...\tResult: " + del_result + "\n"
			print("========================")
			#Result message
			result_message = QtWidgets.QMessageBox()
			if is_all_fine:
				print("All changes saved successfully")
				result_message.setIcon(QtWidgets.QMessageBox.Information)
				result_message.setWindowTitle("Processed successfully")				
			else:
				print("Something gone wrong while saving")
				result_message.setIcon(QtWidgets.QMessageBox.Warning)
				result_message.setWindowTitle("Processed with errors")
				self.pushButton_Save.setEnabled(True)
				is_all_fine = True
			print("========================")
			result_message.setText(result)
			OkButton = result_message.addButton('OK', QtWidgets.QMessageBox.AcceptRole)
			result_message.exec()					
		self.setCursor(Qt.ArrowCursor)

	def clicked_revert(self,campaign_id): #Revert campaign button clicked
		global campaigns_array, campaigns_new_array, campaigns_del_array, timezones_array, skillgroups_array
		global canDelete, canUpdate,ucce_username, ucce_pass, ucce_server
		is_not_deleted = True
		old_campaign = []
		print("Reverting changes")
		if "New" in campaign_id: #It's new campaign
			print("It was new campaign")
			for campaign in campaigns_new_array: 	#get new config
				if campaign[0] == campaign_id:
					print("Found it and delete")
					print("========================")
					campaigns_new_array.remove(campaign) #Удаляем из массива
					self.listWidget_Campaigns_List.clear()
					self.fill_ListWidgetItem()
					self.selected_CampaignClear()
		else: 
			for campaign in campaigns_array: 	#get old config
				if campaign[0] == campaign_id:
					old_campaign = deepcopy(campaign)
			for campaign in campaigns_del_array: #check if campaign was deleted
				if campaign[0] == campaign_id:
					print("It was deleted campaign")
					campaigns_del_array.remove(campaign)
					is_not_deleted = False
					print("Found it and undelete")
					print("========================")
					font = self.listWidget_Campaigns_List.currentItem().font()
					font.setStrikeOut(False)
					self.listWidget_Campaigns_List.currentItem().setFont(font)
			i = 0
			for campaign in campaigns_new_array: 	#get new config
				if campaign[0] == campaign_id:
					campaigns_new_array[i] = deepcopy(old_campaign)
					if is_not_deleted:
						print("It was modified campaign")						
						print("Found it and revert changes")
						print("========================")					
					self.listWidget_Campaigns_List.currentItem().setText(campaigns_new_array[i][1]) #Обновляем имя кампании в списке
					self.campaign_selected()
				i += 1

	def clicked_add_sg(self,campaign_id): #Add SG clicked
		global campaigns_array, skillgroups_array, campaigns_new_array, canUpdate
		print("Add one more skill-group to campaign: ")
		sg_campaign_del = []
		sg_campaign_old = []
		TableWidgetRow = self.tableWidget_SG.rowCount()
		self.tableWidget_SG.setRowCount(TableWidgetRow + 1)
		#Drop-down skill-group's list
		globals()["self.comboBox_CampSG" + str(TableWidgetRow)] = QtWidgets.QComboBox()

		for campaign_old in campaigns_array:		#Check if there are deleted SGs for this campaign
			if campaign_old[0] == campaign_id:
				sg_campaign_old = campaign_old[43]
				sg_campaign_del = deepcopy(sg_campaign_old)
		for campaign_new in campaigns_new_array:
			if campaign_new[0] == campaign_id:
				sg_campaign_new = deepcopy(campaign_new[43])
		for skillgroup in sg_campaign_old:
			for skillgroup_new in sg_campaign_new:
				if skillgroup[0] == skillgroup_new[0]:
					sg_campaign_del.remove(skillgroup)
					
		if len(sg_campaign_del) > 0 and len(skillgroups_array) > 0:
			print("Found & add previously deleted group(s) for this campaign")
			for sg_del in sg_campaign_del: 
				globals()["self.comboBox_CampSG" + str(TableWidgetRow)].addItem(sg_del[1])
			globals()["self.comboBox_CampSG" + str(TableWidgetRow)].setCurrentText(sg_campaign_del[0][1])
			sg_array = deepcopy(sg_campaign_del[0])
			print("Add non assigned free SGs from current config too")
			for all_skillgroup in skillgroups_array:
				globals()["self.comboBox_CampSG" + str(TableWidgetRow)].addItem(all_skillgroup[0])						
		elif len(skillgroups_array) > 0:
			print("Add non assigned free SGs from current config")
			for all_skillgroup in skillgroups_array:
				globals()["self.comboBox_CampSG" + str(TableWidgetRow)].addItem(all_skillgroup[0])
			globals()["self.comboBox_CampSG" + str(TableWidgetRow)].setCurrentText(skillgroups_array[0][0])
			sg_array = [skillgroups_array[0][2],skillgroups_array[0][0],skillgroups_array[0][1],"","0","0","1","",""]
		elif len(campaigns_array) > 0:
			print("There aren't free skill-groups. Add first group assigned to first existing campaigns")
			globals()["self.comboBox_CampSG" + str(TableWidgetRow)].addItem(campaigns_array[0][43][0][1])
			globals()["self.comboBox_CampSG" + str(TableWidgetRow)].setCurrentText(campaigns_array[0][43][0][1])
			sg_array = deepcopy(campaigns_array[0][43][0])
		elif len(sg_campaign_del) == 0:
			print("There aren't free skill-groups and existing campaigns")
			globals()["self.comboBox_CampSG" + str(TableWidgetRow)].addItem("Not Found")
			globals()["self.comboBox_CampSG" + str(TableWidgetRow)].setCurrentText("Not Found")
			sg_array = ["","Not Found","","0","0","1","","",""]	
			
		for campaign_new in campaigns_new_array:
			if campaign_new[0] == campaign_id:
				campaign_new[43].append(sg_array)
	
		globals()["self.comboBox_CampSG" + str(TableWidgetRow)].currentIndexChanged.connect(
			lambda: self.comboBox_CampSG_changed(campaign_id,TableWidgetRow))	
		if canUpdate:
			globals()["self.comboBox_CampSG" + str(TableWidgetRow)].setEnabled(True)
		else:
			globals()["self.comboBox_CampSG" + str(TableWidgetRow)].setEnabled(False)
		#Insert SG list
		self.tableWidget_SG.setCellWidget(TableWidgetRow,0, globals()["self.comboBox_CampSG" + str(TableWidgetRow)]) 
		
		try:
			self.tableWidget_SG.itemChanged.disconnect()
		except:
			pass
		try:
			self.tableWidget_SG.itemClicked.disconnect()
		except:
			pass			
		TableWidgetItem = QtWidgets.QTableWidgetItem()
		TableWidgetItem.setText(sg_array[5])				#overflowAgents
		self.tableWidget_SG.setItem(TableWidgetRow,1, TableWidgetItem)
		TableWidgetItem = QtWidgets.QTableWidgetItem()
		TableWidgetItem.setText(sg_array[3])				#dialedNumber
		self.tableWidget_SG.setItem(TableWidgetRow,2, TableWidgetItem)
		TableWidgetItem = QtWidgets.QTableWidgetItem()
		TableWidgetItem.setText(sg_array[6])				#recordsToCache
		self.tableWidget_SG.setItem(TableWidgetRow,3, TableWidgetItem)
		TableWidgetItem = QtWidgets.QTableWidgetItem()
		TableWidgetItem.setText(sg_array[4])				#ivrPorts
		self.tableWidget_SG.setItem(TableWidgetRow,4, TableWidgetItem)
		TableWidgetItem = QtWidgets.QTableWidgetItem()
		TableWidgetItem.setText(sg_array[7])				#ivrRoutePoint
		self.tableWidget_SG.setItem(TableWidgetRow,5, TableWidgetItem)
		TableWidgetItem = QtWidgets.QTableWidgetItem()
		TableWidgetItem.setText(sg_array[8])				#abandonedRoutePoint
		self.tableWidget_SG.setItem(TableWidgetRow,6, TableWidgetItem)
		self.tableWidget_SG.itemChanged.connect(lambda: self.tableWidget_SG_ItemChanged(campaign_id))
		self.tableWidget_SG.itemClicked.connect(lambda: self.tableWidget_SG_ItemClicked(campaign_id))
		print("========================")
		self.isCampaignChanged(campaign_id)

	def clicked_rem_sg(self,campaign_id,row): #Remove SG clicked
		global campaigns_new_array
		try:
			self.pushButton_Remove_SG.clicked.disconnect()
		except:
			pass
		self.pushButton_Remove_SG.setEnabled(False)		
		self.tableWidget_SG.removeRow(row)
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				print("Remove SG " + campaign[43][row][1] + " from campaign " + campaign[1])
				campaign[43].pop(row)
				print("========================")
		self.isCampaignChanged(campaign_id)
	
#============Filters changed============================#
	def comboCondition_changed(self):
		CurrentText = str(self.comboBox_Condition.currentText())
		if CurrentText == "Is Blank":
			self.comboBox_Value.setCurrentText('')
			self.comboBox_Value.setEnabled(False)
		else:
			self.comboBox_Value.setEnabled(True)	

	def comboFilter_changed(self):
		CurrentText_Filter = str(self.comboBox_Filter.currentText())
		if CurrentText_Filter in ["Campaign Enable","Abandon Calls Limit Enable",
				"Personalized Callback","Enable CPA","Enable IP AMD"]:
			self.comboBox_Condition.setEnabled(True)
			self.comboBox_Condition.clear()
			self.comboBox_Condition.addItem("Equal")
			self.comboBox_Condition.addItem("Not Equal")
			self.comboBox_Value.setEnabled(True)
			self.comboBox_Value.setEditable(False)
			self.comboBox_Value.clear()			
			self.comboBox_Value.setStyleSheet("border: 1px solid gray;")
			self.comboBox_Value.addItem("Checked")
			self.comboBox_Value.addItem("Not Checked")
		elif CurrentText_Filter in ["Campaign Name","Campaign Description","Campaign Prefix Digits"]:
			self.comboBox_Condition.setEnabled(True)
			self.comboBox_Condition.clear()
			self.comboBox_Condition.addItem("Contains")
			self.comboBox_Condition.addItem("Ends With")
			self.comboBox_Condition.addItem("Starts With")
			self.comboBox_Condition.addItem("Is Blank")
			self.comboBox_Value.setEnabled(True)
			self.comboBox_Value.setEditable(True)
			self.comboBox_Value.clear()			
			self.comboBox_Value.setStyleSheet("QComboBox{border: 1px solid gray; background-color : white;}\n"
				"QComboBox::drop-down{border: 0px;}\n"
				"QComboBox::down-arrow{image: url(noimg);border-width: 0px;}")
		elif CurrentText_Filter == "Dialing Mode":
			self.comboBox_Condition.setEnabled(True)
			self.comboBox_Condition.clear()
			self.comboBox_Condition.addItem("Equal")
			self.comboBox_Condition.addItem("Not Equal")
			self.comboBox_Value.setEnabled(True)
			self.comboBox_Value.setEditable(False)
			self.comboBox_Value.clear()			
			self.comboBox_Value.setStyleSheet("border: 1px solid gray;")
			self.comboBox_Value.addItem("PREDICTIVEONLY")
			self.comboBox_Value.addItem("PROGRESSIVEONLY")
			self.comboBox_Value.addItem("PREVIEWONLY")
			self.comboBox_Value.addItem("PREVIEWDIRECTONLY")
			self.comboBox_Value.addItem("INBOUND")
		elif CurrentText_Filter in ["Lines Per Agent","Maximum Lines Per Agent","Minimum Call Duration",
				"Abandon Calls Limit Percent","No Answer Ring Limit","Maximum Attempts","Dialer Abandoned Delay",
				"No Answer Delay","Busy Signal Delay","Customer Abandoned Delay","Answering Machine Delay",
				"Start Hours","Start Minutes","Start Date","End Hours","End Minutes","End Date"]: 
			self.comboBox_Condition.setEnabled(True)
			self.comboBox_Condition.clear()
			self.comboBox_Condition.addItem("Equal")
			self.comboBox_Condition.addItem("Greater Then")
			self.comboBox_Condition.addItem("Less Then")
			self.comboBox_Condition.addItem("Not Equal")
			self.comboBox_Value.setEnabled(True)
			self.comboBox_Value.setEditable(True)
			self.comboBox_Value.clear()			
			self.comboBox_Value.setStyleSheet("QComboBox{border: 1px solid gray; background-color : white;}\n"
						"QComboBox::drop-down{border: 0px;}\n"
						"QComboBox::down-arrow{image: url(noimg);border-width: 0px;}")
		elif CurrentText_Filter == "Campaign Type":
			self.comboBox_Condition.setEnabled(True)
			self.comboBox_Condition.clear()
			self.comboBox_Condition.addItem("Equal")
			self.comboBox_Condition.addItem("Not Equal")
			self.comboBox_Value.setEnabled(True)
			self.comboBox_Value.setEditable(False)
			self.comboBox_Value.clear()			
			self.comboBox_Value.setStyleSheet("border: 1px solid gray;")
			self.comboBox_Value.addItem("agentCampaign")
			self.comboBox_Value.addItem("ivrCampaign")
		else: #NONE or error
			self.comboBox_Condition.setEnabled(False)
			self.comboBox_Condition.clear()
			self.comboBox_Value.setEnabled(False)
			self.comboBox_Value.clear()
			self.comboBox_Value.setCurrentText('')

#============Campaign changed===========================#																		
	def lineEdit_Name_Edited(self,campaign_id):
		global campaigns_new_array,campaigns_array
		newtext = self.lineEdit_Name.text()
		self.listWidget_Campaigns_List.currentItem().setText(newtext) #Обновляем имя кампании в списке
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[1] = newtext			#And Update
		self.isCampaignChanged(campaign_id)

	def checkBox_Campaign_Enabled_Changed(self,campaign_id):
		global campaigns_new_array,campaigns_array
		state = self.checkBox_Campaign_Enabled.checkState()
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				if state == 2:					#And Update
					campaign[18] = "true"
				else:
					campaign[18] = "false"
		self.isCampaignChanged(campaign_id)

	def comboDialing_Mode_changed(self,campaign_id):
		global campaigns_new_array,campaigns_array
		CurrentText = str(self.comboBox_Dialing_Mode.currentText())
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[17] = CurrentText			#And Update
		self.isCampaignChanged(campaign_id)	

	def comboCampaign_Type_changed(self,campaign_id):
		global campaigns_new_array,campaigns_array
		CurrentText = str(self.comboBox_Campaign_Type.currentText())
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[8] = CurrentText			#And Update
				if CurrentText == "agentCampaign" and self.checkBox_CPA_Enable.isChecked() and self.checkBox_IP_AMD_Enable.isChecked():
					self.radioButton_Transfer_Agent.setEnabled(True)
				else:
					self.radioButton_Transfer_Agent.setEnabled(False)
					if self.radioButton_Transfer_Agent.isChecked():
						self.radioButton_Transfer_Agent.setChecked(False)
						self.radioButton_Aban_Call.setChecked(True)
						campaign[6] = "abandonCall"
		self.isCampaignChanged(campaign_id)	

	def lineEdit_Description_Edited(self,campaign_id):
		global campaigns_new_array,campaigns_array
		newtext = self.lineEdit_Description.text()
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[16] = newtext			#And Update
		self.isCampaignChanged(campaign_id)	

	def lineEdit_Lines_Edited(self,campaign_id):
		global campaigns_new_array,campaigns_array
		newtext = self.lineEdit_Lines.text().replace(",",".")
		try:
			newtext = str(float(newtext))
		except:
			pass	
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[23] = newtext			#And Update
		self.isCampaignChanged(campaign_id)	

	def lineEdit_MaxLines_Edited(self,campaign_id):
		global campaigns_new_array,campaigns_array
		newtext = self.lineEdit_Max_Lines.text().replace(",",".")
		try:
			newtext = str(float(newtext))
		except:
			pass		
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[25] = newtext			#And Update
		self.isCampaignChanged(campaign_id)		

	def lineEdit_Prefix_Edited(self,campaign_id):
		global campaigns_new_array,campaigns_array
		newtext = self.lineEdit_Prefix.text()
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[7] = newtext			#And Update
		self.isCampaignChanged(campaign_id)	

	def checkAban_Call_Limit_Changed(self,campaign_id):
		global campaigns_new_array,campaigns_array
		state = self.checkBox_Aban_Call_Limit.checkState()
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				if state == 2:					#And Update
					campaign[4] = "true"
					self.lineEdit_Aban_Call_Limit.setEnabled(True)
				else:
					campaign[4] = "false"
					self.lineEdit_Aban_Call_Limit.setEnabled(False)
		self.isCampaignChanged(campaign_id)	

	def lineEdit_Aban_Call_Limit_Edited(self,campaign_id):
		global campaigns_new_array,campaigns_array
		newtext = self.lineEdit_Aban_Call_Limit.text().replace(",",".")
		try:
			newtext = str(float(newtext))
		except:
			pass		
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[5] = newtext			#And Update
		self.isCampaignChanged(campaign_id)	

	def lineEdit_Calls_Per_Adj_Edited(self,campaign_id):
		global campaigns_new_array,campaigns_array
		newtext = self.lineEdit_Calls_Per_Adjustment.text()
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[28] = newtext			#And Update
		self.isCampaignChanged(campaign_id)	

	def lineEdit_Max_Gain_Edited(self,campaign_id):
		global campaigns_new_array,campaigns_array
		newtext = self.lineEdit_Max_Gain.text().replace(",",".")
		try:
			newtext = str(float(newtext))
		except:
			pass		
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[29] = newtext			#And Update
		self.isCampaignChanged(campaign_id)	

	def lineEdit_NoAnsRingLimit_Edited(self,campaign_id):
		global campaigns_new_array,campaigns_array
		newtext = self.lineEdit_No_Answe_Rin_Limit.text()
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[27] = newtext			#And Update
		self.isCampaignChanged(campaign_id)	

	def lineEdit_Attempts_Edited(self,campaign_id):
		global campaigns_new_array,campaigns_array
		newtext = self.lineEdit_Attempts.text()
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[24] = newtext			#And Update
		self.isCampaignChanged(campaign_id)	

	def lineEdit_MinCallDur_Edited(self,campaign_id):
		global campaigns_new_array,campaigns_array
		newtext = self.lineEdit_Min_Call_Duration.text()
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[26] = newtext			#And Update
		self.isCampaignChanged(campaign_id)	

	def checkPers_CB_Changed(self,campaign_id):
		global campaigns_new_array,campaigns_array
		state = self.checkBox_Pers_Callback.checkState()
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				if state == 2:					#And Update
					campaign[42] = "true"
					self.comboBox_Pers_Callback.setEnabled(True)
				else:
					campaign[42] = "false"
					self.comboBox_Pers_Callback.setEnabled(False)
		self.isCampaignChanged(campaign_id)	

	def comboPers_CB_changed(self,campaign_id):
		global campaigns_new_array,campaigns_array
		CurrentText = str(self.comboBox_Pers_Callback.currentText())
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[30] = CurrentText			#And Update
		self.isCampaignChanged(campaign_id)	

	def lineEdit_NoAnsDelay_Edited(self,campaign_id):
		global campaigns_new_array,campaigns_array
		newtext = self.lineEdit_No_Answer_Delay.text()
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[37] = newtext			#And Update
		self.isCampaignChanged(campaign_id)	

	def lineEdit_BusyDelay_Edited(self,campaign_id):
		global campaigns_new_array,campaigns_array
		newtext = self.lineEdit_Busy_Delay.text()
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[33] = newtext			#And Update
		self.isCampaignChanged(campaign_id)	

	def lineEdit_CustAbanDelay_Edited(self,campaign_id):
		global campaigns_new_array,campaigns_array
		newtext = self.lineEdit_Customer_Aban_Delay.text()
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[34] = newtext			#And Update
		self.isCampaignChanged(campaign_id)	
		
	def lineEdit_DialerAbanDelay_Edited(self,campaign_id):
		global campaigns_new_array,campaigns_array
		newtext = self.lineEdit_Dialer_Aban_Delay.text()
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[36] = newtext			#And Update
		self.isCampaignChanged(campaign_id)	

	def lineEdit_AMDDelay_Edited(self,campaign_id):
		global campaigns_new_array,campaigns_array
		newtext = self.lineEdit_AMD_Delay.text()
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[32] = newtext			#And Update
		self.isCampaignChanged(campaign_id)	

	def lineEdit_CustNotHomeDelay_Edited(self,campaign_id):
		global campaigns_new_array,campaigns_array
		newtext = self.lineEdit_Customer_Home_Delay.text()
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[35] = newtext			#And Update
		self.isCampaignChanged(campaign_id)	

	def checkCPA_Enable_Changed(self,campaign_id):
		global campaigns_new_array,campaigns_array
		state = self.checkBox_CPA_Enable.checkState()
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				if state == 2:					#And Update
					campaign[9] = "true"
					self.checkBox_Record_CPA.setEnabled(True)
					self.checkBox_IP_AMD_Enable.setEnabled(True)
				else:
					campaign[9] = "false"
					self.checkBox_Record_CPA.setEnabled(False)
					self.checkBox_IP_AMD_Enable.setEnabled(False)
		self.isCampaignChanged(campaign_id)	

	def checkRecord_CPA_Changed(self,campaign_id):
		global campaigns_new_array,campaigns_array
		state = self.checkBox_Record_CPA.checkState()
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				if state == 2:					#And Update
					campaign[10] = "true"
				else:
					campaign[10] = "false"
		self.isCampaignChanged(campaign_id)	

	def checkAMD_Enable_Changed(self,campaign_id):
		global campaigns_new_array,campaigns_array
		state = self.checkBox_IP_AMD_Enable.checkState()
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				if state == 2:					#And Update
					campaign[21] = "true"
					self.radioButton_Aban_Call.setEnabled(True)
					self.radioButton_Transfer_IVR.setEnabled(True)
					if campaign[8] == "agentCampaign":
						self.radioButton_Transfer_Agent.setEnabled(True)
					else:
						self.radioButton_Transfer_Agent.setEnabled(False)
				else:
					campaign[21] = "false"
					self.radioButton_Aban_Call.setEnabled(False)
					self.radioButton_Transfer_IVR.setEnabled(False)
					self.radioButton_Transfer_Agent.setEnabled(False)					
		self.isCampaignChanged(campaign_id)	

	def radioButtons_Changed(self,campaign_id):
		global campaigns_new_array,campaigns_array
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				if self.radioButton_Aban_Call.isChecked():
					campaign[6] = "abandonCall"
					self.checkBox_Terminate_Tone_Detect.setEnabled(False)
					self.checkBox_Terminate_Tone_Detect.setChecked(False)
				elif self.radioButton_Transfer_Agent.isChecked():
					campaign[6] = "transferToAgent"
					self.checkBox_Terminate_Tone_Detect.setEnabled(False)
					self.checkBox_Terminate_Tone_Detect.setChecked(False)
				else:
					campaign[6] = "transferToIVRRoutePoint"
					self.checkBox_Terminate_Tone_Detect.setEnabled(True)
		self.isCampaignChanged(campaign_id)				

	def checkTerm_Tone_Detect_Changed(self,campaign_id):
		global campaigns_new_array,campaigns_array
		state = self.checkBox_Terminate_Tone_Detect.checkState()
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				if state == 2:					#And Update
					campaign[22] = "true"
				else:
					campaign[22] = "false"
		self.isCampaignChanged(campaign_id)	

	def lineEdit_MinSilPer_Edited(self,campaign_id):
		global campaigns_new_array,campaigns_array
		newtext = self.lineEdit_Minimum_Silence_Period.text()
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[11] = newtext			#And Update
		self.isCampaignChanged(campaign_id)	

	def lineEdit_AnalysPer_Edited(self,campaign_id):
		global campaigns_new_array,campaigns_array
		newtext = self.lineEdit_Analysis_Period.text()
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[12] = newtext			#And Update
		self.isCampaignChanged(campaign_id)	

	def lineEdit_MinValSpeech_Edited(self,campaign_id):
		global campaigns_new_array,campaigns_array
		newtext = self.lineEdit_Minimum_Valid_Speech.text()
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[13] = newtext			#And Update
		self.isCampaignChanged(campaign_id)

	def lineEdit_MaxAnalysTime_Edited(self,campaign_id):
		global campaigns_new_array,campaigns_array
		newtext = self.lineEdit_Maximum_Analysis_Time.text()
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[14] = newtext			#And Update
		self.isCampaignChanged(campaign_id)	

	def lineEdit_MaxTermTone_Edited(self,campaign_id):
		global campaigns_new_array,campaigns_array
		newtext = self.lineEdit_Maximum_Term_Tone_Analysis.text()
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[15] = newtext			#And Update
		self.isCampaignChanged(campaign_id)	

	def comboTimeZone_changed(self,campaign_id):
		global campaigns_new_array,campaigns_array,timezones_array
		CurrentText = str(self.comboBox_TimeZone.currentText())
		timezone_url = ""
		for timezone in timezones_array: 	#Try to find in timezones_array
			if timezone[0] == CurrentText:
				timezone_url = timezone[1]		
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[41] = CurrentText			#And Update
				campaign[40] = timezone_url
		self.isCampaignChanged(campaign_id)	

	def lineEdit_StartDate_Edited(self,campaign_id):
		global campaigns_new_array,campaigns_array
		newtext = self.lineEdit_StartDate.text()
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[38] = newtext			#And Update
		self.isCampaignChanged(campaign_id)

	def lineEdit_StartTime_Edited(self,campaign_id):
		global campaigns_new_array,campaigns_array
		newtext = self.lineEdit_StartTime.text()
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[39] = newtext			#And Update
		self.isCampaignChanged(campaign_id)	
			
	def lineEdit_EndDate_Edited(self,campaign_id):
		global campaigns_new_array,campaigns_array
		newtext = self.lineEdit_EndDate.text()
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[19] = newtext			#And Update
		self.isCampaignChanged(campaign_id)	
			
	def lineEdit_EndTime_Edited(self,campaign_id):
		global campaigns_new_array,campaigns_array
		newtext = self.lineEdit_EndTime.text()
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[20] = newtext			#And Update
		self.isCampaignChanged(campaign_id)

	def lineEdit_Reserv_Perc_Edited(self,campaign_id):
		global campaigns_new_array,campaigns_array
		newtext = self.lineEdit_Reserv_Percentage.text()
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[31] = newtext			#And Update
		self.isCampaignChanged(campaign_id)

	def tableWidget_SG_ItemChanged(self,campaign_id):
		global campaigns_new_array,campaigns_array
		item = self.tableWidget_SG.currentItem()
		row = self.tableWidget_SG.currentRow()
		column = self.tableWidget_SG.currentColumn()
		if column == 0:
			sg_id = 1
		elif column == 1:
			sg_id = 5
		elif column == 2:
			sg_id = 3
		elif column == 3:
			sg_id = 6
		elif column == 4:
			sg_id = 4
		elif column == 5:
			sg_id = 7
		elif column == 6:
			sg_id = 8
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				campaign[43][row][sg_id] = item.text()
		self.isCampaignChanged(campaign_id)	

	def tableWidget_SG_ItemClicked(self,campaign_id):
		global canUpdate
		if canUpdate:
			print('TableWidget SG ItemClicked. Admin has "canUpdate" role. Enable Remove_SG button')
			row = self.tableWidget_SG.currentRow()
			try:
				self.pushButton_Remove_SG.clicked.disconnect()
			except:
				pass
			self.pushButton_Remove_SG.clicked.connect(lambda: self.clicked_rem_sg(campaign_id,row))		
			self.pushButton_Remove_SG.setEnabled(True)
			print("========================")

	def comboBox_CampSG_changed(self,campaign_id,sg_id):
		global campaigns_new_array,campaigns_array,skillgroups_array
		
		self.tableWidget_SG_ItemClicked(campaign_id)
		
		CurrentText = globals()["self.comboBox_CampSG" + str(sg_id)].currentText()
		new_id = ""
		new_url = ""
		
		for campaign_old in campaigns_array:	#Try to find ID & URL in campaign_old array
			campaign_old_sg_array = deepcopy(campaign_old[43])
			for skillgroup_old in campaign_old_sg_array:
				if skillgroup_old[1] == CurrentText:
					 new_id = skillgroup_old[0]	
					 new_url = skillgroup_old[2]
					 
		for all_skillgroup in skillgroups_array: #Try to find ID & URL in skillgroups_array (non assigned)
			if all_skillgroup[0] == CurrentText:
				new_id = all_skillgroup[2]	
				new_url = all_skillgroup[1]
		
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array & sg array
			if campaign[0] == campaign_id:
				#And Update
				campaign[43][sg_id][0] = new_id
				campaign[43][sg_id][1] = CurrentText	
				campaign[43][sg_id][2] = new_url
		
		self.isCampaignChanged(campaign_id)		

	def isCampaignChanged(self,campaign_id):
		global campaigns_new_array,campaigns_array,campaigns_del_array,canDelete,canUpdate
		old_campaign = []
		new_campaign = []
		for campaign in campaigns_new_array: 	#Try to find in campaigns_new_array
			if campaign[0] == campaign_id:
				new_campaign = deepcopy(campaign)
				new_campaign[43].sort()			#sorting SGs in new campaign
		if not "New" in campaign_id: #It's not new campaign. Try to find in campaigns_array 
			for campaign in campaigns_array:
				if campaign[0] == campaign_id:
					old_campaign = deepcopy(campaign)
					old_campaign[43].sort()		#sorting SGs in old campaign
		if old_campaign != new_campaign: #Campaign Is modified de-facto
			font = self.listWidget_Campaigns_List.currentItem().font()
			font.setItalic(True)
			self.listWidget_Campaigns_List.currentItem().setData(Qt.FontRole, font) #выделяем текущий элемент
			self.pushButton_Revert.setEnabled(True)
		else:
			font = self.listWidget_Campaigns_List.currentItem().font()
			font.setItalic(False)
			self.listWidget_Campaigns_List.currentItem().setData(Qt.FontRole, font) #снимаем выделение
			self.pushButton_Revert.setEnabled(False)
		if (campaigns_array != campaigns_new_array or len(campaigns_del_array) > 0) and canUpdate:
			self.pushButton_Save.setEnabled(True)
		else:
			self.pushButton_Save.setEnabled(False)
		#Checks if current campaign was deleted
		for campaign in campaigns_del_array:
			if campaign[0] == campaign_id and canDelete:
				self.pushButton_Revert.setEnabled(True)
				self.pushButton_Delete.setEnabled(False)	

#=======================================================#

class AboutDialogNew(QtWidgets.QDialog,About_Dialog):
	def __init__(self):
		super().__init__()
		self.setupUi(self)
		
class ConnectionDialogNew(QtWidgets.QDialog,Connection_Dialog):
	def __init__(self):
		super().__init__()
		self.setupUi(self)

def main():
    app = QtWidgets.QApplication(argv)  # Новый экземпляр QApplication
    window = CampaignManagerApp()  # Создаём объект класса CampaignManagerApp
    window.show()  # Показываем окно
    exit(app.exec_())  # и запускаем приложение

if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
