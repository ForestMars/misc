import random
import sys

def randomize_words_from_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            original_text = file.read()

        words = original_text.split()
        random.shuffle(words)
        randomized_text = ' '.join(words)
        print(randomized_text)

    except FileNotFoundError:
        print(f"Error: File not found — {filepath}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python randomize_words.py <filepath>")
    else:
        filepath = sys.argv[1]
        randomize_words_from_file(filepath)

