from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Region(db.Model):
    __tablename__ = "regions"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)

    vendors = db.relationship("Vendor", backref="region", lazy=True)

class Vendor(db.Model):
    __tablename__ = "vendors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    active = db.Column(db.Boolean, default=True)

    region_id = db.Column(db.Integer, db.ForeignKey("regions.id"), nullable=False)

    # Telegram bot info (link-only integration)
    bot_username = db.Column(db.String(120), nullable=True)  # e.g. "Worldwideking"
    bot_link = db.Column(db.String(255), nullable=True)      # e.g. "https://t.me/Worldwideking"
