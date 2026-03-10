from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.subscriptions import subscriptions_bp
from app.models import Subscription
from app.extensions import db
from datetime import datetime


@subscriptions_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        service_name = request.form.get('service_name')
        cost = float(request.form.get('cost'))
        billing_cycle = request.form.get('billing_cycle', 'monthly')
        next_payment_date_str = request.form.get('next_payment_date')
        category = request.form.get('category')

        next_payment_date = None
        if next_payment_date_str:
            next_payment_date = datetime.strptime(next_payment_date_str, '%Y-%m-%d').date()

        subscription = Subscription(
            service_name=service_name,
            cost=cost,
            billing_cycle=billing_cycle,
            next_payment_date=next_payment_date,
            category=category,
            user_id=current_user.id
        )
        db.session.add(subscription)
        db.session.commit()

        flash(f'{service_name} subscription added successfully!', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('subscriptions/add.html')


@subscriptions_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    subscription = Subscription.query.get_or_404(id)

    if subscription.user_id != current_user.id:
        flash('You do not have permission to edit this subscription.', 'danger')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        subscription.service_name = request.form.get('service_name')
        subscription.cost = float(request.form.get('cost'))
        subscription.billing_cycle = request.form.get('billing_cycle', 'monthly')
        next_payment_date_str = request.form.get('next_payment_date')
        subscription.category = request.form.get('category')

        if next_payment_date_str:
            subscription.next_payment_date = datetime.strptime(next_payment_date_str, '%Y-%m-%d').date()

        db.session.commit()

        flash('Subscription updated successfully!', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('subscriptions/edit.html', subscription=subscription)


@subscriptions_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    subscription = Subscription.query.get_or_404(id)

    if subscription.user_id != current_user.id:
        flash('You do not have permission to delete this subscription.', 'danger')
        return redirect(url_for('main.dashboard'))

    db.session.delete(subscription)
    db.session.commit()

    flash('Subscription deleted successfully!', 'success')
    return redirect(url_for('main.dashboard'))
