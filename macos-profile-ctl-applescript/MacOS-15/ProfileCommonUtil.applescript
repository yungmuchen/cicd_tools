-- common parameters

property MacMiniUsername : "tester"
property MacMiniPassword : "qwertyuiop"
property WiFiProfilePath : "/Users/tester/wifi-profile/testing.mobileconfig"


--
-- common function call

on close_system_setting_window()
        tell application "System Events"
                if exists application process "System Settings" then
                        do shell script "killall 'System Settings'"
                end if
        end tell
        delay 1
end close_system_setting_window

on answer_password_to_SecurityAgent()
        tell application "System Events"
                -- Check if the process exists
                if exists process "SecurityAgent" then
                        tell process "SecurityAgent"
                                -- Check if the dialog window is present
                                if exists window 1 then

                                        --                                      set my_MacMiniPassword to ProfileCommunUtil's MacMiniPassword
                                        set my_MacMiniPassword to MacMiniPassword

                                        -- Bring it to the front to ensure it receives keystrokes
                                        set frontmost to true

                                        -- Focus the first field (usually Account Name)
                                        set focused of text field 2 of window 1 to true
                                        delay 0.5 -- Short delay for UI responsiveness

                                        -- Type Password
                                        keystroke my_MacMiniPassword

                                        -- Submit the form
                                        keystroke return

                                        -- wait for the action
                                        delay 2
                                end if
                        end tell
                end if
        end tell
end answer_password_to_SecurityAgent


