# but i also feel like what’s coming is you just ask the AI to validate the email for you
import sys
import smtplib
import dns.resolver

def verify_existence(email):
    address_to_verify = email
    domain = address_to_verify.split('@')[1]

    try:
        # 1. Get the MX record for the domain
        records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(records[0].exchange)

        # 2. Start an SMTP connection
        server = smtplib.SMTP(timeout=10)
        server.set_debuglevel(0)
        server.connect(mx_record)
        server.helo(server.local_hostname)
        server.mail('me@example.com')

        # 3. Ask the server if the recipient exists
        code, message = server.rcpt(address_to_verify)
        server.quit()

        if code == 250:
            return "LIKELY REAL (Server accepted it)"
        else:
            return f"❌ ⚠️ INVALID (Server rejected it: {code})"

    except Exception as e:
        return f"❓ UNKNOWN (Server blocked the check): {e}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(verify_existence(sys.argv[1]))
