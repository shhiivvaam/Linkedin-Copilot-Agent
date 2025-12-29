# LinkedIn Job Outreach & Application Copilot

A human-in-the-loop automation assistant for LinkedIn job hunting that helps reduce manual effort while prioritizing account safety and human-like behavior.

## 🎯 Goal

Reduce manual job-hunting effort by:
- Finding relevant technical recruiters / Talent Acquisition specialists
- Discovering relevant LinkedIn jobs
- Drafting personalized outreach messages
- Assisting with LinkedIn Easy Apply applications

## ⚠️ Core Rules (Mandatory)

- **No mass automation or spam**
- **No full unsupervised autonomy**
- **Human approval before sending messages or submitting applications**
- **Low daily volume (10–20 actions/day)**
- **Real browser automation only (headed, human-like)**
- **Stop on CAPTCHA, OTP, or unexpected UI**

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Main Orchestrator                        │
│              (Coordinates all components)                    │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌───────▼────────┐  ┌───────▼────────┐
│   Browser      │  │   Recruiter    │  │   Job          │
│   Automation   │  │   Discovery    │  │   Discovery    │
└───────┬────────┘  └───────┬────────┘  └───────┬────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌───────▼────────┐  ┌───────▼────────┐
│   Messaging    │  │   Resume       │  │   Safety &     │
│   System       │  │   Intelligence │  │   Logging      │
└────────────────┘  └────────────────┘  └────────────────┘
```

## 📦 Components

### 1. Browser Automation (`browser_automation/`)
- Real Chromium automation with Playwright
- Persistent session management
- Human-like interactions (scrolling, typing, delays)
- CAPTCHA/OTP detection and pause

### 2. Recruiter Discovery (`recruiter_discovery/`)
- LinkedIn search for Technical Recruiters/TAs
- Profile filtering and ranking
- Activity and relevance analysis

### 3. Messaging System (`messaging/`)
- Profile reading and analysis
- Personalized message generation
- Human approval workflow

### 4. Job Discovery (`job_discovery/`)
- LinkedIn job search
- Easy Apply detection
- Job description analysis
- Application form pre-filling

### 5. Resume Intelligence (`resume/`)
- Resume parsing and mapping
- Job requirement matching
- Auto-answer generation for application questions

### 6. Safety & Logging (`safety/`)
- Action throttling
- Duplicate detection
- Comprehensive logging
- Daily summary reports

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Chrome/Chromium browser
- LinkedIn account

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

1. Copy `config.example.yaml` to `config.yaml`
2. Fill in your LinkedIn credentials and preferences
3. Add your resume file path

### Usage

```bash
# Run the copilot
python main.py

# Or use specific modules
python -m recruiter_discovery.search
python -m job_discovery.search
```

## 🔒 Safety Features

- **Rate Limiting**: Maximum 10-20 actions per day
- **Human Approval**: All messages and applications require approval
- **CAPTCHA Detection**: Automatically pauses on CAPTCHA
- **Duplicate Prevention**: Tracks contacted recruiters and applied jobs
- **Activity Logging**: Complete audit trail of all actions

## 📊 Daily Workflow

1. **Morning**: Review daily summary and pending approvals
2. **Discovery**: Find new recruiters and jobs
3. **Review**: Human reviews suggested messages/applications
4. **Approval**: Approve or modify before sending
5. **Execution**: Copilot executes approved actions
6. **Evening**: Review daily summary and plan next day

## ⚠️ Limitations

- **No CAPTCHA bypassing**: System stops and waits for human intervention
- **No OTP automation**: Requires manual verification
- **No mass scraping**: Respects LinkedIn's rate limits
- **Single account only**: Designed for personal use
- **Human approval required**: No fully autonomous operation

## 📝 License

MIT License - For personal use only

## 🤝 Contributing

This is a personal project. Use responsibly and in accordance with LinkedIn's Terms of Service.

