import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import db, Region, Vendor

def create_app():
    app = Flask(__name__)

    # SQLite by default. Later, replace with Postgres using env var DATABASE_URL
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///app.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

    db.init_app(app)

    with app.app_context():
        db.create_all()

    # ---- ADMIN PAGES ----
    @app.get("/admin/regions")
    def admin_regions():
        regions = Region.query.order_by(Region.name.asc()).all()
        return render_template("admin_regions.html", regions=regions)

    @app.post("/admin/regions")
    def admin_regions_create():
        name = request.form.get("name", "").strip()
        if name:
            existing = Region.query.filter_by(name=name).first()
            if not existing:
                db.session.add(Region(name=name))
                db.session.commit()
        return redirect(url_for("admin_regions"))

    @app.get("/admin/vendors")
    def admin_vendors():
        vendors = Vendor.query.join(Region).order_by(Region.name.asc(), Vendor.name.asc()).all()
        regions = Region.query.order_by(Region.name.asc()).all()
        return render_template("admin_vendors.html", vendors=vendors, regions=regions)

    @app.get("/admin/vendors/new")
    def admin_vendor_new():
        regions = Region.query.order_by(Region.name.asc()).all()
        return render_template("admin_vendor_form.html", regions=regions, vendor=None)

    @app.post("/admin/vendors/new")
    def admin_vendor_create():
        form = request.form
        vendor = Vendor(
            name=form.get("name", "").strip(),
            description=form.get("description", "").strip() or None,
            active=(form.get("active") == "on"),
            region_id=int(form.get("region_id")),
            bot_username=form.get("bot_username", "").strip() or None,
            bot_link=form.get("bot_link", "").strip() or None,
        )
        db.session.add(vendor)
        db.session.commit()
        return redirect(url_for("admin_vendors"))

    @app.get("/admin/vendors/<int:vendor_id>/edit")
    def admin_vendor_edit(vendor_id):
        vendor = Vendor.query.get_or_404(vendor_id)
        regions = Region.query.order_by(Region.name.asc()).all()
        return render_template("admin_vendor_form.html", regions=regions, vendor=vendor)

    @app.post("/admin/vendors/<int:vendor_id>/edit")
    def admin_vendor_update(vendor_id):
        vendor = Vendor.query.get_or_404(vendor_id)
        form = request.form
        vendor.name = form.get("name", "").strip()
        vendor.description = form.get("description", "").strip() or None
        vendor.active = (form.get("active") == "on")
        vendor.region_id = int(form.get("region_id"))
        vendor.bot_username = form.get("bot_username", "").strip() or None
        vendor.bot_link = form.get("bot_link", "").strip() or None
        db.session.commit()
        return redirect(url_for("admin_vendors"))

    @app.post("/admin/vendors/<int:vendor_id>/delete")
    def admin_vendor_delete(vendor_id):
        vendor = Vendor.query.get_or_404(vendor_id)
        db.session.delete(vendor)
        db.session.commit()
        return redirect(url_for("admin_vendors"))

    # ---- API FOR TELEGRAM BOT ----
    @app.get("/api/regions")
    def api_regions():
        regions = Region.query.order_by(Region.name.asc()).all()
        return jsonify([{"id": r.id, "name": r.name} for r in regions])

    @app.get("/api/vendors")
    def api_vendors():
        # /api/vendors?region_id=1&page=1&page_size=8
        region_id = int(request.args.get("region_id", "0"))
        page = max(int(request.args.get("page", "1")), 1)
        page_size = max(int(request.args.get("page_size", "8")), 1)

        q = Vendor.query.filter_by(region_id=region_id, active=True).order_by(Vendor.name.asc())
        total = q.count()
        vendors = q.offset((page - 1) * page_size).limit(page_size).all()

        return jsonify({
            "total": total,
            "page": page,
            "page_size": page_size,
            "vendors": [{
                "id": v.id,
                "name": v.name,
                "description": v.description,
                "bot_username": v.bot_username,
                "bot_link": v.bot_link
            } for v in vendors]
        })

    @app.get("/")
    def home():
        return redirect(url_for("admin_regions"))

    return app

if __name__ == "__main__":
    create_app().run(debug=True)
