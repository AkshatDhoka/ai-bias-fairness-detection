from flask import Blueprint, session
from backend.database.models import Analysis
from backend.utils.helpers import api_response

history_bp = Blueprint('history', __name__, url_prefix='/api/history')

@history_bp.route('', methods=['GET'])
def get_user_history():
    """Retrieve historical analyses for logged-in user."""
    user_id = session.get('user_id')
    if not user_id:
        return api_response(success=False, message="Unauthorized access. Please log in.", status_code=401)

    analyses = Analysis.query.filter_by(userId=user_id).order_by(Analysis.dateTime.desc()).all()
    return api_response(
        success=True,
        message="Analysis history retrieved.",
        data={'history': [a.to_dict() for a in analyses]},
        status_code=200
    )
