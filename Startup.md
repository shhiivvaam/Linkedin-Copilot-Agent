# LinkedIn Job Outreach & Application Copilot

A safe, human-in-the-loop automation system to reduce manual LinkedIn job-hunting work — including recruiter outreach, job discovery, and Easy Apply assistance — while prioritizing security and compliance.

---

## 🚀 Features

- **Find** relevant technical recruiters & jobs
- **Draft** personalized outreach messages
- **Assist** with Easy Apply job applications
- **Human-in-the-loop:** All actions require your approval
- **Real browser automation:** Headed Playwright with human-like scrolling, typing, and delays
- **Safety-focused:** No spam, no mass automation, no bypassing CAPTCHAs, always low daily volume

---

## 🛠️ Getting Started

### 1. Install Requirements

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure

- Copy the example config and customize:

```bash
copy config.example.yaml config.yaml
# Or: cp config.example.yaml config.yaml (Mac/Linux)
```

- Fill in `config.yaml` with your:
  - LinkedIn email & password (or set as environment variables LINKEDIN_EMAIL, LINKEDIN_PASSWORD)
  - Profile info (name, title, location, skills, years of experience)
  - Resume file path (recommended: put your resume in the `resume/` folder)

### 3. Add Your Resume

- Place your PDF/DOCX resume in the `resume/` directory.
- Update `profile.resume_path` in `config.yaml` accordingly.

---

## ▶️ Running the Copilot

**Basic run:**

```bash
python main.py
```

**Modes:**

- **Recruiters only:**  
  `python main.py --mode recruiters`

- **Jobs only:**  
  `python main.py --mode jobs`

- **Both (default):**  
  `python main.py`

**Config file:**  
You can use `--config config.yaml` to specify a different config.

---

## 💡 How It Works

1. **Log in** to LinkedIn (or prompt you if CAPTCHA or verification is needed)
2. **Discover recruiters** (search, filter, rank) and draft messages for each
3. **Discover jobs** and analyze if they match your profile before suggesting application
4. **Always asks for your approval before sending messages or submitting applications**
5. **All actions** are logged, summaries generated daily for your review

---

## 🦺 Safety Features

- Random delays and human-like interaction
- Stops on CAPTCHA or OTP screens (requires your manual intervention)
- All messages and applications require your explicit approval
- Strict daily activity and duplicate checking

---

## 📂 Logs & Reporting

- Logs are saved under `logs/` (including daily summaries)
- Contacted recruiters and jobs are tracked to avoid duplicates

---

## 🛑 Limitations & Warnings

- **Do NOT use this for mass automation or spamming**
- **Do NOT use it for multiple accounts or businesses**
- This system complies with LinkedIn's Terms of Service (no CAPTCHA bypass or spam)
- All applications and messages are human-reviewed

---

## 🧰 Support

**Common Issues:**
- Problems logging in? Check credentials and manually solve any CAPTCHA the first time
- Browser won’t start? Make sure to run `playwright install chromium`
- Resume not found? Make sure the path matches in `config.yaml`

**See also:**
- [ARCHITECTURE.md](ARCHITECTURE.md): Full architecture/flow
- [SETUP.md](SETUP.md): Detailed setup/troubleshooting
- [LIMITATIONS.md](LIMITATIONS.md): Known limitations

---

## 📝 License

MIT — for individual, personal, responsible use only. Respect LinkedIn’s Terms of Service!

---

**Start responsibly, review everything before sending, and happy job hunting!**