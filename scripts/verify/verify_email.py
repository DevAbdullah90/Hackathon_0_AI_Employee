#!/usr/bin/env python3
"""
Verify Gmail Integration
Tests IMAP connection and lists recent emails
"""
import os
import sys
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("Verifying Gmail Integration...")
    
    username = os.getenv("EMAIL_USERNAME")
    password = os.getenv("EMAIL_PASSWORD")
    imap_server = os.getenv("EMAIL_IMAP_SERVER", "imap.gmail.com")
    
    if not username or not password:
        print("Error: EMAIL_USERNAME or EMAIL_PASSWORD not set in .env")
        return

    print(f"Connecting to {imap_server} as {username}...")
    
    try:
        # Connect to IMAP server
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(username, password)
        print("Login successful!")
        
        # Select inbox
        mail.select("inbox")
        print("Inbox selected.")
        
        # Search for recent emails
        status, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()
        
        if not email_ids:
            print("No emails found in inbox.")
            return
            
        print(f"Found {len(email_ids)} emails. Fetching last 3...")
        
        # Get last 3 emails
        latest_email_ids = email_ids[-3:]
        
        for e_id in reversed(latest_email_ids):
            # Fetch the email body (RFC822) for the given ID
            status, msg_data = mail.fetch(e_id, "(RFC822)")
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Decode subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                        
                    # Decode sender
                    from_ = msg.get("From")
                    
                    print(f"\n[Email ID: {e_id.decode()}]")
                    print(f"From: {from_}")
                    print(f"Subject: {subject}")
                    
        mail.close()
        mail.logout()
        print("\nIMAP Verification complete!")

        # --- Test Sending (SMTP) ---
        print("\nTesting Email Sending (SMTP)...")
        import smtplib
        from email.mime.text import MIMEText

        smtp_server = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("EMAIL_SMTP_PORT", 587))
        
        msg = MIMEText("This is a test email from your AI Employee to verify sending capability.")
        msg['Subject'] = "AI Employee Email Verification"
        msg['From'] = username
        msg['To'] = username  # Send to self

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
            print("Test email sent successfully!")

    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()
