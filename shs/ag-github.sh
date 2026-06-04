# Function to query the GitHub agent
agent-gh() {
  if [[ -z "$1" ]]; then
    echo "Usage: agent-gh <repo-name>"
    echo "Example: agent-gh vercel/next.js"
    return 1
  fi
  
  local response=$(curl -s -N -X POST http://localhost:4111/api/agents/githubAgent/generate \
    -H "Content-Type: application/json" \
    -d "{\"messages\":[\"Show me stats for $1\"]}")
  
  # Try to extract text using jq with raw input to handle control characters
  local text=$(echo "$response" | jq -R -s 'try fromjson | .text // empty' 2>/dev/null)
  
  if [[ -n "$text" && "$text" != "null" ]]; then
    echo "$text"
  else
    # Fallback: use grep and basic parsing if jq fails
    echo "$response" | grep -o '"text":"[^"]*"' | head -1 | sed 's/"text":"\(.*\)"/\1/' | sed 's/\\n/\n/g'
    
    # If still nothing, show error
    if [[ $? -ne 0 ]]; then
      echo "Error: Could not extract text from response"
      return 1
    fi
  fi
}
