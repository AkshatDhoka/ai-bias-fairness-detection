from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from backend.database.db import db

def utc_now():
    return datetime.now(timezone.utc)

class User(db.Model):
    """User entity representing system users and administrators."""
    __tablename__ = 'users'

    userId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    passwordHash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='USER')
    createdAt = db.Column(db.DateTime, default=utc_now, nullable=False)
    lastLogin = db.Column(db.DateTime, nullable=True)


    # Relationships
    analyses = db.relationship('Analysis', backref='user', lazy=True, cascade='all, delete-orphan')
    history = db.relationship('AnalysisHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    reports = db.relationship('Report', backref='user', lazy=True, cascade='all, delete-orphan')
    preferences = db.relationship('UserPreference', backref='user', uselist=False, cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True)

    def set_password(self, password):
        """Securely hash and set user password using Werkzeug pbkdf2:sha256."""
        self.passwordHash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password against stored password hash."""
        return check_password_hash(self.passwordHash, password)

    def to_dict(self):
        """Return dict representation excluding sensitive data."""
        return {
            'userId': self.userId,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'createdAt': self.createdAt.isoformat() if self.createdAt else None,
            'lastLogin': self.lastLogin.isoformat() if self.lastLogin else None
        }


class Analysis(db.Model):
    """Analysis entity representing text submissions and overall results."""
    __tablename__ = 'analyses'

    analysisId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.userId'), nullable=False)
    inputText = db.Column(db.Text, nullable=False)
    dateTime = db.Column(db.DateTime, default=utc_now, nullable=False)
    language = db.Column(db.String(10), nullable=False, default='en')
    fairnessScore = db.Column(db.Integer, nullable=True)
    overallSeverity = db.Column(db.String(20), nullable=True)
    suggestion = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='COMPLETED')


    # Relationships
    biases = db.relationship('Bias', backref='analysis', lazy=True, cascade='all, delete-orphan')
    reports = db.relationship('Report', backref='analysis', lazy=True, cascade='all, delete-orphan')
    history_entries = db.relationship('AnalysisHistory', backref='analysis', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'analysisId': self.analysisId,
            'userId': self.userId,
            'inputText': self.inputText,
            'dateTime': self.dateTime.isoformat() if self.dateTime else None,
            'language': self.language,
            'fairnessScore': self.fairnessScore,
            'overallSeverity': self.overallSeverity,
            'suggestion': self.suggestion,
            'status': self.status,
            'biases': [bias.to_dict() for bias in self.biases]
        }


class Bias(db.Model):
    """Bias entity representing specific detected bias findings within an analysis."""
    __tablename__ = 'biases'

    biasId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    analysisId = db.Column(db.Integer, db.ForeignKey('analyses.analysisId'), nullable=False)
    biasType = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    severity = db.Column(db.String(20), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    explanation = db.Column(db.Text, nullable=True)
    example = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'biasId': self.biasId,
            'analysisId': self.analysisId,
            'biasType': self.biasType,
            'category': self.category,
            'description': self.description,
            'severity': self.severity,
            'confidence': round(self.confidence, 4) if self.confidence else 0.0,
            'explanation': self.explanation,
            'example': self.example
        }


class AnalysisHistory(db.Model):
    """AnalysisHistory entity tracking user interactions with analysis history."""
    __tablename__ = 'analysis_histories'

    historyId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.userId'), nullable=False)
    analysisId = db.Column(db.Integer, db.ForeignKey('analyses.analysisId'), nullable=False)
    viewedAt = db.Column(db.DateTime, default=utc_now, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'historyId': self.historyId,
            'userId': self.userId,
            'analysisId': self.analysisId,
            'viewedAt': self.viewedAt.isoformat() if self.viewedAt else None,
            'notes': self.notes
        }


class Report(db.Model):
    """Report entity representing generated PDF export artifacts."""
    __tablename__ = 'reports'

    reportId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    analysisId = db.Column(db.Integer, db.ForeignKey('analyses.analysisId'), nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey('users.userId'), nullable=False)
    generatedDate = db.Column(db.DateTime, default=utc_now, nullable=False)
    summary = db.Column(db.Text, nullable=True)
    filePath = db.Column(db.String(255), nullable=True)
    format = db.Column(db.String(10), nullable=False, default='PDF')

    def to_dict(self):
        return {
            'reportId': self.reportId,
            'analysisId': self.analysisId,
            'userId': self.userId,
            'generatedDate': self.generatedDate.isoformat() if self.generatedDate else None,
            'summary': self.summary,
            'filePath': self.filePath,
            'format': self.format
        }


class UserPreference(db.Model):
    """UserPreference entity holding UI and system options for users."""
    __tablename__ = 'user_preferences'

    prefId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.userId'), unique=True, nullable=False)
    theme = db.Column(db.String(20), nullable=False, default='dark')
    notificationEmail = db.Column(db.String(120), nullable=True)
    language = db.Column(db.String(10), nullable=False, default='en')

    def to_dict(self):
        return {
            'prefId': self.prefId,
            'userId': self.userId,
            'theme': self.theme,
            'notificationEmail': self.notificationEmail,
            'language': self.language
        }


class AuditLog(db.Model):
    """AuditLog entity recording security and administrative actions."""
    __tablename__ = 'audit_logs'

    logId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.userId'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    performedAt = db.Column(db.DateTime, default=utc_now, nullable=False)
    details = db.Column(db.Text, nullable=True)
    ipAddress = db.Column(db.String(45), nullable=True)


    def to_dict(self):
        return {
            'logId': self.logId,
            'userId': self.userId,
            'action': self.action,
            'performedAt': self.performedAt.isoformat() if self.performedAt else None,
            'details': self.details,
            'ipAddress': self.ipAddress
        }


class NLPModel(db.Model):
    """NLPModel entity documenting loaded pretrained/hybrid bias detection models."""
    __tablename__ = 'nlp_models'

    modelId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    modelName = db.Column(db.String(100), nullable=False)
    modelVersion = db.Column(db.String(50), nullable=False)
    accuracy = db.Column(db.Float, nullable=True)
    languageSupported = db.Column(db.String(50), nullable=False, default='en')
    description = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'modelId': self.modelId,
            'modelName': self.modelName,
            'modelVersion': self.modelVersion,
            'accuracy': self.accuracy,
            'languageSupported': self.languageSupported,
            'description': self.description
        }
