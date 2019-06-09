from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Catagories, Base, CatalogItems, User

engine = create_engine('sqlite:///catalogitem.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com", picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Catalog Menu for Soccer
catalog1 = Catagories(user_id=1, name="Soccer")
session.add(catalog1)
session.commit()

catalogItem2 = CatalogItems(user_id=1, title="Soccer Cleats", description="Firm ground is the classic soccer shoe with cleats/studs designed to provide traction and stability on most natural grass, outdoor soccer fields.", catagories=catalog1)
session.add(catalogItem2)
session.commit()

catalogItem1 = CatalogItems(user_id=1, title="Soccer Boots", description="Football boots, called cleats or soccer shoes in North America, are an item of footwear worn when playing football. Those designed for grass pitches have studs on the outsole to aid grip", catagories=catalog1)

session.add(catalogItem1)
session.commit()

catalogItem3 = CatalogItems(user_id=1, title="Shin Guards", description="Shin guards are one of the suggested preventive methods. Their main function is to protect the soft tissues and bones in the lower extremities from external impact.", catagories=catalog1)

session.add(catalogItem3)
session.commit()

catalogItem4 = CatalogItems(user_id=1, title="Soccer Uniforms", description="To be worn while players represent there country or team.", catagories=catalog1)

session.add(catalogItem4)
session.commit()

# Catalog Menu for Basketball

catalog2 = Catagories(user_id=1, name="Basketball")

session.add(catalog2)
session.commit()

catalogItem1 = CatalogItems(user_id=1, title="Basketball Ball", description="A basketball is a spherical ball used in basketball games.", catagories=catalog2)

session.add(catalogItem1)
session.commit()

catalogItem2 = CatalogItems(user_id=1, title="Basketball Shoes", description="Basketball shoes are specifically designed for the intensity of the game.", catagories=catalog2)

session.add(catalogItem2)
session.commit()

catalogItem3 = CatalogItems(user_id=1, title="Basketball Unifrom", description="To be worn while players represent there country or team.", catagories=catalog2)

session.add(catalogItem3)
session.commit()

# Catalog Menu for Baseball

catalog3 = Catagories(user_id=1, name="Baseball")

session.add(catalog3)
session.commit()

catalogItem1 = CatalogItems(user_id=1, title="Baseball Uniform", description="To be worn while players represent there country or team.", catagories=catalog3)

session.add(catalogItem1)
session.commit()

catalogItem2 = CatalogItems(user_id=1, title="Baseball Bat", description="A baseball bat is a smooth wooden or metal club used in the sport of baseball to hit the ball after it is thrown by the pitcher.", catagories=catalog3)

session.add(catalogItem2)
session.commit()

# Catalog Menu for Frisbee

catalog4 = Catagories(user_id=1, name="Frisbee")

session.add(catalog4)
session.commit()

catalogItem1 = CatalogItems(user_id=1, title="Flying Discs", description="A frisbee is a gliding toy or sporting item that is generally plastic and roughly 8 to 10 inches in diameter with a pronounced lip.", catagories=catalog4)

session.add(catalogItem1)
session.commit()

# Catalog Menu for Snowboarding

catalog5 = Catagories(user_id=1, name="Snowboarding")

session.add(catalog5)
session.commit()

catalogItem1 = CatalogItems(user_id=1, title="Googles", description="A pair of tight-fitting eyeglasses, often tinted or having side shields, worn to protect the eyes from hazards such as wind, glare, water, or flying debris.", catagories=catalog5)

session.add(catalogItem1)
session.commit()

catalogItem2 = CatalogItems(user_id=1, title="Snowboard", description="A board resembling a short, broad ski, used for sliding downhill on snow.", catagories=catalog5)

session.add(catalogItem2)
session.commit()

# Catalog Menu for Rock Climbing

catalog6 = Catagories(user_id=1, name="Rock Climbing")

session.add(catalog6)
session.commit()

catalogItem1 = CatalogItems(user_id=1, title="Harnesses", description="A harness is a system used for connecting the rope to the climber.", catagories=catalog6)

session.add(catalogItem1)
session.commit()

catalogItem2 = CatalogItems(user_id=1, title="Belay devices", description="Belay devices are mechanical friction brake devices used to control a rope when belaying.", catagories=catalog6)

session.add(catalogItem2)
session.commit()

# Catalog Menu for Foosball

catalog7 = Catagories(user_id=1, name="Foosball")

session.add(catalog7)
session.commit()

catalogItem1 = CatalogItems(user_id=1, title="Foosball Table", description="A table game resembling soccer in which the ball is moved by manipulating rods to which small figures of players are attached.", catagories=catalog7)

session.add(catalogItem1)
session.commit()

# Catalog Menu for Skating

catalog8 = Catagories(user_id=1, name="Skating")

session.add(catalog8)
session.commit()

catalogItem1 = CatalogItems(user_id=1, title="Skating Shoes", description="A type of footwear specifically designed and manufactured for use in skateboarding.", catagories=catalog8)

session.add(catalogItem1)
session.commit()

# Catalog Menu for Hockey

catalog9 = Catagories(user_id=1, name="Hockey")

session.add(catalog9)
session.commit()

catalogItem1 = CatalogItems(user_id=1, title="Hockey Sticks", description="A long stick used to hit or direct the ball or puck.", catagories=catalog9)

session.add(catalogItem1)
session.commit()

print("added menu items!")
