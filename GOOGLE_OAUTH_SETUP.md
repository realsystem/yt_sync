# Google Cloud Console - OAuth Redirect URI Setup

## Step-by-Step Guide to Add Redirect URIs

### Step 1: Access Google Cloud Console

1. Open your browser and go to: **https://console.cloud.google.com/**
2. Sign in with your Google account (the same one that owns the OAuth client)

### Step 2: Select Your Project

1. At the top of the page, click the **project dropdown** (next to "Google Cloud")
2. Find and select: **YOUR_PROJECT_NAME**
   - If you don't see it, click "ALL" tab to show all projects

### Step 3: Navigate to Credentials

1. Click the **☰ hamburger menu** (top left, three horizontal lines)
2. Hover over **"APIs & Services"**
3. Click **"Credentials"** from the submenu

   OR use direct link:
   ```
   https://console.cloud.google.com/apis/credentials?project=YOUR_PROJECT_NAME
   ```

### Step 4: Find Your OAuth Client ID

On the Credentials page, you'll see a section called **"OAuth 2.0 Client IDs"**

Look for:
- **Name**: Might be something like "Desktop client 1" or a custom name
- **Client ID**: `YOUR_CLIENT_ID.apps.googleusercontent.com`
- **Type**: Desktop app or Web application

Click on the **name** (or the pencil/edit icon) to open the edit page

### Step 5: Add Redirect URIs

Now you should see the OAuth client configuration page.

#### If it's a "Desktop app" type:

You **WON'T** see an "Authorized redirect URIs" section (Desktop apps don't have this field).

**Solution**: You need to create a new OAuth client as "Web application" type instead:

1. Go back to Credentials page
2. Click **"+ CREATE CREDENTIALS"** at the top
3. Select **"OAuth client ID"**
4. Choose **"Web application"** as Application type
5. Give it a name: "YouTube Archive Agent"
6. Under **"Authorized redirect URIs"** click **"+ ADD URI"**
7. Add these three URIs (one at a time):
   ```
   http://localhost
   http://127.0.0.1:53682/
   http://localhost:53682/
   ```
8. Click **"CREATE"**
9. A popup will show your new credentials - **download the JSON** or copy them

#### If it's a "Web application" type:

You WILL see a section called **"Authorized redirect URIs"**

1. Scroll down to find **"Authorized redirect URIs"**
2. Click **"+ ADD URI"** button
3. In the text field that appears, paste: `http://127.0.0.1:53682/`
4. Press Enter or click outside the field
5. Click **"+ ADD URI"** again
6. Paste: `http://localhost:53682/`
7. Press Enter
8. Click **"+ ADD URI"** again (if needed)
9. Paste: `http://localhost`
10. Scroll to the bottom and click **"SAVE"**

### Step 6: Wait for Propagation

After saving, wait **5-10 minutes** for Google to propagate the changes across their servers.

### Step 7: Download New Credentials (if needed)

If you created a new Web application OAuth client:

1. Go back to the Credentials page
2. Find your new "Web application" client
3. Click the **download icon** (⬇) on the right side
4. This downloads a JSON file like: `client_secret_XXXXXXX.json`
5. Move this file to your project directory:
   ```bash
   mv ~/Downloads/client_secret_*.json /Users/segorov/Projects/yt_sync/
   ```

---

## Alternative: Check Your Current OAuth Type

Run this command to check what's in your current JSON file:

```bash
cat client_secret_YOUR_CLIENT_ID.apps.googleusercontent.com.json | python3 -m json.tool
```

Look for:
```json
{
  "installed": { ... }
}
```

If it says `"installed"`, this is a **Desktop app** type, which doesn't support redirect URIs in the traditional sense.

---

## What You're Looking For

The edit page should look like this:

```
┌─────────────────────────────────────────────┐
│ Edit OAuth client                           │
├─────────────────────────────────────────────┤
│ Name                                        │
│ [YouTube Archive Agent              ]      │
│                                             │
│ Application type                            │
│ ○ Web application                          │
│                                             │
│ Authorized JavaScript origins               │
│ [                                    ] + ADD│
│                                             │
│ Authorized redirect URIs           ← HERE! │
│ [http://localhost                  ] ✕     │
│ [                                    ] + ADD│ ← Click this
│                                             │
│         [CANCEL]           [SAVE]          │
└─────────────────────────────────────────────┘
```

---

## Still Can't Find It?

### Quick Check:

Run this to see what type of OAuth client you have:

```bash
grep -E "installed|web" client_secret_*.json
```

If you see `"installed"`:
- You have a Desktop app OAuth client
- Desktop apps don't have redirect URI fields
- **Solution**: Create a new Web application OAuth client (see above)

If you see `"web"`:
- You have a Web application OAuth client
- The redirect URI field should be visible
- Make sure you're editing the RIGHT client

---

## Need to Create Web Application OAuth?

1. **https://console.cloud.google.com/apis/credentials**
2. Click **"+ CREATE CREDENTIALS"**
3. Select **"OAuth client ID"**
4. **Application type**: Choose "Web application"
5. **Name**: "YouTube Archive Web"
6. **Authorized redirect URIs**: Click "+ ADD URI" and add:
   - `http://localhost`
   - `http://127.0.0.1:53682/`
   - `http://localhost:53682/`
7. Click **CREATE**
8. Download the JSON file
9. Replace your old client_secret file with this new one

---

## Visual Reference

If you see this interface, you're in the right place:

```
OAuth client (Web application)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Client ID
YOUR_PROJECT_ID-xxxxx.apps.googleusercontent.com

Client secret
GOCSPX-xxxxx

Authorized JavaScript origins
For use with requests from a browser

  [empty or has origins]                    + ADD URI

Authorized redirect URIs
For use with requests from a web server

  http://localhost                          ✕
  [                                    ]    + ADD URI  ← Click here


                                    CANCEL    SAVE
```

---

## Quick Test

After adding the URIs and waiting 5 minutes, test with:

```bash
rclone config

# When asked for client_id, paste:
YOUR_CLIENT_ID.apps.googleusercontent.com

# When asked for client_secret, paste:
YOUR_CLIENT_SECRET
```

If the browser opens and you can authorize, it worked!
