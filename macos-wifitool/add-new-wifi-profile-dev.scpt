-- env: mac-mini M4, macOS 15.5

tell application "System Events"
        tell application process "System Settings"
                set frontmost to true
                do shell script "open 'x-apple.systempreferences:com.apple.wifi-settings-extension'"
                delay 1

                -- click other network icon to add network profile
                tell window 1
                        tell splitter group 1 of group 1
                                tell scroll area 1 of group 1 of group 2
                                        click button 1
                                end tell
                        end tell
                end tell

        end tell
end tell
