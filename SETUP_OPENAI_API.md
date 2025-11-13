# How to Set Up OpenAI API for AI Email Generation

## Step 1: Get Your OpenAI API Key

1. **Go to OpenAI Platform:**
   - Visit: https://platform.openai.com/
   - Sign up or log in to your account

2. **Navigate to API Keys:**
   - Click on your profile (top right)
   - Go to "API keys" or visit: https://platform.openai.com/api-keys

3. **Create a New API Key:**
   - Click "Create new secret key"
   - Give it a name (e.g., "LeaveSync")
   - Copy the key immediately (you won't see it again!)
   - Format: `sk-...` (starts with "sk-")

## Step 2: Add API Key to Your Project

### ✅ Using .env File (Already Set Up!)

Your `.env` file already has the OpenAI configuration added. Just need to replace the placeholder:

1. **Open `.env` file** in your project root: `C:\django\leavesync\.env`

2. **Find this line:**
   ```env
   OPENAI_API_KEY=sk-your-openai-api-key-here
   ```

3. **Replace with your actual key:**
   ```env
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

4. **Save the file** - The configuration is already there, just update the value!

5. **Make sure `.env` is in `.gitignore`** (don't commit your API key!)

### Option B: Set Environment Variable Directly

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-your-actual-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set OPENAI_API_KEY=sk-your-actual-api-key-here
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY=sk-your-actual-api-key-here
```

### Option C: Add to settings.py (Not Recommended for Production)

Only for testing - don't commit this:
```python
OPENAI_API_KEY = "sk-your-actual-api-key-here"
```

## Step 3: Restart Your Django Server

After adding the API key, restart your development server:
```bash
python manage.py runserver
```

## Step 4: Test It

1. Go to "Apply Leave" page
2. Fill in the form
3. Click "🤖 Generate Email Draft"
4. You should see an AI-enhanced professional email!

## Troubleshooting

### Still seeing "OPENAI_API_KEY not found"?

1. **Check .env file location:**
   - Should be in: `C:\django\leavesync\.env`
   - Same directory as `manage.py`

2. **Check .env file format:**
   ```
   OPENAI_API_KEY=sk-... (no quotes, no spaces)
   ```

3. **Restart the server** after adding the key

4. **Check if python-dotenv is installed:**
   ```bash
   pip install python-dotenv
   ```

5. **Verify in Django shell:**
   ```python
   python manage.py shell
   >>> import os
   >>> from django.conf import settings
   >>> print(os.getenv("OPENAI_API_KEY"))
   # Should print your key
   ```

## Cost Information

- **gpt-4o-mini** (default): Very affordable, ~$0.15 per 1M input tokens
- Each email generation uses ~500-1000 tokens
- Estimated cost: ~$0.0001-0.0002 per email
- Free tier: $5 credit for new accounts

## Security Notes

⚠️ **IMPORTANT:**
- Never commit your API key to Git
- Add `.env` to `.gitignore`
- Don't share your API key publicly
- Rotate keys if exposed

## Without API Key

If you don't set up the API key, the system will:
- Use an enhanced fallback template
- Fix basic typos and grammar
- Still generate professional emails
- Just won't have AI enhancement

The system works fine without it, but AI enhancement makes emails much better!

