"""Main Flask application with WebSocket support."""

from flask import Flask, render_template, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

from config import Config
from features.websocket_events import WebSocketEventHandler
from features.game_state import game_state_manager

# Initialize Flask app
app = Flask(__name__, template_folder="../player_web/templates", static_folder="../player_web/static")
app.config.from_object(Config)

# Enable CORS
CORS(app, origins=Config.CORS_ORIGINS)

# Initialize SocketIO for WebSocket support
sio = SocketIO(app, cors_allowed_origins=Config.CORS_ORIGINS)

# Initialize WebSocket event handlers
event_handler = WebSocketEventHandler(sio)

# ============================================================================
# ROUTES
# ============================================================================

@app.route("/")
def index():
    """Serve player web interface."""
    return render_template("index.html")

@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "message": "Backend is running"}), 200

@app.route("/api/config", methods=["GET"])
def get_config():
    """Get server configuration."""
    return jsonify({
        "grid_size": Config.DEFAULT_GRID_SIZE,
        "max_players": Config.MAX_PLAYERS_PER_GAME
    }), 200

@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Get server statistics."""
    stats = event_handler.get_event_stats()
    return jsonify(stats), 200


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print(f"Starting RPG server on {Config.HOST}:{Config.PORT}")
    print(f"Data directory: {Config.DATA_DIR}")
    sio.run(app, host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
