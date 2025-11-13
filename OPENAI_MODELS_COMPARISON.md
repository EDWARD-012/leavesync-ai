# OpenAI Models Comparison & Pricing

## 📊 Model Options for LeaveSync

### 1. **gpt-4o-mini** (Current Default - Recommended) ✅
- **Cost:** $0.15 per 1M input tokens / $0.60 per 1M output tokens
- **Per Email:** ~$0.0001-0.0002 (extremely cheap)
- **Speed:** Fast
- **Quality:** Good for professional emails
- **Best For:** Most use cases, cost-effective

**Example Cost:**
- 1,000 emails = ~$0.10-0.20
- 10,000 emails = ~$1-2

---

### 2. **gpt-4o**
- **Cost:** $2.50 per 1M input tokens / $10 per 1M output tokens
- **Per Email:** ~$0.001 (10x more expensive than mini)
- **Speed:** Fast
- **Quality:** Better quality, more nuanced
- **Best For:** When you need higher quality emails

**Example Cost:**
- 1,000 emails = ~$1
- 10,000 emails = ~$10

---

### 3. **gpt-4o-turbo** (Latest)
- **Cost:** $10 per 1M input tokens / $30 per 1M output tokens
- **Per Email:** ~$0.004 (40x more expensive than mini)
- **Speed:** Very Fast
- **Quality:** Highest quality, most advanced
- **Best For:** When quality is critical and cost is not a concern

**Example Cost:**
- 1,000 emails = ~$4
- 10,000 emails = ~$40

---

## 💰 Cost Comparison

| Model | Cost per Email | 1,000 Emails | 10,000 Emails |
|-------|---------------|--------------|---------------|
| **gpt-4o-mini** | $0.0001-0.0002 | $0.10-0.20 | $1-2 |
| **gpt-4o** | $0.001 | $1 | $10 |
| **gpt-4o-turbo** | $0.004 | $4 | $40 |

## 🎯 Recommendation

**For LeaveSync, use `gpt-4o-mini` because:**
- ✅ Extremely cost-effective
- ✅ Good enough quality for professional emails
- ✅ Fast response times
- ✅ Perfect for leave application emails

**Switch to `gpt-4o-turbo` only if:**
- You need the absolute best quality
- Cost is not a concern
- You're processing very few emails

## 🔄 How to Change Model

### Option 1: Update .env File (Recommended)
```env
# In your .env file
OPENAI_MODEL=gpt-4o-turbo
```

### Option 2: Update settings.py
```python
OPENAI_MODEL = "gpt-4o-turbo"
```

## 📝 Free Tier Information

**Important:** None of the API models are completely free, but:
- New OpenAI accounts get **$5 free credit**
- This gives you ~25,000-50,000 emails with gpt-4o-mini
- After that, you pay per use

**ChatGPT Free Tier** ≠ **API Access**
- ChatGPT free tier is for the chat interface only
- API access requires credits/payment
- But $5 free credit is generous for testing!

## ✅ Current Configuration

Your system is set to use **gpt-4o-mini** by default, which is the best balance of:
- Cost efficiency
- Quality
- Speed

You can easily switch to any model by updating the `OPENAI_MODEL` in your `.env` file!

