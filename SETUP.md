# Setup Guide

## Prerequisites

- Python 3.9 or higher
- Chrome or Chromium browser installed
- LinkedIn account
- (Optional) OpenAI API key for AI-powered message generation

## Installation

### 1. Clone or Download the Project

```bash
cd "Linkedin Copilot Agent"
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright Browsers

```bash
playwright install chromium
```

### 5. Configure the Copilot

1. Copy the example configuration:
```bash
copy config.example.yaml config.yaml
```

2. Edit `config.yaml` and fill in:
   - Your LinkedIn email and password (or use environment variables)
   - Your profile information (name, title, skills, location)
   - Your resume file path
   - Search preferences (keywords, locations)
   - Safety settings

3. (Optional) Set up AI for message generation:
   - Get an OpenAI API key from https://platform.openai.com/
   - Set it as environment variable: `export OPENAI_API_KEY=your_key`
   - Or add it to `config.yaml` (less secure)

### 6. Prepare Your Resume

1. Place your resume (PDF or DOCX) in the `resume/` directory
2. Update the `resume_path` in `config.yaml` to point to your resume

## First Run

### Basic Usage

```bash
python main.py
```

### Command Line Options

```bash
# Discover and contact recruiters only
python main.py --mode recruiters

# Discover and apply to jobs only
python main.py --mode jobs

# Both recruiters and jobs (default)
python main.py --mode both

# Use custom config file
python main.py --config my_config.yaml
```

## Daily Workflow

### Morning Routine

1. **Start the Copilot**
   ```bash
   python main.py
   ```

2. **Review Daily Summary**
   - Check yesterday's activity
   - Review pending approvals

3. **Discover New Opportunities**
   - Let copilot find recruiters and jobs
   - Review suggested matches

4. **Approve Actions**
   - Review drafted messages
   - Approve or modify before sending
   - Review job applications before submission

### During the Day

- The copilot will pause for your approval before:
  - Sending any message
  - Submitting any application
  - Encountering CAPTCHA or OTP

### Evening Routine

1. **Review Daily Summary**
   - Check actions taken
   - Review statistics
   - Plan for next day

2. **Check Logs**
   - Review `logs/copilot_YYYY-MM-DD.log`
   - Check for any errors

## Troubleshooting

### Login Issues

**Problem**: Cannot log in to LinkedIn

**Solutions**:
- Check credentials in `config.yaml`
- Try logging in manually first to clear any security checks
- Check for CAPTCHA - system will pause if detected
- Verify LinkedIn account is not locked

### CAPTCHA Detection

**Problem**: System stops with CAPTCHA warning

**Solution**:
- Manually solve CAPTCHA in the browser
- System will continue after CAPTCHA is resolved
- This is by design for safety

### Rate Limiting

**Problem**: "Rate limit reached" messages

**Solution**:
- This is normal - system enforces daily limits
- Wait until next day or adjust limits in config (not recommended)
- Check `config.yaml` for `max_actions_per_day` setting

### Browser Issues

**Problem**: Browser doesn't start or crashes

**Solutions**:
- Ensure Chromium is installed: `playwright install chromium`
- Check browser settings in `config.yaml`
- Try running with `headless: false` (default)

### Message Generation Issues

**Problem**: Messages are generic or not generating

**Solutions**:
- If using AI: Check API key is set correctly
- If using templates: Review `messaging` config section
- Check logs for specific error messages

### Application Form Issues

**Problem**: Forms not filling correctly

**Solutions**:
- LinkedIn forms vary - some may require manual completion
- Check `resume_data` is parsed correctly
- Review logs for specific field errors
- System will pause for manual review if needed

## Configuration Tips

### Optimize Recruiter Discovery

```yaml
recruiter_discovery:
  search_keywords:
    - "Technical Recruiter"
    - "Engineering Recruiter"
    - "Talent Acquisition Specialist"
  locations:
    - "United States"
    - "Remote"
  min_activity_days: 7
  max_results_per_search: 50
```

### Optimize Job Search

```yaml
job_discovery:
  keywords:
    - "Software Engineer"
    - "Full Stack Developer"
  locations:
    - "San Francisco, CA"
    - "Remote"
  easy_apply_only: true
  max_results_per_search: 100
```

### Adjust Safety Settings

```yaml
safety:
  max_actions_per_day: 15  # Lower for more conservative
  min_delay_between_actions: 600  # 10 minutes
  max_delay_between_actions: 1200  # 20 minutes
  human_approval_required: true  # Always recommended
```

## Best Practices

1. **Start Small**: Begin with 5-10 actions per day
2. **Review Messages**: Always review before sending
3. **Personalize**: Use AI generation for better personalization
4. **Monitor Logs**: Check logs regularly for issues
5. **Respect Limits**: Don't override safety limits
6. **Update Resume**: Keep resume file updated
7. **Stay Active**: Use LinkedIn manually as well

## Security Notes

- **Never commit** `config.yaml` with real credentials
- **Use environment variables** for sensitive data
- **Keep resume files** private
- **Review logs** for any sensitive data exposure
- **Use strong passwords** for LinkedIn account

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review error messages in console
3. Check configuration file
4. Review ARCHITECTURE.md for system details

## License

MIT License - For personal use only. Use responsibly and in accordance with LinkedIn's Terms of Service.

