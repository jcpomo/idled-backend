from app.core.config import get_settings
from app.erp_gateway.base import ERPGateway
from app.erp_gateway.mock import MockERPGateway

def get_erp_gateway() -> ERPGateway:
    return MockERPGateway(base_url=get_settings().erp_base_url)
