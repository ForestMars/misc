   import openai
    import os

    openai.api_key = os.environ.get('OPENAI_API_KEY')

    def completion(messages):
        response = openai.ChatCompletion.create(
            model = gpt_model, temperature = 0, messages = messages )
        return response['choices'][0]['message']['content'].strip()

    response = completion([
              {"role": "system", "content": "You are a helpful assistant."},
              {"role": "user", "content": "Who won the world series in 2020?"} ])

    #####

    import json
    import tiktoken
    import os

    tokenizer = tiktoken.get_encoding("cl100k_base")
     
    class Message:
        def __init__(self, role, text, length=None):
            self.role = role
            self.text = text
            if length != None:
                self.length = length
            else:
                self.length = self._count_tokens(text)
            print("New message, token length is",self.length)

        def _count_tokens(self, text):
            tokens = tokenizer.encode(text)
            return len(tokens)

    class History:
        def __init__(self, ID=None):
            self.messages = []
            self.ID = ID

            if self.ID:
                self._load_from_json()

        def add(self, role, text):
            message = Message(role, text)
            self.messages.append(message)
            self._save_to_json()

        def _save_to_json(self):
            if not self.ID:
                return

            data = {
                "messages": [{"role": m.role, "text": m.text, "length": m.length} for m in self.messages]
            }
            self.create_dir_if_not_exists('conversations')
     
            with open(f"conversations/{self.ID}.json", "w") as f:
                json.dump(data, f)

        def create_dir_if_not_exists(self, directory_path):
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)

        def _load_from_json(self):
            try:
                self.create_dir_if_not_exists('conversations')
                with open(f"conversations/{self.ID}.json", "r") as f:
                    data = json.load(f)
                    self.messages = [Message(m["role"], m["text"]) for m in data["messages"]]
            except FileNotFoundError:
                pass

        def recent_messages(self, max_tokens):
            recent_messages_reversed = []
            total_tokens = 0

            for m in reversed(self.messages):
                if total_tokens + m.length <= max_tokens:
                    recent_messages_reversed.append({
                        "role": m.role,
                        "content": m.text
                    })
                    total_tokens += m.length
                else:
                    break

            recent_messages = recent_messages_reversed[::-1]

            return recent_messages