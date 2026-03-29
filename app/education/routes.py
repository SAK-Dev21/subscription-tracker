import re
from flask import render_template, abort, request, jsonify
from app.education import education_bp
from app.models import CancellationGuide, DarkPatternCategory, CognitiveBias, DarkPattern


def split_steps(text):
    """Split cancellation steps on '. ' followed by an uppercase letter only."""
    return [s.strip() for s in re.split(r'\.\s+(?=[A-Z])', text) if s.strip()]


@education_bp.route('/cancellation-guide')
def cancellation_guide():
    guides = CancellationGuide.query.order_by(CancellationGuide.service_name).all()
    steps_map = {g.id: split_steps(g.how_to_cancel) for g in guides}
    return render_template('education/cancellation_guide.html', guides=guides, steps_map=steps_map)


@education_bp.route('/cancellation-guide/<int:id>')
def cancellation_detail(id):
    guide = CancellationGuide.query.get_or_404(id)
    steps = split_steps(guide.how_to_cancel)
    return render_template('education/cancellation_detail.html', guide=guide, steps=steps)


@education_bp.route('/dark-patterns/pattern/<int:id>')
def dark_pattern_detail(id):
    pattern = DarkPattern.query.get_or_404(id)
    return render_template('education/dark_pattern_detail.html', pattern=pattern)


@education_bp.route('/dark-patterns/bias/<int:id>')
def dark_patterns_bias(id):
    bias = CognitiveBias.query.get_or_404(id)
    patterns = DarkPattern.query.filter_by(cognitive_bias_id=id).all()
    return render_template('education/dark_pattern_bias.html', bias=bias, patterns=patterns)


@education_bp.route('/dark-patterns/category/<int:id>')
def dark_patterns_category(id):
    category = DarkPatternCategory.query.get_or_404(id)
    patterns = DarkPattern.query.filter_by(category_id=id).all()
    return render_template('education/dark_pattern_category.html', category=category, patterns=patterns)


@education_bp.route('/dark-patterns/search')
def dark_patterns_search():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
    results = DarkPattern.query.filter(
        DarkPattern.name.ilike(f'%{q}%')
    ).limit(10).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'category': p.category_rel.name,
        'description': p.description[:100]
    } for p in results])


@education_bp.route('/dark-patterns')
def dark_patterns():
    categories = DarkPatternCategory.query.order_by(DarkPatternCategory.name).all()
    biases = CognitiveBias.query.order_by(CognitiveBias.name).all()
    return render_template('education/dark_patterns.html', categories=categories, biases=biases)
