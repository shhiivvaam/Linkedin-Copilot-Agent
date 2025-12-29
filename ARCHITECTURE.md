# LinkedIn Copilot Architecture

## System Overview

The LinkedIn Job Outreach & Application Copilot is a human-in-the-loop automation system designed to assist job seekers with LinkedIn activities while prioritizing account safety and human-like behavior.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Main Orchestrator                        │
│                         (main.py)                                │
│  - Coordinates all components                                    │
│  - Manages workflow and state                                    │
│  - Handles user interactions                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌────────▼────────┐   ┌───────▼────────┐
│   Browser      │   │   Recruiter     │   │   Job          │
│   Automation   │   │   Discovery     │   │   Discovery    │
│                │   │                 │   │                │
│ - Browser      │   │ - Search        │   │ - Search       │
│   Manager      │   │ - Ranking       │   │ - Analysis     │
│ - Human-like   │   │ - Filtering     │   │ - Application  │
│   Behavior     │   │                 │   │                │
└───────┬────────┘   └────────┬────────┘   └───────┬────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌────────▼────────┐   ┌───────▼────────┐
│   Messaging    │   │   Resume         │   │   Safety &      │
│   System       │   │   Intelligence   │   │   Logging       │
│                │   │                 │   │                 │
│ - Generation   │   │ - Parsing       │   │ - Rate Limiting │
│ - Sending      │   │ - Matching      │   │ - Tracking      │
│ - Validation   │   │ - Answers       │   │ - Logging       │
└────────────────┘   └─────────────────┘   └─────────────────┘
```

## Component Breakdown

### 1. Browser Automation (`browser_automation/`)

**Purpose**: Handles all browser interactions with human-like behavior

**Components**:
- `BrowserManager`: Manages browser session, cookies, login
- `HumanLikeBehavior`: Simulates human interactions (typing, scrolling, delays)

**Key Features**:
- Real Chromium browser (headed mode)
- Persistent session with cookie management
- CAPTCHA/OTP detection and pause
- Human-like delays and interactions
- Webdriver detection evasion

**Safety**:
- Stops on CAPTCHA detection
- Stops on OTP requirements
- Human approval for critical actions

### 2. Recruiter Discovery (`recruiter_discovery/`)

**Purpose**: Find and rank relevant Technical Recruiters

**Components**:
- `RecruiterSearch`: Searches LinkedIn for recruiters
- `RecruiterRanker`: Ranks recruiters by relevance

**Workflow**:
1. Search LinkedIn People with keywords (e.g., "Technical Recruiter")
2. Extract recruiter profiles from search results
3. Rank by:
   - Recent activity
   - Company relevance
   - Profile completeness
   - Title relevance
4. Filter out already contacted recruiters

**Output**: Ranked list of recruiter profiles with relevance scores

### 3. Messaging System (`messaging/`)

**Purpose**: Generate and send personalized messages

**Components**:
- `MessageGenerator`: Creates personalized messages (AI or template-based)
- `MessageSender`: Sends messages via LinkedIn

**Message Generation**:
- AI-powered (OpenAI/Anthropic) for high personalization
- Template-based fallback
- References recruiter profile, company, role
- Asks permission to share resume (no forced attachment)

**Safety**:
- Human approval before sending
- Message validation (length, spam detection)
- Rate limiting

### 4. Job Discovery (`job_discovery/`)

**Purpose**: Find relevant jobs and assist with applications

**Components**:
- `JobSearch`: Searches LinkedIn Jobs
- `JobApplicator`: Assists with Easy Apply

**Workflow**:
1. Search jobs by keywords, location, experience level
2. Filter for Easy Apply jobs (optional)
3. Extract job details and descriptions
4. Match resume to job requirements
5. Pre-fill application forms
6. Pause for human approval before submission

**Safety**:
- Human approval before submission
- Skip if required fields missing
- Rate limiting

### 5. Resume Intelligence (`resume/`)

**Purpose**: Parse resume and match to job requirements

**Components**:
- `ResumeParser`: Extracts structured data from resume (PDF/DOCX)
- `RequirementMatcher`: Matches resume to job requirements

**Features**:
- Parses PDF and DOCX resumes
- Extracts: name, email, phone, skills, experience
- Calculates match scores for jobs
- Generates answers to application questions

### 6. Safety & Logging (`safety/`)

**Purpose**: Ensure safe operation and comprehensive logging

**Components**:
- `RateLimiter`: Enforces daily limits and delays
- `ActionTracker`: Prevents duplicates, tracks actions
- `SafetyLogger`: Comprehensive logging system

**Safety Features**:
- Daily action limits (10-20 actions/day)
- Minimum delays between actions (5-15 minutes)
- Duplicate prevention (recruiters, jobs)
- CAPTCHA/OTP detection
- Human approval requirements

**Logging**:
- All actions logged with timestamps
- Daily summary reports
- Error logging with context
- JSON logs for detailed analysis

## Automation Flow

### Recruiter Outreach Flow

```
1. Start Copilot
   ├─> Initialize browser
   ├─> Login to LinkedIn (or use saved session)
   └─> Check for CAPTCHA/OTP

2. Discover Recruiters
   ├─> Search LinkedIn People
   ├─> Extract recruiter profiles
   ├─> Rank by relevance
   └─> Filter already contacted

3. For Each Recruiter:
   ├─> Generate personalized message
   ├─> Display message to user
   ├─> Wait for approval
   ├─> Send message (if approved)
   ├─> Record action
   └─> Rate limit delay

4. Generate Daily Summary
```

### Job Application Flow

```
1. Discover Jobs
   ├─> Search LinkedIn Jobs
   ├─> Filter Easy Apply (optional)
   └─> Extract job details

2. For Each Job:
   ├─> Analyze job description
   ├─> Calculate match score
   ├─> Display to user
   ├─> Wait for approval
   ├─> Fill application form
   ├─> Upload resume
   ├─> Answer questions
   ├─> Pause for final approval
   ├─> Submit (if approved)
   ├─> Record action
   └─> Rate limit delay

3. Generate Daily Summary
```

## Safety Strategy

### Rate Limiting
- **Daily Limits**: Maximum 10-20 actions per day
- **Action Delays**: 5-15 minutes between actions (randomized)
- **Reset**: Daily limits reset at midnight

### Human-in-the-Loop
- **Message Approval**: All messages require human approval before sending
- **Application Approval**: All applications pause before final submission
- **CAPTCHA Handling**: System stops and waits for manual resolution
- **OTP Handling**: System stops and waits for manual verification

### Duplicate Prevention
- **Database Tracking**: SQLite database tracks all contacted recruiters and applied jobs
- **URL-based Deduplication**: Prevents contacting same recruiter twice
- **Job Deduplication**: Prevents applying to same job twice

### Error Handling
- **Graceful Degradation**: Falls back to simpler methods on errors
- **Comprehensive Logging**: All errors logged with context
- **Safe Shutdown**: Saves state before shutdown

## Limitations

### Technical Limitations
1. **LinkedIn UI Changes**: Selectors may break if LinkedIn updates UI
2. **CAPTCHA**: Cannot bypass CAPTCHA - requires manual intervention
3. **OTP**: Cannot automate OTP verification - requires manual input
4. **Rate Limits**: Limited by LinkedIn's own rate limiting
5. **Form Variations**: Easy Apply forms vary - may not handle all cases

### Functional Limitations
1. **Single Account**: Designed for personal use only
2. **No Mass Automation**: Not designed for bulk operations
3. **Human Approval Required**: Cannot run fully autonomously
4. **Easy Apply Only**: Focuses on Easy Apply jobs (standard applications more complex)

### Legal/Compliance Limitations
1. **LinkedIn ToS**: Must comply with LinkedIn Terms of Service
2. **Personal Use**: Designed for individual job seekers only
3. **No Spam**: Messages must be personalized and non-spammy
4. **Rate Limits**: Must respect LinkedIn's rate limits

## Configuration

All configuration is done via `config.yaml`:

- **LinkedIn Credentials**: Email and password
- **User Profile**: Name, title, skills, experience
- **Search Parameters**: Keywords, locations, filters
- **Safety Settings**: Rate limits, approval requirements
- **AI Settings**: Provider, model, API keys

## Data Storage

- **Sessions**: Browser cookies stored in `./sessions/`
- **Database**: SQLite database at `./sessions/actions.db`
- **Logs**: Daily logs in `./logs/`
- **Resumes**: Resume files in `./resume/`

## Security Considerations

1. **Credentials**: Never commit credentials to version control
2. **Cookies**: Session cookies stored locally (not shared)
3. **API Keys**: AI API keys via environment variables
4. **Resume Data**: Resume files kept local

## Future Enhancements

Potential improvements (not implemented):
- Multi-account support
- Standard application support (non-Easy Apply)
- Advanced NLP for better matching
- Integration with job boards
- Analytics dashboard
- Email notifications

## Conclusion

This architecture prioritizes safety, quality, and realism over speed or volume. The human-in-the-loop design ensures that users maintain control while reducing manual effort. The modular design allows for easy maintenance and extension.

