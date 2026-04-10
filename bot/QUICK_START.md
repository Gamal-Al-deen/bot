# 🚀 Quick Start Guide - Supabase Setup

## ⚡ 5 Steps to Get Your Bot Running with Supabase

---

### Step 1: Create Supabase Project (5 minutes)

1. Go to https://supabase.com
2. Click **Start your project** or **New Project**
3. Sign in with GitHub/Google/Email
4. Click **New Project**
5. Fill in:
   - **Name**: SMM Bot (or any name)
   - **Database Password**: Create a strong password (save it!)
   - **Region**: Choose closest to your users
6. Click **Create new project**
7. Wait 2-3 minutes for setup

---

### Step 2: Run Database Schema (2 minutes)

1. In your Supabase dashboard, click **SQL Editor** (left sidebar)
2. Click **New query**
3. Open the file `supabase_schema.sql` from your bot folder
4. Copy ALL content
5. Paste into SQL Editor
6. Click **Run** (bottom right)
7. You should see: `Success. No rows returned`

✅ **Verify tables created:**
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

You should see 7 tables:
- categories
- channels
- orders
- pricing_rules
- services
- settings
- users

---

### Step 3: Get API Keys (1 minute)

1. Click **Project Settings** ⚙️ (bottom left)
2. Click **API** (under Configuration)
3. Copy these two values:

   **Project URL:**
   ```
   https://xxxxxxxxxxxxx.supabase.co
   ```

   **service_role key (secret):**
   ```
   eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (long string)
   ```

⚠️ **IMPORTANT**: Use `service_role` key, NOT `anon` key!

---

### Step 4: Update config.py (1 minute)

Open `config.py` in your bot folder and update these lines:

```python
# Find these lines at the bottom:
SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_KEY = "YOUR_SUPABASE_KEY"

# Replace with your actual values:
SUPABASE_URL = "https://xxxxxxxxxxxxx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

Save the file.

---

### Step 5: Install & Run (2 minutes)

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Run the bot:**
```bash
python run.py
```

**Check the output in `log.txt`:**

✅ **Success looks like this:**
```
🗄️ Initializing Supabase Database...
✅ Supabase connected successfully!
🎯 Database system is ready!
```

❌ **If you see this:**
```
⚠️ Supabase connection failed!
```

**Fix:**
1. Check `SUPABASE_URL` is correct (starts with https://)
2. Check `SUPABASE_KEY` is the service_role key (not anon)
3. Verify SQL schema was executed successfully
4. Check your internet connection

---

## 🎯 First Steps After Setup

### 1. Add a Category (Admin)
```
/adminpanel → إدارة الخدمات → إضافة قسم جديد
Send: خدمات Instagram
```

### 2. Add a Service (Admin)
```
/adminpanel → إدارة الخدمات → إضافة خدمة
Choose: خدمات Instagram
Send service ID from API: 123
```

### 3. Check Database (Supabase)
Go to **Table Editor** in Supabase dashboard
You should see:
- 1 row in `categories` table
- 1 row in `services` table
- 1 row in `pricing_rules` table (default 50% percentage)

---

## 📊 Verify Everything Works

### Test 1: User Registration
```
User sends: /start
Check users table: 1 row added
```

### Test 2: Add Balance (Admin)
```
Admin sends: /addbalance USER_ID 10
Check users table: balance = 10.0
```

### Test 3: Place Order
```
User browses services → selects service → enters link → enters quantity → confirms
Check orders table: 1 row added with all details
Check users table: balance decreased
```

---

## 🐛 Common Issues

### Issue: "ModuleNotFoundError: No module named 'supabase'"
**Fix:**
```bash
pip install supabase==2.3.4
```

### Issue: "Connection refused" or timeout
**Fix:**
- Check internet connection
- Verify SUPABASE_URL is correct
- Check Supabase project is active (not paused)

### Issue: "relation 'users' does not exist"
**Fix:**
- Go to SQL Editor
- Re-run `supabase_schema.sql`
- Verify all 7 tables created

### Issue: Orders not saving
**Fix:**
- Check `log.txt` for errors
- Verify database connection is successful
- Check if user exists before placing order

---

## 📱 Admin Commands Quick Reference

| Command | Description |
|---------|-------------|
| `/adminpanel` | Open admin control panel |
| `/addbalance USER_ID AMOUNT` | Add balance to user |
| `/removebalance USER_ID AMOUNT` | Remove balance from user |
| `/setpercent VALUE` | Set percentage pricing |
| `/setprice VALUE` | Set fixed pricing |
| `/broadcast` | Send message to all users |
| `/addcategory` | Add new category |
| `/addservice` | Add service to category |

---

## 🎉 You're Done!

Your bot is now running with a professional Supabase database!

**What's next:**
1. Add more categories and services
2. Configure pricing for each service
3. Set up notification channel
4. Start accepting orders!

---

## 📚 Need More Help?

- **Full Arabic Guide**: Read `SUPABASE_SYSTEM_GUIDE_AR.md`
- **Migration Details**: Read `MIGRATION_SUMMARY.md`
- **Supabase Docs**: https://supabase.com/docs
- **Check Logs**: Open `log.txt` for detailed operation logs

---

**⚡ Total Setup Time: ~10 minutes**

**🚀 Your bot is now production-ready with cloud database!**
