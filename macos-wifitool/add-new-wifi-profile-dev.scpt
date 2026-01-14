-- env: mac-mini M4, macOS 15.5

tell application "System Events"
        tell application process "System Settings"
                -- activate
                -- set frontmost to true
                do shell script "open 'x-apple.systempreferences:com.apple.wifi-settings-extension'"
                delay 2

                -- click other network icon to add network profile
                tell window 1
                        tell splitter group 1 of group 1
                                tell scroll area 1 of group 1 of group 2
                                        click button 1
                                end tell
                        end tell
                end tell

                repeat until exists sheet 1 of window 1
                        delay 0.2
                end repeat

                tell sheet 1 of window 1
                        tell group 1
                                tell scroll area 1
                                        tell group 1

                                                -- switch security type to WPA2 Enterprise for 8021x PEAP
                                                click pop up button 1
                                                delay 1
                                                click menu item "WPA2 Enterprise" of menu 1 of pop up button 1

                                                delay 2

                                                -- enter ssid
                                                set focused of text field 1 to true
                                                set value of text field 1 to "MY_SSID"
                                                tell application "System Events" to keystroke space
                                                tell application "System Events" to keystroke (ASCII character 8)

                                                delay 1

                                                -- enter Username
                                                set focused of text field 2 to true
                                                tell application "System Events" to keystroke "MY_USERNAME"
                                                tell application "System Events" to keystroke tab

                                                -- enter Password
                                                set focused of text field 3 to true
                                                delay 0.2
                                                tell application "System Events" to keystroke "MY_PASSWORD"

                                                delay 0.5
                                                if (exists button "OK") then
                                                        click button "OK"
                                                else
                                                        -- force enter
                                                        tell application "System Events" to keystroke return
                                                end if
                                        end tell --end of group
                                end tell -- end of scroll
                                --click button "OK"
                        end tell -- end of group of sheet
                end tell -- end of sheet

        end tell
end tell



