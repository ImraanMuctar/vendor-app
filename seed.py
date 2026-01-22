from app import create_app
from models import db, Region, Vendor

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    uk = Region(name="UK")
    usa = Region(name="USA")
    eu = Region(name="EU")
    db.session.add_all([uk, usa, eu])
    db.session.commit()

    vendors = [
        Vendor(name="Worldwideking", region_id=uk.id, active=True, bot_link="https://t.me/Worldwideking"),
        Vendor(name="UkPablo Shop", region_id=uk.id, active=True, bot_link="https://t.me/UkPabloShop"),
        Vendor(name="Harrod Shop", region_id=uk.id, active=True, bot_link="https://t.me/HarrodShop"),
    ]
    db.session.add_all(vendors)
    db.session.commit()

print("Seeded database!")
