from flask import render_template
from app.education import education_bp


@education_bp.route('/cancellation-guide')
def cancellation_guide():
    return render_template('education/cancellation_guide.html')


@education_bp.route('/dark-patterns')
def dark_patterns():
    return render_template('education/dark_patterns.html')
