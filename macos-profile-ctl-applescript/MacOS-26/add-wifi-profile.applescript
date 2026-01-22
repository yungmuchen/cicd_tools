
-- Load the external script file for common parameters
--set ProfileCommonUtil to load script file (POSIX file "/Users/tester/wifi-profile/ProfileCommonUtil.scpt")
global ProfileCommonUtil
set ProfileCommonUtil to load script file ((path to home folder as text) & "wifi-profile:ProfileCommonUtil.scpt")

ProfileCommonUtil's close_system_setting_window()

tell application "System Events"
	tell application process "System Settings"
		activate
		delay 1
		
		
		-- Navigate directly to Device Management
		do shell script "open x-apple.systempreferences:com.apple.Profiles-Settings.extension"
		
		repeat until window "Device Management" exists
			delay 1
		end repeat
		
		-- click add profile icon under device management window
		tell window "Device Management"
			tell splitter group 1 of group 1
				tell scroll area 1 of group 1 of group 3
					tell group 2
						click button 1
						delay 1
					end tell
				end tell
			end tell
		end tell
		
	end tell
end tell

-- select WiFi profile via NSOpenPanel
tell application "System Events"
	tell process "System Settings"
		-- Wait for the file selection sheet/dialog to appear
		repeat until exists window 1
			delay 1
		end repeat
		
		set my_profile_path to ProfileCommonUtil's WiFiProfilePath
		
		-- Use the 'Go to Folder' shortcut (Cmd+Shift+G) to enter the path
		keystroke "g" using {command down, shift down}
		delay 1
		-- due to UI delay, sometime we need to type shortcut twice
		keystroke "g" using {command down, shift down}
		
		-- Wait for the 'Go to Folder' sheet
		repeat until exists sheet 1 of window 1
			delay 1
		end repeat
		
		-- It takes time for panel loading
		delay 1
		
		-- Set the path to your profile file	
		set value of text field 1 of sheet 1 of sheet 1 of window 1 to my_profile_path
		
		-- let panel select the file
		delay 1
		keystroke return
		
		-- Final confirmation in the main dialog
		delay 1
		keystroke return
		
		delay 2
		
	end tell
end tell


-- click continue icon
tell application "System Events"
	if exists application process "System Settings" then
		tell application "System Events"
			tell application process "System Settings"
				
				repeat until exists sheet 1 of window 1
					delay 1
				end repeat
				
				tell sheet 1 of window 1
					tell group 1
						click button 2
						delay 2
					end tell
				end tell
				
			end tell
		end tell
	end if
end tell

-- click install button
tell application "System Events"
	if exists application process "System Settings" then
		tell application "System Events"
			tell application process "System Settings"
				
				repeat until exists sheet 1 of window 1
					delay 1
				end repeat
				
				tell sheet 1 of window 1
					click button 1
					delay 2
				end tell
				
			end tell
		end tell
	end if
end tell

-- answer password to SecurityAgent pop-up window

ProfileCommonUtil's answer_password_to_SecurityAgent()

-- close system setting window
ProfileCommonUtil's close_system_setting_window()
