#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import time
import datetime
import subprocess
import quickscript.api as quick

SCREEN_COUNT = {}
DIR_PATH = '~/Documents'
TEST_RESULTS={}
REPORT = '\nFinal Results of Quicklook Tests'

#Method to check a pane name
def current_buddy_pane(device):
	assert device != None, 'No Device Provided for Pane Detection'
	cur_dev = quick.select_device(device)
	nav_bar = quick.inspect('NavigationBar')
	try:
		return_val = str(nav_bar['name'])
		return return_val
	except:
		return 'Not in Buddy'
	
def pane_check(device =  None, expected_pane = None):
	pane = current_buddy_pane(device)
	if pane == expected_pane:
		log_info(' - Expected Pane ({0}) Entered'.format(pane))
		return True
	else:
		log_info(' - Unexpected Pane : {0}'.format(pane))
		return False


#Method to tap a value after verifiying it exists
def press(item, modifiers=None):
	quick.wait(str(item), modifiers=modifiers)
	quick.tap(str(item), modifiers=modifiers)
#Method to tap a partial value after verifying it exists

#Method to check for springboard being loaded

#Methods to collect and place a screenshot from tests
def ql_directory_setup(user = 'jason'): #defaulted to my user name
	global DIR_PATH
	today = datetime.date.today()
	test_date = today.strftime('%b_%d_%Y')
	dir_path = '/Users/{0}/Documents/iOS_Quicklooks_{1}'.format(user, test_date)
	if os.path.exists(dir_path):
		DIR_PATH = dir_path
	else:
		os.mkdir(dir_path)
		DIR_PATH = dir_path
	f = open('{0}/TestLog_{1}'.format(dir_path,test_date), 'w+')
	log_info(' - Test Directory Path Created')

def screen_log(dir_path = DIR_PATH, device = None):
	assert len(quick.get_devices()) > 1, 'No Attached Devices'
	pane = current_buddy_pane(device)
	if pane in SCREEN_COUNT:
		current_count = SCREEN_COUNT.get(pane)
		SCREEN_COUNT.update({pane : current_count + 1})
	else:
		SCREEN_COUNT.update({pane: 1})
	screen_path = '{0}/{1}_{2}'.format(DIR_PATH,pane,str(SCREEN_COUNT.get(pane)))
	quick.screenshot(file_path = screen_path, device = device)

def log_info(message = ''):
	today = datetime.date.today()
	test_date = today.strftime('%b_%d_%Y')
	time = str(datetime.datetime.now())
	f = open('{0}/TestLog_{1}'.format(DIR_PATH,test_date), 'a+')
	f.write(time)
	f.write(message + '\n')
	f.close

def pass_fail(expected, test_case = None, test_num = 0):
	global TEST_RESULTS
	device = quick.get_current_device()
	if pane_check(device=device, expected_pane=expected):
		log_info(" - QL Test {0}: {1} Ran Successfully".format(test_num, test_case)) 
		TEST_RESULTS.update({test_num: 'Pass'})

	else:
		log_info(' - QL Test {0}: {1} Resulted in an unexpected state.'.format(test_num, test_case))
		TEST_RESULTS.update({test_num: 'Fail'})
		screen_log(device=device)

def report():
	global REPORT
	global TEST_RESULTS
	sorted_keys = sorted(TEST_RESULTS.keys())
	for _ in sorted_keys:
		REPORT += ('\nTest {0}: {1}'.format(_, TEST_RESULTS.get(_)))
	return REPORT

#Method for restoring from backup



#Object to hold variables being used for a particular test run
#customizing this object determines pane logic during test run
class FlowState(object):
	def __init__(self):

		#A Device must be assigned for use.
		self.primary_device  = None

		#Device used as a source for any type of data migration
		self.source_device = None

		#Default Languae for Buddy
		self.language_primary = 'English'

		#Secondary Language used for testing the Language Pane
		self.language_tmp = None

		#Region
		self.region = 'United States'
		self.region_tmp = None

		#iCloud sign in info
		self.iCloud_account = None
		self.iCloud_password = None

		#Siri
		self.siri_on = False

		#Screentime
		self.screentime_on = True

		#WiFi Settings
		self.wifi_ssid = 'AppleWiFi'
		self.wifi_password = None
		self.protected_wifi = False

		#Passcode
		self.skip_passcode = True
		self.alpha_passcode = None
		self.six_num_passcode = None #numeric passcodes can be set as integers
		self.four_num_passcode = None #or numeric strings


		#Device Type

#Methods for handling the panes of Buddy

def language_chooser(FlowState):
	device = FlowState.primary_device
	quick.unlock(device = device)
	#This makes language localization available and prevents a reboot mid test.
	quick.set_localized_mode(True)
	quick.set_localized_mode(False)
	pane_check(device = device, expected_pane = 'BuddyLanguage')
	if FlowState.language_tmp is not None:
		screen_log(device = device)
		quick.wait(FlowState.language_tmp)
		quick.tap(FlowState.language_tmp)
		quick.tap('StaticText', index = 2) #Selects the Unites States no matter what 
		quick.set_localized_mode(True)
		the_back = quick.get_localized_string('GENERIC_BACK_BUTTON', partial=False)
		quick.set_localized_mode(False)
		press(the_back)
		quick.tap(the_back)
		press(FlowState.language_primary)
		pass_fail(expected='BuddyLocale', test_case='Language Chooser Test', test_num=2)

	else:
		screen_log(device = device)
		press(FlowState.language_primary)
		log_info(" - Language Chooser Successful") 

def region_chooser(FlowState):
	device = FlowState.primary_device
	pane_check(device=device, expected_pane='BuddyLocale')
	if FlowState.region_tmp is not None:
		screen_log(device=device)
		press(FlowState.region_tmp)
		quick.set_localized_mode(True)
		the_back = quick.get_localized_string('GENERIC_BACK_BUTTON', partial=False)
		quick.set_localized_mode(False)
		press(the_back)
		press('United States')
		quick.wait(5)
		pass_fail(expected='BuddyProximitySetup', test_case = 'Region Chooser Test', test_num=3)
		
	else:
		press('United States')
		log_info(' - Region Chooser Successful')

def prox_pane():
	press('Set Up Manually')

def wifi_chooser(FlowState):
	ssid = FlowState.wifi_ssid
	device = FlowState.primary_device
	pane_check(device=device, expected_pane='WFBuddyView')
	if FlowState.protected_wifi:
		press(ssid)
		quick.wait('Join')
		quick.type_string(FlowState.wifi_password)
		quick.tap('Join')
		while not pane_check(device=device, expected_pane='OBPrivacySplash'):
			quick.wait(3)
		pass_fail(expected='OBPrivacySplash', test_case='Protected Network Test', test_num=28)
	else:
		press(ssid)
		quick.wait('Continue')
		pass_fail(expected='OBPrivacySplash', test_case='Open Network Test', test_num=5)

def privacy_pane():
	press('Continue')

def skip_bio(FlowState):
	device = FlowState.primary_device
	pane = current_buddy_pane(device=device)
	if pane == 'PearlSplash':
		quick.tap('Set Up Later in Settings')
		press("Don't Use", modifiers = [quick.BUTTON])
		log_info(' - FaceID skipped')
	elif pane == 'BuddyMesaEnrollment':
		quick.tap("Set Up Touch ID Later")
		quick.wait('Are you sure you don’t want to use Touch ID?', modifiers = [quick.ALERT])
        quick.tap('Button', index = 4)
        log_info(' - TouchID skipped')
    
def passcode_pane(FlowState):
	device = FlowState.primary_device
	if FlowState.skip_passcode:
		screen_log(device=device)
		quick.wait('Passcode', modifiers = ['partial'])
		quick.tap('Button', index = 2)
		press('Don', modifiers = [quick.BUTTON, 'partial'])
		press('Don', modifiers = [quick.ALERT, 'partial'])
		pass_fail(expected='DeviceRestoreChoice', test_case = 'Skip Passcode', test_num=9)
	else:
		if FlowState.alpha_passcode != None:
			passcode = str(FlowState.alpha_passcode)
			if len(passcode) < 5:
				passcode = 'apple1984'
			inc = passcode + 'a'
			screen_log(device=device)
			quick.wait('Passcode', modifiers = ['partial'])
			quick.tap('Button', index = 2)
			press('Custom Alphanumeric Code')
			quick.type_string(inc)
			quick.type_string(passcode)
			quick.type_string(passcode)
			quick.type_string(passcode)
			pass_fail(expected = 'DeviceRestoreChoice' , test_case = 'Alphanumeric Passcode', test_num=33)
		elif FlowState.six_num_passcode != None:
			passcode = str(FlowState.six_num_passcode)
			if len(passcode) != 6 or int(passcode) == 999999:
				passcode = '100000'
			inc = str(int(passcode) + 1) 
			screen_log(device=device)
			quick.type_string(inc)
			quick.type_string(passcode)
			quick.type_string(passcode)
			quick.type_string(passcode)	
			pass_fail(expected = 'DeviceRestoreChoice' , test_case = 'Alphanumeric Passcode', test_num=32)
		"""Four digit passcodes are not currently part of testing.	
		elif FlowState.four_num_passcode != None:
			passcode = str(FlowState.four_num_passcode)
			if len(passcode) != 4 or int(passcode) == 9999:
				passcode = '1000'			
			inc = str(int(passcode) + 1)
			screen_log(device=device)
			quick.wait('Passcode', modifiers = ['partial'])
			quick.tap('Button', index = 2)
			press('4-Digit Numeric Code')
			quick.type_string(inc)
			quick.type_string(passcode)
			quick.type_string(passcode)
			quick.type_string(passcode)			
			"""
		else:
			#reverts back to a no password check if other options not available
			log_info(' - No password details provided. Skipping password input')
			FlowState.skip_passcode = True
			passcode_pane(FlowState)





def main():
	#This main represents one pass through buddy, it will later be defined as a method
	#for this particular set of test cases.
	ql_directory_setup() #This statement will be part of the final main and only be run once per set of tests
	log_info(' - Beginning Test')
	flow = FlowState()
	flow.primary_device = quick.select_device(1)
	flow.language_tmp  = 'Deutsch'
	flow.region_tmp = 'Australia'
	flow.wifi_ssid="Suiteamerica450"
	flow.wifi_password='450suite'
	flow.protected_wifi=True
	language_chooser(flow)
	region_chooser(flow)
	prox_pane()
	wifi_chooser(flow)
	privacy_pane()
	skip_bio(flow)
	passcode_pane(flow)
	results = report()
	log_info(results)
	

	



	

main()