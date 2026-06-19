#!/usr/bin/env bash

AGENTS=(
  "com.coppertino.VOXAgent"
  "application.notion.id.137269227.137269233"
  "application.com.figma.agent.11780252.44399902"
  "us.zoom.updater"
  "com.microsoft.update.agent"
  "com.google.GoogleUpdater.wake"
  "homebrew.mxcl.rabbitmq"
  "homebrew.mxcl.postgresql@17"
)

for agent in "${AGENTS[@]}"; do
  echo "Removing $agent..."
  launchctl remove "$agent" 2>/dev/null || true
  echo "Disabling $agent..."
  launchctl disable "gui/501/$agent" 2>/dev/null || true
done

echo ""
echo "Done. Reboot to confirm nothing comes back."
