# 🤖 AI Employee - Gold Tier Extended

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Playwright](https://img.shields.io/badge/Playwright-Automation-green?style=for-the-badge&logo=playwright)
![Status](https://img.shields.io/badge/Status-Operational-success?style=for-the-badge)

**An autonomous AI workforce system designed to manage social media, communications, and reporting with human-in-the-loop oversight.**

---

## 🚀 Overview

The **AI Employee** is a comprehensive automation suite that acts as a digital workforce. It autonomously monitors, generates, and publishes content across multiple platforms while ensuring human oversight through a file-based approval workflow.

Powered by **Python** and **Playwright**, it handles complex browser-based tasks (like LinkedIn and Instagram posting) and API integrations (Twitter/X, Email) in a unified system.

## ✨ Key Features

### 🌐 Multi-Platform Support
-   **LinkedIn**: Auto-posting (Text/Image/Article), Analytics monitoring.
-   **Instagram**: Post Images, Stories, and Send DMs.
-   **WhatsApp**: Send daily updates and messages via Web automation.
-   **Twitter/X**: Post tweets via API.
-   **Email**: Send reports and notifications via SMTP.
-   **Facebook**: Post content to profiles/pages.

### 🧠 Intelligent Workflow
-   **Content Generation**: AI-driven content creation using Gemini/Groq.
-   **Human-in-the-Loop**: Content is generated into `Pending_Approval`. simply move files to `Approved` to trigger publishing.
-   **Smart Scheduler**: Optimizes posting times for maximum engagement.
-   **Auto-Processor**: 24/7 monitoring of the `Approved` folder.

### 📊 Monitoring & Reporting
-   **Dashboard**: Real-time status updates in `Dashboard.md`.
-   **Health Checks**: Automated system diagnostics.
-   **Comprehensive Logging**: Detailed activity logs in `Logs/`.

---

## 🛠️ Installation & Setup

### Prerequisites
-   Python 3.10 or higher
-   Chrome/Chromium Browser (for Playwright)

### 1. Clone & Install Dependencies
```bash
# Install core dependencies
pip install playwright python-dotenv watchdog schedule tweepy pyyaml rich colorama

# Install Playwright browsers
playwright install chromium
```

### 2. Configuration
Create a `.env` file in the root directory with your credentials:

```ini
# --- Social Media Credentials ---
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
TWITTER_API_KEY=your_key
...

# --- AI Configuration ---
GEMINI_API_KEY=your_gemini_key

# --- System Paths ---
VAULT_PATH=.
```

*(See `.env.example` if available for a full list of options)*

---

## 🚀 Usage

### Start the System
Double-click **`start_ai_employee.bat`** or run:

```bash
python src/core/workflow_orchestrator.py
```

The system will:
1.  Start the **Workflow Orchestrator**.
2.  Launch background threads for **Auto Processor**, **Schedulers**, and **Watchers**.
3.  Begin monitoring for tasks.

### 📝 Publishing Content
The system uses a simple file-based workflow:

1.  **Draft**: AI generates content drafts in `Pending_Approval/`.
2.  **Review**: You review and edit the `.md` files.
3.  **Approve**: Move the file to the `Approved/` folder.
4.  **Publish**: The **Auto Processor** picks it up immediately, posts it, and moves the file to `Done/` (or `Failed/` if an error occurs).

### Supported File Types
Add this metadata to the top of your Markdown files:

```yaml
---
type: linkedin_post  # or instagram_post, twitter_post, whatsapp, email
image_path: "path/to/image.jpg"
---
```

---

## 📂 Project Structure

-   **`Approved/`**: Drop files here to trigger immediate processing.
-   **`Pending_Approval/`**: AI-generated drafts waiting for review.
-   **`Done/`**: Successfully processed files.
-   **`Failed/`**: Files that encountered errors.
-   **`Logs/`**: System logs and error reports.
-   **`src/`**: Source code.
    -   **`core/`**: Orchestrator and Processor logic.
    -   **`platforms/`**: Platform-specific modules (LinkedIn, WA, etc.).
    -   **`generators/`**: AI content generation logic.
    -   **`schedulers/`**: Timing and task management.

---

## 🛡️ Security

-   **`.gitignore`**: Configured to exclude `.env`, session data, and cookies.
-   **Local Execution**: All browser automation runs locally on your machine.
-   **Session Management**: Cookies are saved locally to maintain login sessions without re-authenticating.

---

## 📜 License

Private / Custom License.
