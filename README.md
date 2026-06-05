# AI-Powered Job Application Follow-Up Agent

## Overview

This project automates the process of generating and sending personalized follow-up emails for job applications.

The agent:

* Connects to Gmail using the Gmail API
* Identifies recently submitted job applications
* Extracts relevant application details
* Selects the most appropriate resume version
* Uses OpenAI models to generate personalized follow-up emails
* Sends follow-ups directly within the original email thread

The goal is to help job seekers maintain consistent recruiter engagement without manually drafting and sending dozens of follow-up emails.

---

## Features

### Gmail Integration

* Authenticate securely using OAuth 2.0
* Read sent application emails
* Retrieve thread information
* Send follow-up messages within existing email conversations

### Resume-Aware Personalization

Supports multiple resume versions:

* Data Scientist Resume
* Data Analyst Resume

The agent automatically selects the most relevant resume based on the job title.

### AI-Generated Follow-Ups

Uses OpenAI models to:

* Generate personalized recruiter outreach
* Reference relevant experience
* Maintain professional tone
* Adapt messaging to different roles

### Automated Thread Management

* Detects application emails from the Sent folder
* Identifies applications with no previous follow-up
* Sends replies directly inside the original Gmail thread

---

## Project Structure

```text
project-root/
│
├── credentials/
│   ├── credentials.json
│   └── token.json
│
├── resumes/
│   ├── Dhrubajyoti_ray_Data_Scientist.pdf
│   └── Dhrubajyoti_Ray_Data_Analyst.pdf
│
├── .env
├── .gitignore
└── README.md
```

---

## Installation

### Clone Repository

```bash
git clone <repository-url>
cd <repository-name>
```

### Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install google-api-python-client
pip install google-auth-oauthlib
pip install google-auth-httplib2
pip install pdfplumber
pip install openai
pip install python-dotenv
```

---

## OpenAI Configuration

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key
```

Load the key in Python:

```python
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
```

---

## Gmail API Setup

### Step 1: Create a Google Cloud Project

1. Go to Google Cloud Console
2. Create a new project
3. Enable Gmail API

### Step 2: Configure OAuth

1. Navigate to APIs & Services → Credentials
2. Create OAuth Client ID
3. Select Desktop Application
4. Download `credentials.json`

Place the file inside:

```text
credentials/credentials.json
```

### Step 3: First Authentication

Run the notebook/script.

The browser will open for Gmail authentication.

A token file will automatically be created:

```text
credentials/token.json
```

---

## Resume Configuration

Store resume files in:

```text
resumes/
```

Example:

```text
resumes/
├── Dhrubajyoti_ray_Data_Scientist.pdf
└── Dhrubajyoti_Ray_Data_Analyst.pdf
```

The agent extracts text from the PDF resumes and uses it for follow-up generation.

---

## Workflow

### 1. Retrieve Application Emails

The agent searches Gmail Sent Mail:

```text
subject:applied newer_than:12d
```

### 2. Identify Eligible Applications

Applications are selected when:

* They were recently sent
* Only one message exists in the thread

### 3. Select Resume

Rules:

```python
if "scientist" in subject:
    use DS resume
elif "analyst" in subject:
    use analyst resume
else:
    use DS resume
```

### 4. Generate Follow-Up

The OpenAI model receives:

* Resume content
* Recruiter information
* Job title
* Application date
* Original email snippet

and generates a personalized follow-up email.

### 5. Send Email

The follow-up is sent:

* To the recruiter
* Within the existing Gmail thread
* As a reply to the original application

---

## Security

Sensitive files are excluded from Git:

```gitignore
credentials/
.env
__pycache__/
.ipynb_checkpoints/
.DS_Store
```

Never commit:

* OpenAI API keys
* Gmail OAuth credentials
* Gmail tokens

---

## Example Use Case

1. Apply to 50+ jobs.
2. Wait 7–12 days.
3. Run the notebook.
4. Generate personalized follow-ups.
5. Review generated messages.
6. Send follow-ups automatically.

---

## Future Improvements

* SQLite application tracking database
* Recruiter/company extraction using LLMs
* Follow-up scheduling
* Multiple follow-up sequences
* LinkedIn outreach generation
* ATS status tracking
* Streamlit dashboard
* Email performance analytics
* RAG-based company personalization
* Batch approval workflow before sending

---

## Disclaimer

This project is intended for educational and personal productivity purposes. Users are responsible for complying with Gmail API policies, OpenAI usage policies, and applicable privacy regulations.

