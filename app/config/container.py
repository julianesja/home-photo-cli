from app.config.settings import Settings
from dependency_injector import containers, providers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
class Container(containers.DeclarativeContainer):
    config = providers.Singleton(Settings)
    engine = create_engine(
        config.provided.db_url
        )
    SessionLocal = sessionmaker(bind=engine)
    session = providers.Singleton(SessionLocal)
    
    
    


