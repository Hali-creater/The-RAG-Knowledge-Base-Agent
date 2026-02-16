import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def send_lead_alert(lead):
    """Sends an email alert for a high-priority lead."""
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    receiver_email = os.getenv("EMAIL_RECEIVER")

    if not all([smtp_user, smtp_password, receiver_email]):
        logger.warning("Email configuration missing. Skipping alert.")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🔥 HIGH PRIORITY LEAD: {lead['title']}"
    msg["From"] = f"Real Estate AI <{smtp_user}>"
    msg["To"] = receiver_email

    # HTML Email Template
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
            <h2 style="color: #dc3545;">🚨 High Priority Lead Detected!</h2>
            <hr>
            <p><strong>Title:</strong> {lead['title']}</p>
            <p><strong>Score:</strong> <span style="font-size: 1.2em; font-weight: bold; color: #dc3545;">{lead['intent_score']}</span> ({lead['intent_level']})</p>
            <p><strong>Type:</strong> {lead['lead_type']}</p>
            <p><strong>Source:</strong> {lead['source']}</p>
            <p><strong>Location:</strong> {lead['location'] or 'Not specified'}</p>
            <p><strong>Price:</strong> {lead.get('price', 'N/A')}</p>
            <div style="background-color: #fff; padding: 15px; border: 1px solid #ddd; border-radius: 5px; margin-top: 10px;">
                <p><strong>Contact Info:</strong></p>
                <ul>
                    <li>📞 Phone: {lead.get('phone', '---')}</li>
                    <li>📧 Email: {lead.get('email', '---')}</li>
                </ul>
            </div>
            <p><strong>Description:</strong><br>{lead['description'][:300]}...</p>
            <div style="margin-top: 20px;">
                <a href="{lead['url']}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">View Original Listing</a>
            </div>
        </div>
        <p style="font-size: 0.8em; color: #777; margin-top: 20px;">
            This is an automated alert from your Real Estate Lead Intelligence System.
        </p>
    </body>
    </html>
    """

    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, receiver_email, msg.as_string())
        logger.info(f"Email alert sent for lead: {lead['title']}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email alert: {e}")
        return False
