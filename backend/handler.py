import json
import os
import boto3

ses_client = boto3.client('ses', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
NOTIFICATION_EMAIL = os.environ.get('NOTIFICATION_EMAIL', 'contact@cloudspendguard.com')

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        full_name = body.get('fullName', '').strip()
        email = body.get('businessEmail', '').strip()
        company = body.get('companyName', '').strip() or 'N/A'
        spend = body.get('monthlySpend', '').strip()

        if not full_name or not email or not spend:
            return {
                'statusCode': 400,
                'headers': { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
                'body': json.dumps({'status': 'error', 'message': 'Missing required fields.'})
            }

        subject = f"[Audit Request] CloudSpendGuard - {company}"
        email_body = f"New Cloud Cost Audit Request:\n\nFull Name: {full_name}\nEmail: {email}\nCompany: {company}\nMonthly Spend: {spend}"

        ses_client.send_email(
            Source=NOTIFICATION_EMAIL,
            Destination={'ToAddresses': [NOTIFICATION_EMAIL]},
            Message={ 'Subject': {'Data': subject}, 'Body': {'Text': {'Data': email_body}} },
            ReplyToAddresses=[email]
        )

        return {
            'statusCode': 200,
            'headers': { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
            'body': json.dumps({'status': 'success', 'message': 'Audit request sent successfully.'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
            'body': json.dumps({'status': 'error', 'message': str(e)})
        }
