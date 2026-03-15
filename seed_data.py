from app import create_app
from app.extensions import db
from app.models import User, Subscription
from datetime import date, timedelta
import random


def calculate_next_payment(start_date, billing_cycle):
    """Calculate next payment date from start_date based on billing cycle."""
    today = date.today()
    if billing_cycle == 'monthly':
        next_date = start_date
        while next_date <= today:
            # Advance by ~1 month
            month = next_date.month + 1
            year = next_date.year
            if month > 12:
                month = 1
                year += 1
            day = min(start_date.day, 28)  # avoid Feb issues
            next_date = next_date.replace(year=year, month=month, day=day)
        return next_date
    elif billing_cycle == 'yearly':
        next_date = start_date
        while next_date <= today:
            next_date = next_date.replace(year=next_date.year + 1)
        return next_date
    elif billing_cycle == 'weekly':
        next_date = start_date
        while next_date <= today:
            next_date += timedelta(weeks=1)
        return next_date
    return today + timedelta(days=30)


def random_start():
    """Return a random start date between 3 months and 2 years ago."""
    days_ago = random.randint(90, 730)
    return date.today() - timedelta(days=days_ago)


def create_subscriptions(user_id, subs_data):
    """Create and add Subscription objects for a given user from a list of dicts."""
    for data in subs_data:
        start = random_start()
        cycle = data['billing_cycle']
        sub = Subscription(
            service_name=data['service_name'],
            cost=data['cost'],
            billing_cycle=cycle,
            category=data['category'],
            start_date=start,
            next_payment_date=calculate_next_payment(start, cycle),
            cancellation_url=data.get('cancellation_url'),
            notes=data.get('notes'),
            is_active=data.get('is_active', True),
            user_id=user_id
        )
        db.session.add(sub)


def seed():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        # --- User 1 ---
        user1 = User(username='testuser1', email='test1@example.com', monthly_budget=100.00)
        user1.set_password('password123')
        db.session.add(user1)
        db.session.flush()  # get user1.id

        subs_data_1 = [
            dict(service_name='Netflix Standard', cost=10.99, billing_cycle='monthly',
                 category='entertainment',
                 cancellation_url='https://www.netflix.com/cancelplan'),
            dict(service_name='Spotify Premium', cost=10.99, billing_cycle='monthly',
                 category='entertainment',
                 cancellation_url='https://www.spotify.com/account/cancel/'),
            dict(service_name='Amazon Prime', cost=95.00, billing_cycle='yearly',
                 category='entertainment',
                 cancellation_url='https://www.amazon.co.uk/gp/help/customer/display.html?nodeId=201118390'),
            dict(service_name='Disney+ Standard', cost=7.99, billing_cycle='monthly',
                 category='entertainment'),
            dict(service_name='YouTube Premium', cost=12.99, billing_cycle='monthly',
                 category='entertainment'),
            dict(service_name='Deliveroo Plus', cost=3.49, billing_cycle='monthly',
                 category='food'),
            dict(service_name='HelloFresh', cost=39.99, billing_cycle='monthly',
                 category='food', is_active=False,
                 notes='Cancelled — too expensive'),
            dict(service_name='Adobe Creative Cloud', cost=54.99, billing_cycle='monthly',
                 category='software'),
            dict(service_name='Microsoft 365 Personal', cost=59.99, billing_cycle='yearly',
                 category='software'),
            dict(service_name='iCloud+ 200GB', cost=2.99, billing_cycle='monthly',
                 category='software'),
            dict(service_name='PureGym', cost=24.99, billing_cycle='monthly',
                 category='fitness'),
            dict(service_name='Strava Premium', cost=6.99, billing_cycle='monthly',
                 category='fitness', is_active=False,
                 notes='Free version is enough'),
            dict(service_name='EE Mobile Contract', cost=35.00, billing_cycle='monthly',
                 category='utilities'),
            dict(service_name='Sky Broadband', cost=32.00, billing_cycle='monthly',
                 category='utilities'),
            dict(service_name='NordVPN', cost=89.99, billing_cycle='yearly',
                 category='software'),
        ]

        create_subscriptions(user1.id, subs_data_1)

        # --- User 2 ---
        user2 = User(username='testuser2', email='test2@example.com', monthly_budget=150.00)
        user2.set_password('password123')
        db.session.add(user2)
        db.session.flush()

        subs_data_2 = [
            dict(service_name='Netflix Premium', cost=17.99, billing_cycle='monthly',
                 category='entertainment',
                 cancellation_url='https://www.netflix.com/cancelplan'),
            dict(service_name='Apple TV+', cost=8.99, billing_cycle='monthly',
                 category='entertainment'),
            dict(service_name='Amazon Prime', cost=95.00, billing_cycle='yearly',
                 category='entertainment',
                 cancellation_url='https://www.amazon.co.uk/gp/help/customer/display.html?nodeId=201118390'),
            dict(service_name='Audible', cost=7.99, billing_cycle='monthly',
                 category='entertainment'),
            dict(service_name='Spotify Family', cost=17.99, billing_cycle='monthly',
                 category='entertainment'),
            dict(service_name='Gousto', cost=34.99, billing_cycle='monthly',
                 category='food'),
            dict(service_name='GitHub Copilot', cost=9.17, billing_cycle='monthly',
                 category='software'),
            dict(service_name='iCloud+ 2TB', cost=8.99, billing_cycle='monthly',
                 category='software'),
            dict(service_name='Headspace', cost=49.99, billing_cycle='yearly',
                 category='fitness'),
            dict(service_name='Peloton App', cost=12.99, billing_cycle='monthly',
                 category='fitness', is_active=False,
                 notes='Paused — not using it'),
            dict(service_name='Virgin Media Broadband', cost=38.00, billing_cycle='monthly',
                 category='utilities'),
            dict(service_name='Vodafone Mobile', cost=28.00, billing_cycle='monthly',
                 category='utilities'),
        ]

        create_subscriptions(user2.id, subs_data_2)

        db.session.commit()

        print('Database seeded successfully!')
        print()
        print('testuser1  —  test1@example.com / password123  —  budget: £100.00')
        print(f'  {len(subs_data_1)} subscriptions created')
        print()
        print('testuser2  —  test2@example.com / password123  —  budget: £150.00')
        print(f'  {len(subs_data_2)} subscriptions created')


if __name__ == '__main__':
    seed()
