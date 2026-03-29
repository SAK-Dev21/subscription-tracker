from app.extensions import db, bcrypt
from flask_login import UserMixin
from datetime import datetime, date


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    monthly_budget = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    subscriptions = db.relationship(
        'Subscription', back_populates='owner', lazy=True, cascade='all, delete-orphan'
    )

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_name = db.Column(db.String(100), nullable=False)
    cost = db.Column(db.Float, nullable=False)
    billing_cycle = db.Column(db.String(20), nullable=False)  # 'monthly', 'weekly', 'yearly'
    category = db.Column(db.String(50), nullable=False)  # 'entertainment', 'food', 'software', 'fitness', 'utilities', 'other'
    next_payment_date = db.Column(db.Date, nullable=True)
    start_date = db.Column(db.Date, default=date.today)
    is_active = db.Column(db.Boolean, default=True)
    cancellation_url = db.Column(db.String(500), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    owner = db.relationship('User', back_populates='subscriptions')

    @property
    def monthly_cost(self):
        if self.billing_cycle == 'weekly':
            return self.cost * 4.33
        elif self.billing_cycle == 'yearly':
            return self.cost / 12
        return self.cost

    def __repr__(self):
        return f'<Subscription {self.service_name}>'


class CancellationGuide(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))           # entertainment/food/software/fitness/utilities/other
    cost_display = db.Column(db.String(50))        # e.g. '£10.99/month'
    how_to_cancel = db.Column(db.Text, nullable=False)
    cancellation_url = db.Column(db.String(500), nullable=True)
    difficulty = db.Column(db.String(20))          # 'easy', 'medium', 'hard'
    tips = db.Column(db.Text, nullable=True)
    dark_pattern_warning = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<CancellationGuide {self.service_name}>'


class DarkPatternCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    dark_patterns = db.relationship('DarkPattern', back_populates='category_rel', lazy=True)

    def __repr__(self):
        return f'<DarkPatternCategory {self.name}>'


class CognitiveBias(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    dark_patterns = db.relationship('DarkPattern', back_populates='bias_rel', lazy=True)

    def __repr__(self):
        return f'<CognitiveBias {self.name}>'


class DarkPattern(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('dark_pattern_category.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    real_example = db.Column(db.Text, nullable=False)
    how_to_spot = db.Column(db.Text, nullable=False)
    how_to_protect = db.Column(db.Text, nullable=False)
    cognitive_bias_id = db.Column(db.Integer, db.ForeignKey('cognitive_bias.id'), nullable=True)
    image_filename = db.Column(db.String(200), nullable=True)
    source_citation = db.Column(db.Text, nullable=False)
    category_rel = db.relationship('DarkPatternCategory', back_populates='dark_patterns')
    bias_rel = db.relationship('CognitiveBias', back_populates='dark_patterns')

    def __repr__(self):
        return f'<DarkPattern {self.name}>'
