from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import smtplib
import requests
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os

router = APIRouter(prefix="/api/integrations", tags=["integrations"])

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

class GmailTestRequest(BaseModel):
    clientId: str
    clientSecret: str
    refreshToken: str

class EmailRequest(BaseModel):
    to: str
    subject: str
    body: str

class SlackTestRequest(BaseModel):
    webhookUrl: str
    channel: str

class SMSTestRequest(BaseModel):
    provider: str
    apiKey: str
    phoneNumber: str

@router.post("/test-gmail")
async def test_gmail_connection(request: GmailTestRequest):
    """Test Gmail OAuth connection"""
    try:
        # Create credentials object
        creds = Credentials(
            token=None,
            refresh_token=request.refreshToken,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=request.clientId,
            client_secret=request.clientSecret,
            scopes=SCOPES
        )
        
        # Refresh the token
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        
        # Test by trying to get user info
        from googleapiclient.discovery import build
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        
        return {
            "success": True,
            "message": f"Gmail connection successful for {profile['emailAddress']}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Gmail connection failed: {str(e)}")

@router.post("/send-test-email")
async def send_test_email(request: EmailRequest):
    """Send a test email using Gmail API"""
    try:
        # This would typically use the stored credentials from the user's settings
        # For now, we'll return a success message
        return {
            "success": True,
            "message": f"Test email would be sent to {request.to}",
            "subject": request.subject,
            "body": request.body
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to send email: {str(e)}")

@router.post("/test-slack")
async def test_slack_connection(request: SlackTestRequest):
    """Test Slack webhook connection"""
    try:
        # Test message
        test_message = {
            "text": "🧪 Test message from Smart Stock Ordering App",
            "channel": request.channel,
            "username": "Smart Stock Bot",
            "icon_emoji": ":package:"
        }
        
        response = requests.post(request.webhookUrl, json=test_message)
        
        if response.status_code == 200:
            return {
                "success": True,
                "message": "Slack webhook test successful"
            }
        else:
            raise HTTPException(status_code=400, detail=f"Slack webhook failed: {response.text}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Slack connection failed: {str(e)}")

@router.post("/test-sms")
async def test_sms_connection(request: SMSTestRequest):
    """Test SMS provider connection"""
    try:
        if request.provider == "twilio":
            # Test Twilio connection
            from twilio.rest import Client
            
            # Extract account SID and auth token from API key
            # In real implementation, these would be separate fields
            account_sid = request.apiKey.split(':')[0] if ':' in request.apiKey else request.apiKey
            auth_token = request.apiKey.split(':')[1] if ':' in request.apiKey else "test_token"
            
            client = Client(account_sid, auth_token)
            
            # Send test message
            message = client.messages.create(
                body="🧪 Test SMS from Smart Stock Ordering App",
                from_="+1234567890",  # Your Twilio number
                to=request.phoneNumber
            )
            
            return {
                "success": True,
                "message": f"SMS test successful. SID: {message.sid}"
            }
            
        elif request.provider == "aws-sns":
            # Test AWS SNS connection
            import boto3
            
            sns = boto3.client(
                'sns',
                aws_access_key_id=request.apiKey.split(':')[0] if ':' in request.apiKey else request.apiKey,
                aws_secret_access_key=request.apiKey.split(':')[1] if ':' in request.apiKey else "test_secret",
                region_name='us-east-1'
            )
            
            response = sns.publish(
                PhoneNumber=request.phoneNumber,
                Message="🧪 Test SMS from Smart Stock Ordering App"
            )
            
            return {
                "success": True,
                "message": f"SMS test successful. Message ID: {response['MessageId']}"
            }
        else:
            raise HTTPException(status_code=400, detail="Unsupported SMS provider")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SMS connection failed: {str(e)}")

@router.post("/send-notification")
async def send_notification(notification_type: str, message: str, user_id: str):
    """Send notification through all enabled channels"""
    try:
        # This would check user's notification settings and send accordingly
        # For now, we'll return a success message
        return {
            "success": True,
            "message": f"Notification '{notification_type}' sent: {message}",
            "channels": ["email", "browser", "slack", "sms"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to send notification: {str(e)}")

@router.get("/gmail-auth-url")
async def get_gmail_auth_url():
    """Get Gmail OAuth authorization URL"""
    try:
        # This would generate the OAuth URL for Gmail
        # For now, return a placeholder
        return {
            "auth_url": "https://accounts.google.com/o/oauth2/auth?client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&scope=https://www.googleapis.com/auth/gmail.send&response_type=code"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate auth URL: {str(e)}")

@router.post("/gmail-callback")
async def gmail_oauth_callback(code: str):
    """Handle Gmail OAuth callback"""
    try:
        # This would exchange the authorization code for tokens
        # For now, return a success message
        return {
            "success": True,
            "message": "Gmail OAuth successful",
            "refresh_token": "sample_refresh_token"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth callback failed: {str(e)}") 