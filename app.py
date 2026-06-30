import sys
import types

# 1. Defuse the Python 3.14 breaking C-API bug by mocking the broken extension module
# This tricks protobuf into safely skipping the broken C code entirely.
sys.modules['google._upb'] = types.ModuleType('google._upb')
sys.modules['google._upb._message'] = None 

import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

# 2. Now import your regular application components
from flask import Flask
from routes import routes_bp

def create_app() -> Flask:
    """Application factory building initialization modules sequence."""
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "system-dev-session-key-0129")
    
    # Register Routing Blueprints
    app.register_blueprint(routes_bp)
    
    return app

if __name__ == '__main__':
    application = create_app()
    application.run(host='0.0.0.0', port=5000, debug=True)


