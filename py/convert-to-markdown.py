import json
import os
import sys
from datetime import datetime

# Define module-level variables at the top
INPUT_FILE = "path/to/conversations.json"  # Replace with your conversations.json path
OUTPUT_DIR = "chatgpt_history"
MAX_CONVS_PER_FILE = 100  # Split output files after this many conversations
SUMMARY_FILE = os.path.join(OUTPUT_DIR, "chat_summary.txt")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

def stream_conversations(json_file):
    """Stream conversations from JSON file to handle large files."""
    try:
        if not os.path.exists(json_file):
            print(f"Error: {json_file} not found. Check the path.")
            sys.exit(1)
        
        with open(json_file, 'r', encoding='utf-8') as f:
            conversations = json.load(f)  # Load JSON; for huge files, ijson can be used
            for conv in conversations:
                yield conv
    except Exception as e:
        print(f"Error reading JSON: {e}")
        sys.exit(1)

def format_message(msg):
    """Format a single message as Markdown."""
    role = msg.get("role", "Unknown").capitalize()
    content = msg.get("content", "").replace("\n", "\n> ")  # Quote content for readability
    timestamp = msg.get("timestamp", "Unknown")
    return f"**{role}** ({timestamp}):\n> {content}\n"

def save_markdown_chunk(chunk, output_file, conv_count):
    """Save a chunk of conversations as a Markdown file."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# ChatGPT History (Part {conv_count // MAX_CONVS_PER_FILE + 1})\n")
        f.write(f"Exported on: {datetime.now().isoformat()}\n\n")
        for conv in chunk:
            f.write(conv["markdown"])
    print(f"Saved Markdown to {output_file}")

def parse_conversations_to_markdown(json_file):
    """Convert conversations.json to readable Markdown files."""
    # Define function-level variables
    total_convs = 0
    total_messages = 0
    chunk = []
    chunk_conv_count = 0
    summary = []

    # Initialize summary file
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(SUMMARY_FILE, 'w', encoding='utf-8') as sf:
        sf.write("ChatGPT History Summary\n")
        sf.write(f"Export Processed: {datetime.now().isoformat()}\n\n")

    # Process conversations
    for conv_index, conv in enumerate(stream_conversations(json_file)):
        conv_id = conv.get("id", "Unknown")
        title = conv.get("title", "No Title")
        messages = []
        markdown_content = []

        # Start conversation section
        markdown_content.append(f"## Conversation: {title} (ID: {conv_id})\n")
        markdown_content.append(f"Exported: {datetime.now().isoformat()}\n\n")

        # Extract messages
        for msg in conv.get("mapping", {}).values():
            if "message" in msg and "content" in msg["message"]:
                role = msg["message"]["author"]["role"]
                content = msg["message"]["content"].get("parts", [])
                if content and isinstance(content, list) and len(content) > 0:
                    messages.append({
                        "role": role,
                        "content": content[0],
                        "timestamp": msg["message"].get("create_time", "Unknown")
                    })

        # Format messages as Markdown
        for msg in messages:
            markdown_content.append(format_message(msg))

        # Add separator
        markdown_content.append("\n---\n")

        # Update counts
        total_convs += 1
        total_messages += len(messages)
        chunk_conv_count += 1

        # Add to chunk
        chunk.append({"markdown": "".join(markdown_content)})

        # Write summary
        with open(SUMMARY_FILE, 'a', encoding='utf-8') as sf:
            sf.write(f"Conversation {total_convs}: ID={conv_id}, Title={title}, Messages={len(messages)}\n")

        # Save chunk if it’s big enough
        if chunk_conv_count >= MAX_CONVS_PER_FILE:
            output_file = os.path.join(OUTPUT_DIR, f"conversations_part_{total_convs // MAX_CONVS_PER_FILE + 1}_{TIMESTAMP}.md")
            save_markdown_chunk(chunk, output_file, total_convs)
            chunk = []
            chunk_conv_count = 0

    # Save any remaining chunk
    if chunk:
        output_file = os.path.join(OUTPUT_DIR, f"conversations_part_{(total_convs // MAX_CONVS_PER_FILE) + 1}_{TIMESTAMP}.md")
        save_markdown_chunk(chunk, output_file, total_convs)

    # Finalize summary
    with open(SUMMARY_FILE, 'a', encoding='utf-8') as sf:
        sf.write(f"\nTotal Conversations: {total_convs}\n")
        sf.write(f"Total Messages: {total_messages}\n")
    print(f"Processing complete. Summary saved to {SUMMARY_FILE}")
    print(f"Markdown files saved in {OUTPUT_DIR}")
    print(f"Total conversations: {total_convs}, Total messages: {total_messages}")

def main():
    # Define main variables
    json_file = INPUT_FILE
    parse_conversations_to_markdown(json_file)

if __name__ == "__main__":
    main()