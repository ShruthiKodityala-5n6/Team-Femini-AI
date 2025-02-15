import streamlit as st
import smtplib
import os
import requests
from email.message import EmailMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Hugging Face API
HUGGINGFACE_API_KEY = os.getenv("HF_API_KEY")
HUGGINGFACE_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"

# Email credentials
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Function to generate email content
def generate_email_content(prompt, tone, recipient_name):
    url = f"https://api-inference.huggingface.co/models/{HUGGINGFACE_MODEL}"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    payload = {"inputs": f"Write a {tone} email addressed to {recipient_name}. Content: {prompt}"}

    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        return result[0].get("generated_text", "Error: No text generated.")
    
    return f"Error: Unable to generate email content. Status Code: {response.status_code}"

# Function to send emails
def send_email(sender_email, receiver_emails, names, subject, email_body):
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            
            for receiver_email, name in zip(receiver_emails, names):
                msg = EmailMessage()
                msg["From"] = sender_email
                msg["To"] = receiver_email
                msg["Subject"] = subject
                personalized_body = f"Hello {name},\n\n{email_body}"  # Ensure body is personalized
                msg.set_content(personalized_body)
                server.send_message(msg)
        
        return "✅ Emails sent successfully!"
    
    except smtplib.SMTPAuthenticationError:
        return "❌ Error: Authentication failed. Ensure you are using an App Password."
    except Exception as e:
        return f"❌ Error sending email: {str(e)}"

# Function to test email login
def test_email_login():
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        return "✅ Gmail login successful!"
    except smtplib.SMTPAuthenticationError:
        return "❌ Error: Authentication failed. Use an App Password."
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Streamlit UI
st.title("📧 AI Email Generator & Sender")

prompt = st.text_area("Enter your email prompt")
tone = st.radio("Select Email Tone", ["Formal", "Informal"], index=0)
sender_email = st.text_input("Sender's Email", EMAIL_ADDRESS)  # Auto-fill sender email
receiver_emails = st.text_input("Receiver's Email(s) (comma-separated)")
names = st.text_input("Receiver's Name(s) (comma-separated)")
subject = st.text_input("Email Subject")

# Initialize session state for email body if it does not exist
if "edited_email" not in st.session_state:
    st.session_state["edited_email"] = ""

# Email generation
if st.button("Generate Email"):
    receiver_list = [email.strip() for email in receiver_emails.split(",") if email.strip()]
    name_list = [name.strip() for name in names.split(",") if name.strip()]

    if not receiver_list or not name_list:
        st.error("❌ Please provide recipient emails and their names.")
    elif len(receiver_list) != len(name_list):
        st.error(f"❌ The number of names ({len(name_list)}) must match the number of emails ({len(receiver_list)}).")
    else:
        generated_email_body = generate_email_content(prompt, tone, name_list[0])
        st.session_state["edited_email"] = generated_email_body  # Store the generated email
        st.subheader("✉️ Generated Email Preview:")
        
# Editable email body
edited_email_body = st.text_area("Edit the email before sending:", st.session_state["edited_email"], height=200, key="email_body")

# Save the updated content when edited
st.session_state["edited_email"] = edited_email_body

# Email sending
if st.button("Send Email"):
    receiver_list = [email.strip() for email in receiver_emails.split(",") if email.strip()]
    name_list = [name.strip() for name in names.split(",") if name.strip()]

    if not receiver_list or not name_list:
        st.error("❌ Please provide at least one recipient email and name.")
    elif len(receiver_list) != len(name_list):
        st.error(f"❌ The number of names ({len(name_list)}) must match the number of emails ({len(receiver_list)}).")
    else:
        final_email_body = st.session_state["edited_email"]
        if not final_email_body.strip():
            st.error("❌ Email content is empty. Please generate or edit the email before sending.")
        else:
            send_status = send_email(sender_email, receiver_list, name_list, subject, final_email_body)
            if "✅" in send_status:
                st.success(send_status)
            else:
                st.error(send_status)

# Debugging email login
if st.button("Test Email Login"):
    test_result = test_email_login()
    st.info(test_result)
