global ProfileCommonUtil

on run
	
	-- Load the external script file for common parameters
	set ProfileCommonUtil to load script file ((path to home folder as text) & "wifi-profile:ProfileCommonUtil.scpt")
	
	ProfileCommonUtil's close_system_setting_window()
	
	tell application "System Events"
		tell process "System Settings"
			activate
			delay 1
			
			-- Navigate directly to Device Management
			do shell script "open x-apple.systempreferences:com.apple.Profiles-Settings.extension"
			delay 2
			
			tell window 1
				-- Profiles are usually in a list or table
				set profileList to outline 1 of scroll area 1 of group 2 of scroll area 1 of group 1 of group 3 of splitter group 1 of group 1
				set rowCount_a to count rows of profileList
				set rowCount to rowCount_a - 1
				
				-- Loop backwards to avoid index shifting during deletion
				repeat with i from rowCount to 1 by -1
					select row i of profileList
					
					-- Click the Remove (-) button
					click button 2 of group 2 of scroll area 1 of group 1 of group 3 of splitter group 1 of group 1
					
					-- Handle the confirmation sheet
					repeat until exists sheet 1
						delay 1
					end repeat
					delay 1
					click button "Remove" of sheet 1
					delay 1
					
					-- input password for remove
					ProfileCommonUtil's answer_password_to_SecurityAgent()
					
				end repeat
				
			end tell
		end tell
	end tell
	
	ProfileCommonUtil's close_system_setting_window()
	
end run
