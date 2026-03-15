from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.main import main_bp
from app.models import Subscription
from app.extensions import db
from datetime import datetime, date as date_type
from calendar import monthrange


@main_bp.route('/')
@login_required
def dashboard():
    # --- Unfiltered stats — always used for budget card ---
    all_subs = Subscription.query.filter_by(user_id=current_user.id).all()
    active_subs_all = [s for s in all_subs if s.is_active]
    total_monthly_cost = sum(s.monthly_cost for s in active_subs_all)
    active_count_all = len(active_subs_all)
    monthly_budget = current_user.monthly_budget or 0
    budget_remaining = monthly_budget - total_monthly_cost
    budget_percentage = (total_monthly_cost / monthly_budget * 100) if monthly_budget > 0 else 0
    max_cost = max((s.cost for s in all_subs), default=100)

    # --- Read filter/sort params ---
    search     = request.args.get('search', '').strip()
    category   = request.args.get('category', '')
    status     = request.args.get('status', '')        # 'active', 'inactive', or ''
    sort       = request.args.get('sort', '')           # 'name', 'cost_asc', 'cost_desc', 'billing_cycle'
    date_month = request.args.get('date_month', 0, type=int)   # 1-12 or 0 = any
    date_year  = request.args.get('date_year', 0, type=int)    # 0 = any
    date_mode  = request.args.get('date_mode', 'exact')        # 'exact' or 'upto'
    cost_max   = request.args.get('cost_max', 0, type=float)   # 0 = no limit

    is_filtered = any([search, category, status, sort, date_month, date_year, cost_max])

    # --- Build filtered query ---
    query = Subscription.query.filter_by(user_id=current_user.id)

    if search:
        query = query.filter(Subscription.service_name.ilike(f'%{search}%'))

    if category:
        query = query.filter_by(category=category)

    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)

    if cost_max > 0:
        query = query.filter(Subscription.cost <= cost_max)

    if date_year and date_month:
        last_day = monthrange(date_year, date_month)[1]
        if date_mode == 'upto':
            cutoff = date_type(date_year, date_month, last_day)
            query = query.filter(Subscription.next_payment_date <= cutoff)
        else:
            query = query.filter(
                Subscription.next_payment_date >= date_type(date_year, date_month, 1),
                Subscription.next_payment_date <= date_type(date_year, date_month, last_day)
            )
    elif date_year and not date_month:
        if date_mode == 'upto':
            query = query.filter(Subscription.next_payment_date <= date_type(date_year, 12, 31))
        else:
            query = query.filter(
                Subscription.next_payment_date >= date_type(date_year, 1, 1),
                Subscription.next_payment_date <= date_type(date_year, 12, 31)
            )

    if sort == 'name':
        query = query.order_by(Subscription.service_name.asc())
    elif sort == 'cost_asc':
        query = query.order_by(Subscription.cost.asc())
    elif sort == 'cost_desc':
        query = query.order_by(Subscription.cost.desc())
    elif sort == 'billing_cycle':
        query = query.order_by(Subscription.billing_cycle.asc())

    subscriptions = query.all()

    # --- Filtered summary stats ---
    filtered_monthly_cost = sum(s.monthly_cost for s in subscriptions if s.is_active)
    filtered_count = len(subscriptions)
    monthly_cost_share = (filtered_monthly_cost / total_monthly_cost * 100) if total_monthly_cost > 0 else 0

    # Billing cycle breakdown for filtered set (active only)
    cycle_totals = {}
    for s in subscriptions:
        if s.is_active:
            cycle_totals[s.billing_cycle] = cycle_totals.get(s.billing_cycle, 0) + s.cost

    filters = dict(search=search, category=category, status=status, sort=sort,
                   date_month=date_month, date_year=date_year, date_mode=date_mode,
                   cost_max=cost_max)

    return render_template('main/dashboard.html',
                           subscriptions=subscriptions,
                           # unfiltered / budget
                           total_monthly_cost=total_monthly_cost,
                           active_count_all=active_count_all,
                           budget_remaining=budget_remaining,
                           budget_percentage=budget_percentage,
                           max_cost=max_cost,
                           # filtered
                           filtered_monthly_cost=filtered_monthly_cost,
                           filtered_count=filtered_count,
                           monthly_cost_share=monthly_cost_share,
                           cycle_totals=cycle_totals,
                           is_filtered=is_filtered,
                           filters=filters)


@main_bp.route('/update-budget', methods=['POST'])
@login_required
def update_budget():
    budget_str = request.form.get('monthly_budget', '')
    try:
        budget = float(budget_str)
        if budget < 0:
            raise ValueError
    except ValueError:
        flash('Please enter a valid budget amount.', 'danger')
        return redirect(url_for('main.dashboard'))

    current_user.monthly_budget = budget
    db.session.commit()
    flash('Budget updated successfully!', 'success')
    return redirect(url_for('main.dashboard'))


@main_bp.route('/analytics')
@login_required
def analytics():
    active_subs = [s for s in Subscription.query.filter_by(user_id=current_user.id).all() if s.is_active]

    # spending by category
    spending_by_category = {}
    for s in active_subs:
        spending_by_category[s.category] = spending_by_category.get(s.category, 0) + s.monthly_cost

    # top 5 by monthly cost
    top_subscriptions = sorted(
        [(s.service_name, round(s.monthly_cost, 2)) for s in active_subs],
        key=lambda x: x[1], reverse=True
    )[:5]

    total_monthly = sum(s.monthly_cost for s in active_subs)
    subscription_count = len(active_subs)
    average_cost = total_monthly / subscription_count if subscription_count > 0 else 0

    most_expensive = max(active_subs, key=lambda s: s.monthly_cost, default=None)
    cheapest = min(active_subs, key=lambda s: s.monthly_cost, default=None)

    category_labels = list(spending_by_category.keys())
    category_values = [round(v, 2) for v in spending_by_category.values()]
    top_names = [t[0] for t in top_subscriptions]
    top_costs = [t[1] for t in top_subscriptions]

    return render_template('main/analytics.html',
                           spending_by_category=spending_by_category,
                           total_monthly=total_monthly,
                           subscription_count=subscription_count,
                           average_cost=average_cost,
                           most_expensive=most_expensive,
                           cheapest=cheapest,
                           category_labels=category_labels,
                           category_values=category_values,
                           top_names=top_names,
                           top_costs=top_costs)


@main_bp.route('/upcoming-bills')
@login_required
def upcoming_bills():
    today = datetime.now().date()
    raw = Subscription.query.filter(
        Subscription.user_id == current_user.id,
        Subscription.is_active == True,
        Subscription.next_payment_date != None
    ).order_by(Subscription.next_payment_date).all()

    def urgency(days):
        if days < 0:
            return 'overdue'
        elif days <= 7:
            return 'urgent'
        elif days <= 14:
            return 'soon'
        elif days <= 30:
            return 'upcoming'
        return 'later'

    upcoming = []
    for s in raw:
        days = (s.next_payment_date - today).days
        upcoming.append({'sub': s, 'days': days, 'urgency': urgency(days)})

    total_7_days  = sum(e['sub'].monthly_cost for e in upcoming if e['days'] <= 7)
    total_14_days = sum(e['sub'].monthly_cost for e in upcoming if e['days'] <= 14)
    total_30_days = sum(e['sub'].monthly_cost for e in upcoming if e['days'] <= 30)

    return render_template('main/upcoming_bills.html',
                           upcoming=upcoming,
                           total_7_days=total_7_days,
                           total_14_days=total_14_days,
                           total_30_days=total_30_days)
