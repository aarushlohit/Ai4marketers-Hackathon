"""Custom application exceptions."""


class EntityNotFoundError(Exception):
    """Raised when a requested entity does not exist."""
    def __init__(self, entity: str, id: str):
        super().__init__(f"{entity} with id '{id}' not found")
        self.entity = entity
        self.id = id


class DuplicateEntityError(Exception):
    """Raised when creating an entity that already exists."""
    def __init__(self, entity: str, field: str, value: str):
        super().__init__(f"{entity} with {field}='{value}' already exists")


class AuthenticationError(Exception):
    """Raised when credentials are invalid."""


class AuthorizationError(Exception):
    """Raised when a user lacks the required permissions."""


class ValidationError(Exception):
    """Raised when business rule validation fails."""
    def __init__(self, message: str, field: str | None = None):
        super().__init__(message)
        self.field = field


class IntegrationError(Exception):
    """Raised when an external CRM integration fails."""
    def __init__(self, crm_type: str, message: str):
        super().__init__(f"{crm_type} integration error: {message}")
        self.crm_type = crm_type
