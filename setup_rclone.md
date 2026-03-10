# Setting Up rclone with Your Google OAuth Credentials

You have a Google OAuth client secret file, but rclone needs the redirect URI to be configured correctly.

## Option 1: Fix the Redirect URI in Google Cloud Console (Recommended)

### Step 1: Update OAuth Consent Screen

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select project: **YOUR_PROJECT_NAME**
3. Navigate to: **APIs & Services → Credentials**
4. Click on your OAuth 2.0 Client ID: `YOUR_PROJECT_ID-15e3su4bran0lrgbs33bq4vrheiq742v`

### Step 2: Add Redirect URIs

In the "Authorized redirect URIs" section, add BOTH:
- `http://localhost`
- `http://127.0.0.1:53682/`
- `http://localhost:53682/`

Click **Save**

### Step 3: Configure rclone with Your Credentials

```bash
rclone config
```

When prompted:

1. Choose: **n** (New remote)
2. Name: **gdrive**
3. Storage: **drive** (or number for Google Drive, usually 15)
4. **client_id**: `YOUR_CLIENT_ID.apps.googleusercontent.com`
5. **client_secret**: `YOUR_CLIENT_SECRET`
6. Scope: **1** (Full access)
7. Root folder: (leave blank, press Enter)
8. Service account: (leave blank, press Enter)
9. Advanced config: **n**
10. Auto config: **y** (browser will open)
11. Sign in with your Google account
12. Confirm configuration: **y**

---

## Option 2: Quick Setup Script (Automated)

Use the provided script to configure rclone automatically:

```bash
python setup_rclone.py
```

This will:
- Extract credentials from your JSON file
- Configure rclone interactively
- Test the connection
- Create the archive folder

---

## Option 3: Manual Configuration (If Browser Doesn't Work)

If auto-config fails (no browser access), use remote authorization:

### On your MacBook:

```bash
rclone authorize "drive" \
  "YOUR_CLIENT_ID.apps.googleusercontent.com" \
  "YOUR_CLIENT_SECRET"
```

This will:
1. Open your browser for authorization
2. Generate a token string
3. Copy the entire token output

### Then run:

```bash
rclone config
```

And paste the token when prompted.

---

## Verify Setup

After configuration, test the connection:

```bash
# List your Google Drive
rclone lsd gdrive:

# Create archive folder
rclone mkdir gdrive:/youtube_archive

# Test upload
echo "test" > test.txt
rclone copy test.txt gdrive:/youtube_archive/
rclone ls gdrive:/youtube_archive/
rm test.txt
```

You should see your Google Drive folders and the archive folder should be created successfully.

---

## Troubleshooting

### "invalid_client" error
- Make sure redirect URIs are updated in Google Cloud Console
- Wait 5 minutes after updating (propagation delay)
- Clear browser cache and try again

### "access_denied" error
- Make sure OAuth consent screen is configured
- Add your email as a test user if app is in testing mode
- Check that Google Drive API is enabled

### Enable Google Drive API

If not already enabled:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select project: **YOUR_PROJECT_NAME**
3. Navigate to: **APIs & Services → Library**
4. Search for: **Google Drive API**
5. Click **Enable**

---

## Next Steps

Once rclone is configured:

```bash
# Test the agent
python agent.py --check-deps

# Configure your watchlist
cp config.example.py my_config.py
nano my_config.py  # Set WATCHLIST_URL

# Run once to test
python agent.py --config my_config.py --once
```
