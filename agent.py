# %%
import subprocess
subprocess.run(['pip', 'install', 'google-api-python-client'])
subprocess.run(['pip', 'install', 'google-auth-oauthlib'])
subprocess.run(['pip', 'install', 'google-auth-httplib2'])
subprocess.run(['pip', 'install', 'pdfplumber'])
subprocess.run(['pip', 'install', 'openai'])

# %%
import os
import os.path
import base64
import re
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pdfplumber
import openai
from google.auth.transport.requests import Request


# %%
# SCOPES: Full access to Gmail read-only
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/gmail.send']
API_KEY = os.getenv("OPENAI_API_KEY")
ROOT_DIR = Path(__file__).parent
TOKEN_PATH = ROOT_DIR / 'token.json'
CREDENTIALS_PATH = ROOT_DIR / 'credentials.json'

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def get_unique_application_emails(service):
    # Step 1: Search messages from last 7 days with 'application' in subject
    response = service.users().messages().list(
        userId='me',
        q='in:sent subject:applied newer_than:12d'
    ).execute()

    messages = response.get('messages', [])
    if not messages:
        return []

    thread_count = {}
    message_details = {}

    # Step 2: Count messages per thread
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        thread_id = msg_data['threadId']
        message_id = msg_data['id']

        thread_count[thread_id] = thread_count.get(thread_id, 0) + 1
        if thread_id not in message_details:
            headers = msg_data['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            to = next((h['value'] for h in headers if h['name'] == 'To'), '')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            snippet = msg_data.get('snippet', '')

            message_details[thread_id] = {
                'to': to,
                'subject': subject,
                'date': date,
                'snippet': snippet,
                'message_id': message_id,
                'thread_id': thread_id
            }

    # Step 3: Only keep threads with exactly one message sent
    unique_emails = [
        message_details[tid]
        for tid, count in thread_count.items()
        if count == 1
    ]

    return unique_emails


if __name__ == '__main__':
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)
    emails = get_unique_application_emails(service)

    # for email in emails:
    #     print("\n--- Email ---")
    #     print(f"To: {email['to']}")
    #     print(f"Subject: {email['subject']}")
    #     print(f"Date: {email['date']}")
    #     print(f"Snippet: {email['snippet']}")

# %%
def extract_resume_text(file_path):
    text = ''
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + '\n'
    return text.strip()

# %%
resume_ds=extract_resume_text(ROOT_DIR / "resumes" / "Dhrubajyoti_ray_Data_Scientist.pdf")
resume_analyst=extract_resume_text(ROOT_DIR / "resumes" / "Dhrubajyoti_Ray_Data_Analyst.pdf")


# %%
client=openai.OpenAI(api_key = API_KEY)  # Use env var for security in real app

def generate_followup_gpt4o(resume_text, recruiter_name, company, job_title, applied_date, original_email_snippet=None):
    prompt = f"""
You are a job applicant who applied for a {job_title} role at {company} on {applied_date}.
You're writing a follow-up email to {recruiter_name}. Your resume is shown below. Use it to personalize the message.

Resume:
{resume_text}

Original email snippet (if any): {original_email_snippet or 'N/A'}

Now write a concise, polite, professional follow-up email asking for an update on the application.
Don't include the resume content directly — use it to highlight strengths. Keep it friendly and respectful. Also remember that I have graduated from CMU. Remove the Subject and start directly with Hello first_name of {recruiter_name}. My Linkedin profile is https://www.linkedin.com/in/dhrubajyoti-ray-38186646/ 
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content


# %%
def choose_resume(subject_line):
    if 'scientist' in subject_line.lower():
        return resume_ds
    elif 'analyst' in subject_line.lower():
        return resume_analyst
    else:
        return resume_ds 

# %%
followups = []

for email in emails:
    recruiter_email = email['to']
    subject = email['subject']
    applied_date = email['date']
    snippet = email['snippet']
    message_id = email['message_id']
    thread_id = email['thread_id']

    # Try to extract recruiter name and company from subject/snippet
    recruiter_name = recruiter_email.split('@')[0].replace('.', ' ').title()
    job_title = subject.replace('Application for', '').strip()
    company = "Unknown Company"  # You can improve this with regex on snippet

    # Choose appropriate resume
    resume = choose_resume(subject)

    # Generate email
    followup = generate_followup_gpt4o(
        resume_text=resume,
        recruiter_name=recruiter_name,
        company=company,
        job_title=job_title,
        applied_date=applied_date,
        original_email_snippet=snippet
    )

    followups.append({
        "to": recruiter_email,
        "followup_email": followup,
        "message_id": message_id,
        "thread_id": thread_id,
        "subject": subject,
        "applied_date": applied_date,
        "snippet": snippet
    })

# Print or save
for f in followups:
    print("\n--- Follow-up Email ---")
    print(f"To: {f['to']}")
    print(f"{f['followup_email']}")






# %%
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def create_reply_message(service, thread_id, to_email, subject, followup_text, message_id):
    """Constructs a proper reply email"""
    message = MIMEMultipart()
    message['to'] = to_email
    message['subject'] = f"Re: {subject}"
    message['In-Reply-To'] = message_id
    message['References'] = message_id

    message.attach(MIMEText(followup_text.replace('\n', '<br>'), 'html'))

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    return {
        'raw': raw_message,
        'threadId': thread_id
    }

def send_followup_email(service, thread_id, to_email, subject, followup_text, message_id):
    """Sends the reply email via Gmail API"""
    message_body = create_reply_message(
        service,
        thread_id,
        to_email,
        subject,
        followup_text,
        message_id
    )
    return service.users().messages().send(userId='me', body=message_body).execute()


# %%
for f in followups[1:]:
    result = send_followup_email(
        service,
        f['thread_id'],
        f['to'],
        f['subject'],
        f['followup_email'],
        f['message_id']
    )
    print(f"Sent follow-up to: {f['to']} | Gmail ID: {result['id']}")

# %%


# %%



