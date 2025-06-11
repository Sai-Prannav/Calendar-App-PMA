"""
Session management for database operations.
"""
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

class SessionManager:
    """Manages database sessions."""
    
    def __init__(self, db_path: str = 'weather_app.db'):
        """Initialize session manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self) -> Session:
        """Get a new session.
        
        Returns:
            A new SQLAlchemy Session instance
        """
        return self.Session()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """Provide a transactional scope around a series of operations.
        
        Yields:
            Session: SQLAlchemy Session instance
            
        Example:
            with session_manager.session_scope() as session:
                session.add(some_object)
                session.commit()
        """
        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()