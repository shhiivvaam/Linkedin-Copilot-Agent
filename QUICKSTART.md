# Quick Start Guide

Get up and running with the LinkedIn Copilot in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

## Step 2: Configure

1. Copy the example config:
```bash
copy config.example.yaml config.yaml
```

2. Edit `config.yaml`:
   - Add your LinkedIn email and password
   - Add your profile info (name, title, skills)
   - Set your resume path

## Step 3: Add Your Resume

Place your resume (PDF or DOCX) in the `resume/` folder and update the path in config.

## Step 4: Run

```bash
python main.py
```

## First Run Checklist

- [ ] Dependencies installed
- [ ] Config file created and filled
- [ ] Resume file added
- [ ] LinkedIn credentials set
- [ ] Browser opens successfully
- [ ] Login works (or session saved)

## Common First-Run Issues

**"Configuration file not found"**
- Make sure you copied `config.example.yaml` to `config.yaml`

**"Browser not found"**
- Run: `playwright install chromium`

**"Login failed"**
- Check credentials in config.yaml
- Try logging in manually first
- Check for CAPTCHA

**"Resume not found"**
- Check resume path in config.yaml
- Make sure file exists

## Next Steps

1. **Start Small**: Run with `--mode recruiters` first
2. **Review Messages**: Always review before sending
3. **Check Logs**: Review `logs/` directory
4. **Read Documentation**: See `SETUP.md` for detailed guide

## Example Workflow

```bash
# Discover recruiters only
python main.py --mode recruiters

# Discover jobs only  
python main.py --mode jobs

# Both (default)
python main.py
```

## Getting Help

- **Setup Issues**: See `SETUP.md`
- **Architecture**: See `ARCHITECTURE.md`
- **Limitations**: See `LIMITATIONS.md`
- **Logs**: Check `logs/` directory

## Safety Reminders

⚠️ **Always review messages before sending**
⚠️ **Always review applications before submitting**
⚠️ **Respect daily limits (10-20 actions/day)**
⚠️ **Stop if CAPTCHA appears**
⚠️ **Use responsibly and comply with LinkedIn ToS**

Happy job hunting! 🚀

