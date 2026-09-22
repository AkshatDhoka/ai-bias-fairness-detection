from flask import Blueprint, session
from backend.database.models import Report
from backend.utils.helpers import api_response

report_bp = Blueprint('reports', __name__, url_prefix='/api/reports')

@report_bp.route('', methods=['GET'])
def get_reports():
    """Retrieve list of generated reports for logged-in user."""
    user_id = session.get('user_id')
    if not user_id:
        return api_response(success=False, message="Unauthorized access. Please log in.", status_code=401)

    reports = Report.query.filter_by(userId=user_id).order_by(Report.generatedDate.desc()).all()
    return api_response(
        success=True,
        message="User reports list retrieved.",
        data={'reports': [r.to_dict() for r in reports]},
        status_code=200
    )
