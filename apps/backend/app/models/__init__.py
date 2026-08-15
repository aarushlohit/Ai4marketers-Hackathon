"""
Import all models here so Alembic can detect them via Base.metadata.
"""
from app.models.tenant import TenantModel  # noqa: F401
from app.models.user import UserModel  # noqa: F401
from app.models.customer import CustomerModel  # noqa: F401
from app.models.workflow import WorkflowModel  # noqa: F401
from app.models.recommendation import RecommendationModel  # noqa: F401
from app.models.feedback import FeedbackModel  # noqa: F401
from app.models.meeting import MeetingSummaryModel  # noqa: F401
