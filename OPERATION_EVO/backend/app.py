import os
import sys
import threading
import time
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, send_from_directory, url_for
from flask_cors import CORS
from flask_login import LoginManager, current_user, login_required

BACKEND_ROOT = Path(__file__).resolve().parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from config import Config
from controllers.auth_controller import get_user_by_id_for_session
from database.db import init_db
from routes import auth_bp, stats_bp, tickets_bp, users_bp
from services.email_service import send_weekly_system_email

app = Flask(__name__, template_folder="templates")
app.config.from_object(Config)
CORS(app, supports_credentials=True)

login_manager = LoginManager()
login_manager.login_view = "auth.login_page"
login_manager.login_message = "Connectez-vous pour accéder à Operation EVO."
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id_for_session(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith("/api/"):
        return jsonify({"error": "authentication required"}), 401
    return redirect(url_for("auth.login_page", next=request.path))


app.register_blueprint(auth_bp)
app.register_blueprint(users_bp, url_prefix="/api/users")
app.register_blueprint(tickets_bp, url_prefix="/api/tickets")
app.register_blueprint(stats_bp, url_prefix="/api/stats")


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "authenticated": current_user.is_authenticated})


@app.route("/admin", methods=["GET"])
@login_required
def admin_dashboard():
    if str(current_user.role).lower() not in {"admin", "manager"}:
        return redirect(url_for("user_dashboard"))
    return render_template("admin_dashboard.html", current_user_data=current_user.to_dict())


@app.route("/dashboard", methods=["GET"])
@login_required
def user_dashboard():
    if str(current_user.role).lower() in {"admin", "manager"}:
        return redirect(url_for("admin_dashboard"))
    return render_template("user_dashboard.html", current_user_data=current_user.to_dict())


@app.route("/images.png")
def serve_dashboard_image():
    return send_from_directory(app.template_folder, "images.png", mimetype="image/png")


@app.route("/api/system-email/weekly", methods=["POST"])
@login_required
def trigger_weekly_email():
    if current_user.role != "admin":
        return jsonify({"error": "administrator access required"}), 403
    payload = request.get_json(silent=True) or {}
    recipient = payload.get("recipient")
    result = send_weekly_system_email(recipient=recipient)
    status = 502 if result.get("status") == "error" else 200
    return jsonify(result), status


def weekly_email_worker():
    while True:
        time.sleep(604800)
        send_weekly_system_email()


init_db(force=False)

if os.getenv("FLASK_ENV") != "test" and os.getenv("DISABLE_EMAIL_WORKER", "true").lower() != "true":
    thread = threading.Thread(target=weekly_email_worker, daemon=True)
    thread.start()

if __name__ == "__main__":
    app.run(
        debug=os.getenv("FLASK_DEBUG", "true").lower() == "true",
        host=os.getenv("FLASK_HOST", "127.0.0.1"),
        port=int(os.getenv("FLASK_PORT", "5000")),
    )
