# /// script
# dependencies = ["email-validator"]
# ///

import sys
import csv
from email_validator import validate_email, EmailNotValidError

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate.py <input_file.csv>")
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        with open(input_file, mode='r', encoding='utf-8') as f:
            # Using DictReader assumes your CSV has a header (e.g., 'email')
            # If it's just a raw list, use csv.reader(f) instead
            reader = csv.reader(f)
            
            print(f"{'EMAIL':<40} | {'STATUS':<10} | {'DETAILS'}")
            print("-" * 80)

            for row in reader:
                if not row: continue  # Skip empty lines
                
                email = row[0].strip()
                try:
                    # check_deliverability=True performs the DNS/MX lookup
                    info = validate_email(email, check_deliverability=True)
                    print(f"{info.normalized:<40} | ✅ VALID    | -")
                except EmailNotValidError as e:
                    print(f"{email:<40} | ❌ INVALID  | {str(e)}")

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
