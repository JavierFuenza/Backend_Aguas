
from .database import engine, Base
from .models import ObrasMedicion

def create_tables():
    Base.metadata.create_all(bind=engine)