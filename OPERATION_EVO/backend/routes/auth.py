from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from controllers.auth_controller import authenticate_user


auth_bp = Blueprint("auth", __name__)


def _dashboard_url(user):
    """Return the correct landing page for the authenticated role."""
    return url_for("admin_dashboard" if user.role == "admin" else "user_dashboard")


@auth_bp.route("/", methods=["GET"])
def index():
    if current_user.is_authenticated:
        return redirect(_dashboard_url(current_user))
    return redirect(url_for("auth.login_page"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login_page():
    if current_user.is_authenticated:
        return redirect(_dashboard_url(current_user))

    error = None
    if request.method == "POST":
        payload = request.get_json(silent=True) or {} if request.is_json else request.form
        user = authenticate_user(payload.get("email"), payload.get("password"))
        if user is None:
            error = "Email ou mot de passe incorrect."
            if request.is_json:
                return jsonify({"error": error}), 401
        else:
            login_user(user, remember=False)
            destination = _dashboard_url(user)

            # Honour a safe next URL only when it matches the user's role.
            next_url = request.args.get("next")
            if next_url and next_url.startswith("/") and not next_url.startswith("//"):
                if user.role == "admin" or not next_url.startswith("/admin"):
                    destination = next_url

            if request.is_json:
                return jsonify(
                    {
                        "message": "login successful",
                        "user": user.to_dict(),
                        "redirect_url": destination,
                    }
                )
            return redirect(destination)

    return render_template("login.html", error=error)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout_route():
    logout_user()
    if request.is_json or request.path.startswith("/api/"):
        return jsonify({"message": "logout successful"})
    return redirect(url_for("auth.login_page"))


@auth_bp.route("/api/auth/me", methods=["GET"])
@login_required
def current_user_route():
    return jsonify(current_user.to_dict())
