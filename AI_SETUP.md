# AI Summary Feature Setup

## Overview
The People Manager now includes an **AI-powered summary feature** that uses **Google Gemini** to intelligently summarize contact information.

## Features
- 🤖 **Smart Summarization**: Processes raw details and timestamps into clear summaries
- 📊 **Key Information Extraction**: Identifies phone numbers, emails, addresses automatically
- 📅 **Chronological Understanding**: Understands update history and timestamps
- ✨ **Concise Output**: 3-5 bullet points max, easy to scan
- 🆓 **Free to Use**: Google Gemini has generous free tier limits

## Setup Instructions

### 1. Get Google Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Select a Google Cloud project (or create a new one)
5. Copy the API key

### 2. Set Environment Variable

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set GEMINI_API_KEY=your-api-key-here
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY="your-api-key-here"
```

**For permanent setup, add to your system environment variables.**

### 3. Run the Application

```bash
python app.py
```

The AI feature will automatically activate if the API key is detected.

## Usage

1. **Add or Update** person details with timestamps
2. Click the **"Summary"** button on any person card
3. Wait a few seconds for the AI to analyze
4. View the generated summary
5. Click **"Refresh"** to update the summary

## Example

**Raw Details:**
```
--- Added (Nov 1, 2025, 10:00 AM) ---
Phone: 123-456-7890
Email: john@example.com

--- Update (Nov 1, 2025, 11:00 AM) ---
Met at Python conference
Discussed AI projects

--- Update (Nov 1, 2025, 02:00 PM) ---
Follow up next week about collaboration
Interested in ML applications
```

**AI Summary:**
```
• Contact: john@example.com, Phone: 123-456-7890
• Met at Python conference, discussed AI and ML projects  
• Follow-up scheduled next week for collaboration
```

## Cost Considerations

- Uses **Google Gemini 2.5 Flash** (free model)
- **FREE**: 15 requests per minute, 1,500 per day (generous free tier)
- No credit card required for basic usage
- Only generates on-demand (not automatic)

## Without API Key

If `GEMINI_API_KEY` is not set:
- Application runs normally
- AI Summary button still visible
- Clicking shows: "AI feature not configured"
- All other features work as expected

## Troubleshooting

**Error: "AI feature not configured"**
- Solution: Set the `GEMINI_API_KEY` environment variable

**Error: "Failed to generate summary"**
- Check API key is valid
- Verify you're within free tier limits (15 requests/min, 1,500/day)
- Check internet connection
- If quota exceeded, wait 60 seconds (for minute limit) or 24 hours (for daily limit)

**Button shows "No details available"**
- Add some details to the person first
- Details field cannot be empty

## Security

- ✅ API key loaded from environment variable
- ✅ Not stored in code or database
- ✅ Requires login to access
- ✅ Only processes data you provide

## Privacy

- Data is sent to Google Gemini API for processing
- Google's data usage policy applies
- Consider this for sensitive information
- For full privacy, disable the feature (don't set API key)

---

**Need help?** Check the main [README.md](README.md) for general setup instructions.

