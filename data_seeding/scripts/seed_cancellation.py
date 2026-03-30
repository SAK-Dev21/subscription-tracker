import os
import csv
from app import create_app
from app.extensions import db
from app.models import CancellationGuide

app = create_app()

with app.app_context():
    db.session.query(CancellationGuide).delete()

    count = 0
    
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'cancellation_data.csv')
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            guide = CancellationGuide(
                service_name=row['service_name'],
                category=row['category'] or None,
                cost_display=row['cost_display'] or None,
                how_to_cancel=row['how_to_cancel'],
                cancellation_url=row['cancellation_url'] or None,
                difficulty=row['difficulty'] or None,
                tips=row['tips'] or None,
                dark_pattern_warning=row['dark_pattern_warning'] or None,
            )
            db.session.add(guide)
            count += 1

    db.session.commit()
    print(f'Loaded {count} cancellation guides.')