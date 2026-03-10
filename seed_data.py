from app import create_app
from app.extensions import db
from app.models import User, Subscription
from datetime import date, timedelta


def seed():
    app = create_app()
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        # Create a demo user
        user = User(username='demo', email='demo@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        # Create sample subscriptions
        subscriptions = [
            Subscription(
                service_name='Netflix',
                cost=15.99,
                billing_cycle='monthly',
                next_payment_date=date.today() + timedelta(days=5),
                category='entertainment',
                user_id=user.id
            ),
            Subscription(
                service_name='Spotify',
                cost=10.99,
                billing_cycle='monthly',
                next_payment_date=date.today() + timedelta(days=12),
                category='entertainment',
                user_id=user.id
            ),
            Subscription(
                service_name='Adobe Creative Cloud',
                cost=54.99,
                billing_cycle='monthly',
                next_payment_date=date.today() + timedelta(days=20),
                category='software',
                user_id=user.id
            ),
            Subscription(
                service_name='GitHub Pro',
                cost=44.00,
                billing_cycle='yearly',
                next_payment_date=date.today() + timedelta(days=90),
                category='software',
                user_id=user.id
            ),
            Subscription(
                service_name='Gym Membership',
                cost=29.99,
                billing_cycle='monthly',
                next_payment_date=date.today() + timedelta(days=3),
                category='fitness',
                user_id=user.id
            ),
        ]

        db.session.add_all(subscriptions)
        db.session.commit()

        print('Database seeded successfully!')
        print(f'Demo user: demo@example.com / password123')
        print(f'Added {len(subscriptions)} sample subscriptions.')


if __name__ == '__main__':
    seed()
