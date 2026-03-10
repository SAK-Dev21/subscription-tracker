from flask import render_template
from flask_login import login_required, current_user
from app.main import main_bp
from app.models import Subscription
from datetime import datetime, timedelta


@main_bp.route('/')
@login_required
def dashboard():
    subscriptions = Subscription.query.filter_by(user_id=current_user.id).all()
    total_monthly = sum(s.monthly_cost for s in subscriptions)
    return render_template('main/dashboard.html',
                           subscriptions=subscriptions,
                           total_monthly=total_monthly)


@main_bp.route('/analytics')
@login_required
def analytics():
    subscriptions = Subscription.query.filter_by(user_id=current_user.id).all()
    return render_template('main/analytics.html', subscriptions=subscriptions)


@main_bp.route('/upcoming-bills')
@login_required
def upcoming_bills():
    today = datetime.now().date()
    upcoming = Subscription.query.filter(
        Subscription.user_id == current_user.id,
        Subscription.next_payment_date <= today + timedelta(days=30),
        Subscription.next_payment_date >= today
    ).order_by(Subscription.next_payment_date).all()
    return render_template('main/upcoming_bills.html', upcoming=upcoming)
