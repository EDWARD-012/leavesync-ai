# Environment Variables Configuration (.env file)

## Overview
All secret keys, API keys, and global configuration should be stored in the `.env` file in the project root.

## 📋 Complete .env File Template

```env
# ============================================
# Django Core Settings
# ============================================
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://user:password@host:port/database

# ============================================
# Email Configuration
# ============================================
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# ============================================
# Google OAuth (Social Login)
# ============================================
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_SECRET=your-google-secret

# ============================================
# OpenAI API (AI Email Generation)
# ============================================
OPENAI_API_KEY=sk-your-openai-api-key-here
# Model options: gpt-4o-mini (cheapest), gpt-4o, gpt-4o-turbo (best quality)
OPENAI_MODEL=gpt-4o-mini
```

## 🔑 Current Configuration

Your `.env` file should now contain:

### ✅ Already Configured:
- `DJANGO_SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (True/False)
- `DATABASE_URL` - PostgreSQL database connection
- `EMAIL_*` - Email settings for notifications
- `GOOGLE_CLIENT_ID` & `GOOGLE_SECRET` - Google OAuth

### ✅ Just Added:
- `OPENAI_API_KEY` - For AI email generation (replace with your actual key)
- `OPENAI_MODEL` - AI model to use (default: gpt-4o-mini)

## 📝 How to Use

1. **Open your `.env` file** in the project root: `C:\django\leavesync\.env`

2. **Replace placeholder values:**
   ```env
   OPENAI_API_KEY=sk-your-actual-openai-api-key-here
   ```

3. **Get your OpenAI API key:**
   - Visit: https://platform.openai.com/api-keys
   - Create a new secret key
   - Copy and paste it into `.env`

4. **Restart your Django server** after making changes:
   ```bash
   python manage.py runserver
   ```

## 🔒 Security Notes

⚠️ **IMPORTANT:**
- Never commit `.env` file to Git
- Add `.env` to `.gitignore` (if not already there)
- Don't share your API keys publicly
- Rotate keys if exposed

## ✅ Verification

To verify your `.env` is loaded correctly:

```python
python manage.py shell
>>> import os
>>> from django.conf import settings
>>> print(os.getenv("OPENAI_API_KEY"))
# Should print your key (or None if not set)
```

## 📚 All Environment Variables Reference

| Variable | Purpose | Required | Example |
|----------|---------|----------|---------|
| `DJANGO_SECRET_KEY` | Django security key | ✅ Yes | `django-insecure-...` |
| `DEBUG` | Debug mode | ✅ Yes | `True` or `False` |
| `DATABASE_URL` | Database connection | ✅ Yes | `postgresql://...` |
| `EMAIL_HOST` | SMTP server | Optional | `smtp.gmail.com` |
| `EMAIL_HOST_USER` | Email username | Optional | `your-email@gmail.com` |
| `EMAIL_HOST_PASSWORD` | Email password | Optional | `your-app-password` |
| `GOOGLE_CLIENT_ID` | Google OAuth | Optional | `...apps.googleusercontent.com` |
| `GOOGLE_SECRET` | Google OAuth secret | Optional | `GOCSPX-...` |
| `OPENAI_API_KEY` | OpenAI API key | Optional | `sk-...` |
| `OPENAI_MODEL` | AI model name | Optional | `gpt-4o-mini` |

## 🎯 Next Steps

1. **Add your OpenAI API key** to `.env`:
   ```env
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

2. **Restart the server** to load the new environment variable

3. **Test AI email generation** in the "Apply Leave" page

The system will automatically use the API key from `.env` for AI email generation!

