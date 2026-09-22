from flask import Blueprint, request, session
from backend.utils.validators import validate_analysis_input
from backend.utils.helpers import api_response

analysis_bp = Blueprint('analysis', __name__, url_prefix='/api/analyze')

@analysis_bp.route('', methods=['POST'])
def analyze_text():
    """Text analysis API endpoint (Foundation placeholder)."""
    user_id = session.get('user_id')
    if not user_id:
        return api_response(success=False, message="Unauthorized access. Please log in.", status_code=401)

    data = request.get_json(silent=True) or {}
    text = data.get('text', '')
    language = data.get('language', 'en')

    is_valid, err_msg = validate_analysis_input(text, language=language)
    if not is_valid:
        return api_response(success=False, message=err_msg, status_code=400)

    # Foundation placeholder: NLP Engine will be integrated in Phase 5
    return api_response(
        success=True,
        message="Text input validated successfully. NLP engine integration pending Phase 5.",
        data={
            'status': 'PENDING_NLP_INTEGRATION',
            'validated_text_length': len(text),
            'language': language
        },
        status_code=200
    )


@analysis_bp.route('/upload', methods=['POST'])
def upload_file():
    """Text file upload endpoint for analysis (Foundation placeholder)."""
    user_id = session.get('user_id')
    if not user_id:
        return api_response(success=False, message="Unauthorized access. Please log in.", status_code=401)

    if 'file' not in request.files:
        return api_response(success=False, message="No file uploaded.", status_code=400)

    file = request.files['file']
    if not file or file.filename == '':
        return api_response(success=False, message="No file selected.", status_code=400)

    if not file.filename.endswith('.txt'):
        return api_response(success=False, message="Invalid file format. Only .txt files are allowed.", status_code=400)

    try:
        content = file.read().decode('utf-8')
    except Exception as e:
        return api_response(success=False, message=f"Failed to read file content: {str(e)}", status_code=400)

    is_valid, err_msg = validate_analysis_input(content)
    if not is_valid:
        return api_response(success=False, message=err_msg, status_code=400)

    return api_response(
        success=True,
        message="File content extracted and validated successfully.",
        data={
            'filename': file.filename,
            'text_length': len(content),
            'status': 'PENDING_NLP_INTEGRATION'
        },
        status_code=200
    )
