"""
JailbrokeGPT Flask Backend
Main application entry point
"""
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from model_loader import ModelLoader
from models import init_db, Message, Conversation, get_db_session
from auth import token_required
from routes import routes
from summarization import should_summarize, summarize_conversation, get_context_for_generation, auto_generate_title
from datetime import datetime

# Load environment variables
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIST_DIR = os.path.join(BASE_DIR, 'frontend_dist')

# Initialize Flask app
app = Flask(__name__, static_folder=FRONTEND_DIST_DIR, static_url_path='')
CORS(app)  # Enable CORS for React frontend

# Register blueprints
app.register_blueprint(routes, url_prefix='/api')

# Configuration
MODEL_REPO = os.getenv('MODEL_REPO', 'v8karlo/UNCENSORED-TinyLlama-1.1B-intermediate-step-1431k-3T-Q5_K_M-GGUF')
MODEL_FILE = os.getenv('MODEL_FILE', 'uncensored-tinyllama-1.1b-intermediate-step-1431k-3t-q5_k_m.gguf')
MAX_TOKENS = int(os.getenv('MAX_TOKENS', 512))
TEMPERATURE = float(os.getenv('TEMPERATURE', 0.7))
TOP_P = float(os.getenv('TOP_P', 0.9))
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')

# Initialize database
print("Initializing database...")
try:
    init_db()
    print("Database initialized successfully")
except Exception as e:
    print(f"Warning: Database initialization failed: {e}")
    print("Make sure MySQL is running and configured in .env")

# Initialize model loader
print("Initializing JailbrokeGPT...")
model_loader = ModelLoader(MODEL_REPO, MODEL_FILE)

# Load model on startup
try:
    model_loader.load_model()
except Exception as e:
    import traceback
    print(f"Error loading model: {e}")
    print("\nFull error details:")
    traceback.print_exc()
    print("\nServer will start but model needs to be loaded manually")


# ============================================
# Error Handlers
# ============================================

@app.errorhandler(Exception)
def handle_error(error):
    """Global error handler that returns JSON instead of HTML"""
    import traceback
    print(f"Error occurred: {error}")
    traceback.print_exc()
    
    # Check if it's a database connection error
    error_str = str(error)
    if 'MySQL' in error_str or 'database' in error_str.lower() or '2003' in error_str:
        return jsonify({
            'error': 'Database connection failed',
            'message': 'MySQL is not running. Please start MySQL or use the no-auth version.',
            'details': str(error)
        }), 503
    
    # Generic error response
    return jsonify({
        'error': 'Internal server error',
        'message': str(error)
    }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested endpoint does not exist'
    }), 404


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model_loader.model is not None
    })


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve compiled frontend files when available (for packaged app usage)."""
    if path.startswith('api') or path in {'health', 'model-info'}:
        return not_found(None)

    if os.path.isdir(FRONTEND_DIST_DIR):
        requested_file = os.path.join(FRONTEND_DIST_DIR, path)
        if path and os.path.exists(requested_file):
            return send_from_directory(FRONTEND_DIST_DIR, path)

        index_file = os.path.join(FRONTEND_DIST_DIR, 'index.html')
        if os.path.exists(index_file):
            return send_from_directory(FRONTEND_DIST_DIR, 'index.html')

    return jsonify({
        'error': 'Frontend not built',
        'message': 'Run the frontend build and place output in backend/frontend_dist'
    }), 503


@app.route('/api/chat', methods=['POST'])
@token_required
def chat(current_user):
    """
    Main chat endpoint with conversation support
    
    Expected JSON body:
    {
        "prompt": "Your message here",
        "conversation_id": 1,  # required
        "max_tokens": 512,     # optional
        "temperature": 0.7     # optional
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Missing prompt in request body'}), 400
        
        if 'conversation_id' not in data:
            return jsonify({'error': 'Missing conversation_id in request body'}), 400
        
        prompt = data['prompt']
        conversation_id = data['conversation_id']
        max_tokens = data.get('max_tokens', MAX_TOKENS)
        temperature = data.get('temperature', TEMPERATURE)
        
        db = get_db_session()
        try:
            # Verify conversation belongs to user
            conversation = db.query(Conversation)\
                .filter_by(id=conversation_id, user_id=current_user.id)\
                .first()
            
            if not conversation:
                return jsonify({'error': 'Conversation not found'}), 404
            
            # Save user message
            user_message = Message(
                conversation_id=conversation_id,
                role='user',
                content=prompt
            )
            db.add(user_message)
            db.commit()
            
            # Check if we should summarize
            if should_summarize(conversation_id):
                print(f"Summarizing conversation {conversation_id}...")
                summary_result = summarize_conversation(model_loader, conversation_id)
                print(f"Summarization result: {summary_result}")
            
            # Auto-generate title after first exchange
            if len(conversation.messages) == 2:  # After first user message and response
                auto_generate_title(model_loader, conversation_id)
            
            # Get context for generation
            context = get_context_for_generation(conversation_id, max_messages=8)
            
            # Format prompt with context
            if context:
                formatted_prompt = f"{context}\n\nUser: {prompt}\nAssistant:"
            else:
                formatted_prompt = f"User: {prompt}\nAssistant:"
            
            # Generate response
            response = model_loader.generate(
                prompt=formatted_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=TOP_P
            )
            
            # Save assistant message
            assistant_message = Message(
                conversation_id=conversation_id,
                role='assistant',
                content=response
            )
            db.add(assistant_message)
            
            # Update conversation timestamp
            conversation.updated_at = datetime.utcnow()
            db.commit()
            
            return jsonify({
                'response': response,
                'prompt': prompt,
                'conversation_id': conversation_id,
                'message_id': assistant_message.id
            })
        
        finally:
            db.close()
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/model-info', methods=['GET'])
def model_info():
    """Get information about the loaded model"""
    return jsonify({
        'model_repo': MODEL_REPO,
        'model_file': MODEL_FILE,
        'max_tokens': MAX_TOKENS,
        'temperature': TEMPERATURE,
        'top_p': TOP_P,
        'loaded': model_loader.model is not None
    })


if __name__ == '__main__':
    print("\n" + "="*50)
    print("JailbrokeGPT Backend Server")
    print("="*50)
    print(f"Running on: http://{FLASK_HOST}:{FLASK_PORT}")
    print(f"Model: {MODEL_REPO}")
    print(f"Chat endpoint: http://localhost:{FLASK_PORT}/chat")
    print("Press CTRL+C to stop the server")
    print("="*50 + "\n")
    
    app.run(
        host=FLASK_HOST,
        port=FLASK_PORT,
        debug=False,
        use_reloader=False
    )
