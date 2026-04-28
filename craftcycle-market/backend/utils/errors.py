"""
craftcycle/backend/app/utils/errors.py
────────────────────────────────────────
Global error handlers — every exception returns clean JSON.
"""
from flask import jsonify


def register_error_handlers(app):

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify(error="Bad request", message=str(e)), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify(error="Unauthorized", message="Authentication required."), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify(error="Forbidden", message="You don't have permission."), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify(error="Not found", message="Resource not found."), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify(error="Method not allowed"), 405

    @app.errorhandler(409)
    def conflict(e):
        return jsonify(error="Conflict", message=str(e)), 409

    @app.errorhandler(422)
    def unprocessable(e):
        return jsonify(error="Validation error", message=str(e)), 422

    @app.errorhandler(429)
    def too_many_requests(e):
        return jsonify(error="Too many requests", message="Please slow down."), 429

    @app.errorhandler(500)
    def internal_error(e):
        # Reveal actual error for debugging (remove in final production)
        return jsonify(error="Internal server error", message=str(e)), 500
