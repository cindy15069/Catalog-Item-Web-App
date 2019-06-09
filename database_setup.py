from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    # representing our table inside the database
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))
    @property
    def serialize(self):
        return {
            'name': self.name,
            'email': self.email,
            'picture': self.picture,
            'id': self.id
        }


class Catagories(Base):
    __tablename__ = 'catagories'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # Return object data in easily serializeable format
        return {
            'name': self.name,
            'id': self.id,
            'user_id': self.user_id
        }


class CatalogItems(Base):
    __tablename__ = 'catalog_item'
    title = Column(String(100), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    catagories_id = Column(Integer, ForeignKey('catagories.id'))
    catagories = relationship(Catagories)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    # We added this serialize function to be able to send JSON objects
    #  in a serializable format
    @property
    def serialize(self):
        return {
            'title': self.title,
            'description': self.description,
            'cat_id': self.id,
            'id': self.id,
        }


engine = create_engine('sqlite:///catalogitem.db')
Base.metadata.create_all(engine)
