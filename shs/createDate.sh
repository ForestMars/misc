#!/bin/bash
# createDate.sh - Single file for global Mac date/time hotkey

# Clean up any previous attempts
rm -rf ~/Library/Services/DateTime*

# Create minimal working Automator Quick Action via CLI
mkdir -p ~/Library/Services/DateTimeInsert.workflow/Contents/Info.plist

# Write the complete working workflow as BINARY plist (what Automator expects)
cat > ~/Library/Services/DateTimeInsert.workflow/Contents/Info.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>AMWorkflowMode</key>
	<integer>1</integer>
	<key>AMWorkflowVersion</key>
	<string>1.4</string>
	<key>CFBundleDisplayName</key>
	<string>DateTime Insert</string>
</dict>
</plist>
EOF

# Create the actual workflow actions file
cat > ~/Library/Services/DateTimeInsert.workflow/Contents/document.wflow << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>WFWorkflowActions</key>
	<array>
		<dict>
			<key>WFWorkflowActionIdentifier</key>
			<string>is.workflow.actions.runapplescript.1</string>
			<key>WFWorkflowActionParameters</key>
			<dict>
				<key>WFAppleScriptSource</key>
				<string>on run argv
set theDate to do shell script "date +%Y-%m-%d %H:%M"
tell application "System Events"
keystroke theDate
end tell
end run</string>
			</dict>
		</dict>
	</array>
	<key>WorkflowInputDataType</key>
	<string>public.data</string>
	<key>WorkflowTypes</key>
	<array/>
</dict>
</plist>
EOF

# Register service
/System/Library/Frameworks/CoreServices.framework/Versions/A/Frameworks/LaunchServices.framework/Versions/A/Support/lsregister -f ~/Library/Services/DateTimeInsert.workflow

echo "✅ Setup complete. Go to System Settings > Keyboard > Shortcuts > Services > General > 'DateTime Insert' and assign ⌃⌥⌘D"
echo "Now press that hotkey in ANY text field to insert date/time"

