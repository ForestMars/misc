# Function to query the GitHub agent and extract ONLY the plain text output
agent-gh() {
  if [[ -z "$1" ]]; then
    echo "Usage: agent-gh <repo-name>"
    echo "Example: agent-gh vercel/next.js"
    return 1
  fi
  
  # Assumes the generated stats text is in the top-level key named 'text'.
  # The -r flag (raw output) removes quotes.
  curl -s -X POST http://localhost:4111/api/agents/githubAgent/generate \
    -H "Content-Type: application/json" \
    -d "{\"messages\":[\"Show me stats for $1\"]}" \
    | jq -r .text
}
