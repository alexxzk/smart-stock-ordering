# Integrations Setup Guide

## 🚀 Overview

The Smart Stock Ordering App supports multiple integrations to enhance your workflow:

- **Gmail API** - Send automated emails for orders and notifications
- **Slack** - Receive real-time notifications in your Slack workspace
- **SMS** - Get text message alerts for critical events
- **Browser Notifications** - In-app notifications

## 📧 Gmail Integration Setup

### 1. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

### 2. Create OAuth 2.0 Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Web application"
4. Add authorized redirect URIs:
   - `http://localhost:5174/integrations` (for development)
   - `https://yourdomain.com/integrations` (for production)
5. Note down your Client ID and Client Secret

### 3. Get Refresh Token
1. Use the OAuth 2.0 Playground:
   - Go to [OAuth 2.0 Playground](https://developers.google.com/oauthplayground/)
   - Click the settings icon (⚙️)
   - Check "Use your own OAuth credentials"
   - Enter your Client ID and Client Secret
2. Select Gmail API v1 > "Send email"
3. Click "Authorize APIs"
4. Click "Exchange authorization code for tokens"
5. Copy the Refresh Token

### 4. Configure in App
1. Go to Integrations page in your app
2. Enable Gmail integration
3. Enter your credentials:
   - Client ID
   - Client Secret
   - Refresh Token
   - Your email address
4. Test the connection

## 💬 Slack Integration Setup

### 1. Create Slack App
1. Go to [Slack API](https://api.slack.com/apps)
2. Click "Create New App" > "From scratch"
3. Name your app (e.g., "Smart Stock Bot")
4. Select your workspace

### 2. Configure Incoming Webhooks
1. In your app settings, go to "Incoming Webhooks"
2. Toggle "Activate Incoming Webhooks" to On
3. Click "Add New Webhook to Workspace"
4. Choose the channel where you want notifications
5. Copy the Webhook URL

### 3. Configure in App
1. Go to Integrations page
2. Enable Slack integration
3. Enter:
   - Webhook URL
   - Channel name (e.g., "#general")
4. Test the connection

## 📱 SMS Integration Setup

### Option 1: Twilio
1. Sign up for [Twilio](https://www.twilio.com/)
2. Get your Account SID and Auth Token from the dashboard
3. Buy a phone number for sending SMS
4. In the app, enter:
   - Provider: Twilio
   - API Key: `ACCOUNT_SID:AUTH_TOKEN`
   - Phone Number: Your Twilio number

### Option 2: AWS SNS
1. Create AWS account
2. Go to SNS service
3. Create access keys for programmatic access
4. In the app, enter:
   - Provider: AWS SNS
   - API Key: `ACCESS_KEY:SECRET_KEY`
   - Phone Number: Your phone number

## 🔔 Browser Notifications

Browser notifications work automatically when you:
1. Allow notifications when prompted
2. Enable "Browser Notifications" in the app settings

## ⚙️ Environment Variables

Add these to your `.env` file for production:

```bash
# Gmail API
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret

# Slack
SLACK_WEBHOOK_URL=your_webhook_url

# Twilio
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_twilio_number

# AWS SNS
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
```

## 🧪 Testing Integrations

### Test Gmail
1. Enable Gmail integration
2. Enter your credentials
3. Click "Test Connection"
4. Click "Send Test Email"

### Test Slack
1. Enable Slack integration
2. Enter webhook URL and channel
3. Click "Test Connection"
4. Check your Slack channel for the test message

### Test SMS
1. Enable SMS integration
2. Enter provider credentials
3. Click "Test Connection"
4. Check your phone for the test message

## 🔧 Troubleshooting

### Gmail Issues
- **"Invalid credentials"**: Check your Client ID, Secret, and Refresh Token
- **"Access denied"**: Make sure Gmail API is enabled
- **"Token expired"**: Get a new refresh token

### Slack Issues
- **"Webhook failed"**: Check the webhook URL is correct
- **"Channel not found"**: Make sure the channel exists and bot has access
- **"Rate limited"**: Wait a few minutes before sending more messages

### SMS Issues
- **Twilio errors**: Check Account SID and Auth Token
- **AWS SNS errors**: Verify access keys and region
- **Phone number format**: Use international format (+1234567890)

## 📋 Notification Types

The app can send notifications for:

- **Low Stock Alerts**: When inventory items fall below minimum levels
- **Order Updates**: When order status changes
- **Forecast Alerts**: When sales forecasts indicate unusual patterns
- **System Notifications**: Important app events

## 🔒 Security Best Practices

1. **Never commit credentials** to version control
2. **Use environment variables** for sensitive data
3. **Rotate API keys** regularly
4. **Limit API scopes** to minimum required permissions
5. **Monitor API usage** for unusual activity

## 🚀 Production Deployment

For production deployment:

1. **Update redirect URIs** in Google Cloud Console
2. **Use HTTPS** for all webhook URLs
3. **Set up proper error handling** and logging
4. **Monitor integration health** regularly
5. **Backup configuration** settings

## 📞 Support

If you encounter issues:

1. Check the browser console for errors
2. Verify all credentials are correct
3. Test each integration individually
4. Check API quotas and limits
5. Review the troubleshooting section above

For additional help, check the logs and provide:
- Error messages
- Integration type
- Steps to reproduce
- Environment (development/production) 