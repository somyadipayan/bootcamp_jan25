from workers import celery
from models import *
from celery.schedules import crontab
from mailer import send_email
from flask import render_template 
from datetime import datetime

@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # sender.add_periodic_task(crontab(minute=0, hour=10), send_daily_reminders.s(), name='send_daily_reminders at 10:00')
    sender.add_periodic_task(crontab(minute='*/1'), send_daily_reminders.s(), name='send_daily_reminders every 60 seconds')


@celery.task()
def send_daily_reminders():
    """ Send daily reminders to influencer to checkout public campaigns or pending ad requests """
    influencers = InfluencerProfile.query.all()
    for influencer in influencers:
        pending_ad_requests = AdRequests.query.filter_by(influencer_id=influencer.id).filter_by(status='Pending').all()
        if pending_ad_requests:
            body = render_template('daily_reminder.html', pending_request_count=len(pending_ad_requests), influencer=influencer)
            send_email('Influencer: Pending Ad Requests', influencer.user.email, body)
            return f"Mail sent to {influencer.name} for {len(pending_ad_requests)} pending ad requests"

@celery.task()
def send_monthly_activity_report():
    sponsors = SponsorProfile.query.all()
    for sponsor in sponsors:
        now = datetime.now()
        last_month = now - datetime.timedelta(days=30)
        # Find the count of AdRequests for each campaign in last month
        accepted_ad_requests = AdRequests.query.join(Campaign).filter(Campaign.sponsor_id == sponsor.id).filter(Campaign.created_at.between(last_month, now)).filter_by(status='Accepted').all()
        rejected_ad_requests = AdRequests.query.join(Campaign).filter(Campaign.sponsor_id == sponsor.id).filter(Campaign.created_at.between(last_month, now)).filter_by(status='Rejected').all()
        pending_ad_requests = AdRequests.query.join(Campaign).filter(Campaign.sponsor_id == sponsor.id).filter(Campaign.created_at.between(last_month, now)).filter_by(status='Pending').all()
        ad_requests = {'accepted': len(accepted_ad_requests), 'rejected': len(rejected_ad_requests), 'pending': len(pending_ad_requests)}
        report_month = datetime.now().strftime('%B %Y')
        html_content = render_template('monthly_activity_report.html', sponsor=sponsor, ad_requests=ad_requests,  report_month=report_month, pending_ad_requests=pending_ad_requests)
        send_email(to=sponsor.user.email, subject='Monthly Activity Report', body=html_content)

