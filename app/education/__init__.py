from flask import Blueprint

education_bp = Blueprint('education', __name__, template_folder='../templates/education')

from app.education import routes
