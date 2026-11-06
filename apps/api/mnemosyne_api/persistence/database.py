from sqlalchemy import create_engine

from mnemosyne_api.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
