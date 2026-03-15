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
        service_name = request.form.get('service_name', '').strip()
        cost_str = request.form.get('cost', '')
        billing_cycle = request.form.get('billing_cycle', 'monthly')
        next_payment_date_str = request.form.get('next_payment_date')
        category = request.form.get('category', 'other')
        cancellation_url = request.form.get('cancellation_url', '').strip() or None
        notes = request.form.get('notes', '').strip() or None

        if not service_name:
            flash('Service name is required.', 'danger')
            return render_template('subscriptions/add.html')

        try:
            cost = float(cost_str)
            if cost < 0:
                raise ValueError
        except ValueError:
            flash('Cost must be a positive number.', 'danger')
            return render_template('subscriptions/add.html')

        next_payment_date = None
        if next_payment_date_str:
            next_payment_date = datetime.strptime(next_payment_date_str, '%Y-%m-%d').date()

        subscription = Subscription(
            service_name=service_name,
            cost=cost,
            billing_cycle=billing_cycle,
            next_payment_date=next_payment_date,
            category=category,
            cancellation_url=cancellation_url,
            notes=notes,
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
        service_name = request.form.get('service_name', '').strip()
        cost_str = request.form.get('cost', '')
        billing_cycle = request.form.get('billing_cycle', 'monthly')
        next_payment_date_str = request.form.get('next_payment_date')
        category = request.form.get('category', 'other')
        cancellation_url = request.form.get('cancellation_url', '').strip() or None
        notes = request.form.get('notes', '').strip() or None

        if not service_name:
            flash('Service name is required.', 'danger')
            return render_template('subscriptions/edit.html', subscription=subscription)

        try:
            cost = float(cost_str)
            if cost < 0:
                raise ValueError
        except ValueError:
            flash('Cost must be a positive number.', 'danger')
            return render_template('subscriptions/edit.html', subscription=subscription)

        subscription.service_name = service_name
        subscription.cost = cost
        subscription.billing_cycle = billing_cycle
        subscription.category = category
        subscription.cancellation_url = cancellation_url
        subscription.notes = notes

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
