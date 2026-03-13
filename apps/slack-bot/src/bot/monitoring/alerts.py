"""
Basic alerts functionality for the monitoring module.
"""
import os
import json
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, List, Any, Union

def save_alert_history(
    alert_data: Dict[str, Any],
    history_file: str = "alert_history.json"
) -> None:
    """
    Save alert data to a history file.
    
    Args:
        alert_data: Dictionary containing alert information
        history_file: Path to the history file (default: alert_history.json)
    """
    try:
        # Add timestamp to alert data
        alert_data['timestamp'] = datetime.datetime.now().isoformat()
        
        # Load existing history
        history = []
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    history = json.load(f)
            except json.JSONDecodeError:
                # If file is corrupted, start fresh
                pass
        
        # Append new alert
        history.append(alert_data)
        
        # Save updated history
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"Error saving alert history: {e}")

def send_email_alert(
    smtp_config: Dict[str, str],
    message: str,
    subject: str,
    recipients: Union[str, List[str]],
) -> None:
    """
    Send an alert via email.
    
    Args:
        smtp_config: Dictionary containing SMTP configuration:
            - host: SMTP server host
            - port: SMTP server port
            - username: SMTP authentication username
            - password: SMTP authentication password
            - from_email: Sender email address
        message: The message body
        subject: Email subject
        recipients: Single recipient email or list of recipient emails
    """
    if isinstance(recipients, str):
        recipients = [recipients]
        
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_config['from_email']
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject
        
        msg.attach(MIMEText(message, 'plain'))
        
        server = smtplib.SMTP(smtp_config['host'], int(smtp_config['port']))
        server.starttls()
        server.login(smtp_config['username'], smtp_config['password'])
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Error sending email alert: {e}")

def send_slack_alert(webhook_url: str, message: str, channel: Optional[str] = None) -> None:
    """
    Send an alert to Slack using a webhook URL.
    
    Args:
        webhook_url: The Slack webhook URL to send the alert to
        message: The message to send
        channel: Optional channel override
    """
    try:
        import requests
        payload = {
            "text": message,
        }
        if channel:
            payload["channel"] = channel
            
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"Error sending Slack alert: {e}")

def send_alert(alert_config, message, level="warning"):
    """
    Send an alert through configured channels.
    
    Args:
        alert_config: AlertConfig instance containing channel configuration
        message: The alert message to send
        level: Alert level (e.g., "warning", "error", "critical")
    """
    if not alert_config.is_enabled():
        return
        
    for channel in alert_config.channels:
        try:
            channel.send(message, level=level)
        except Exception as e:
            # Log the error but don't raise to ensure all channels are attempted
            print(f"Error sending alert through channel {channel}: {e}")

    def __init__(self, enabled=True, threshold=None, channels=None):
        self.enabled = enabled
        self.threshold = threshold
        self.channels = channels or []

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __init__(self, name, description, metric, threshold):
        super().__init__(name, description)
        self.metric = metric
        self.threshold = threshold

    def __init__(self):
        """Initialize alert manager."""
        self.alerts = []
        self.configs = []

    def get_active_alerts(self):
        """Retourne les alertes actives."""
        return [alert for alert in self.alerts if alert.severity in ['critical', 'high']]

# Export these classes and functions
__all__ = ['Alert', 'MetricAlert', 'AlertConfig', 'AlertManager', 'check_thresholds', 'send_alert', 'send_slack_alert', 'send_email_alert', 'save_alert_history']
