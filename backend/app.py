"""Main Flask application with WebSocket support."""

from flask import Flask, render_template, jsonify
from flask_cors import CORS
import socketio

from config import Config

# Initialize Flask app
app = Flask(__name__, template_folder="../player_web/templates", static_folder="../player_web/static")
app.config.from_object(Config)

# Enable CORS
CORS(app, origins=Config.CORS_ORIGINS)

# Initialize SocketIO for WebSocket support
sio = socketio.Server(
    async_mode='threading',
    cors_allowed_origins=Config.CORS_ORIGINS,
    logger=True,
    engineio_logger=True
)
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

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

# ============================================================================
# WEBSOCKET EVENTS
# ============================================================================

@sio.event
def connect(sid, environ):
    """Handle client connection."""
    print(f"Client {sid} connected")
    sio.emit("response", {"data": "Connected to server"}, to=sid)

@sio.event
def disconnect(sid):
    """Handle client disconnection."""
    print(f"Client {sid} disconnected")

@sio.event
def echo(sid, data):
    """Echo test - simple echo-back for testing."""
    print(f"Received message from {sid}: {data}")
    sio.emit("response", {"data": data}, to=sid)

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
