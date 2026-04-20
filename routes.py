from flask import Blueprint, request, jsonify
from models import User, Conversation, Message, get_db_session
from auth import token_required
from datetime import datetime

routes = Blueprint('routes', __name__)

# ============================================
# Authentication Routes
# ============================================

@routes.route('/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400
    
    username = data['username'].strip()
    password = data['password']
    
    if len(username) < 3:
        return jsonify({'error': 'Username must be at least 3 characters'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    db = get_db_session()
    try:
        # Check if username already exists
        existing_user = db.query(User).filter_by(username=username).first()
        if existing_user:
            return jsonify({'error': 'Username already exists'}), 409
        
        # Create new user
        user = User(username=username)
        user.set_password(password)
        db.add(user)
        db.commit()
        
        # Generate token
        from auth import generate_token
        token = generate_token(user.id)
        
        return jsonify({
            'message': 'User created successfully',
            'token': token,
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500
    finally:
        db.close()


@routes.route('/auth/login', methods=['POST'])
def login():
    """Login a user"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400
    
    username = data['username'].strip()
    password = data['password']
    
    db = get_db_session()
    try:
        # Find user
        user = db.query(User).filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Generate token
        from auth import generate_token
        token = generate_token(user.id)
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict()
        }), 200
    
    finally:
        db.close()


# ============================================
# Conversation Routes
# ============================================

@routes.route('/conversations', methods=['GET'])
@token_required
def get_conversations(current_user):
    """Get all conversations for the current user"""
    db = get_db_session()
    try:
        conversations = db.query(Conversation)\
            .filter_by(user_id=current_user.id)\
            .order_by(Conversation.updated_at.desc())\
            .all()
        
        return jsonify({
            'conversations': [conv.to_dict() for conv in conversations]
        }), 200
    
    finally:
        db.close()


@routes.route('/conversations', methods=['POST'])
@token_required
def create_conversation(current_user):
    """Create a new conversation"""
    data = request.get_json() or {}
    title = data.get('title', 'New Chat')
    
    db = get_db_session()
    try:
        conversation = Conversation(
            user_id=current_user.id,
            title=title
        )
        db.add(conversation)
        db.commit()
        
        return jsonify({
            'message': 'Conversation created',
            'conversation': conversation.to_dict()
        }), 201
    
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Failed to create conversation: {str(e)}'}), 500
    finally:
        db.close()


@routes.route('/conversations/<int:conversation_id>', methods=['GET'])
@token_required
def get_conversation(conversation_id, current_user):
    """Get a specific conversation with all messages"""
    db = get_db_session()
    try:
        conversation = db.query(Conversation)\
            .filter_by(id=conversation_id, user_id=current_user.id)\
            .first()
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        return jsonify({
            'conversation': conversation.to_dict(include_messages=True)
        }), 200
    
    finally:
        db.close()


@routes.route('/conversations/<int:conversation_id>', methods=['DELETE'])
@token_required
def delete_conversation(conversation_id, current_user):
    """Delete a conversation"""
    db = get_db_session()
    try:
        conversation = db.query(Conversation)\
            .filter_by(id=conversation_id, user_id=current_user.id)\
            .first()
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        db.delete(conversation)
        db.commit()
        
        return jsonify({'message': 'Conversation deleted'}), 200
    
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Failed to delete conversation: {str(e)}'}), 500
    finally:
        db.close()


@routes.route('/conversations/<int:conversation_id>/title', methods=['PATCH'])
@token_required
def update_conversation_title(conversation_id, current_user):
    """Update conversation title"""
    data = request.get_json()
    
    if not data or not data.get('title'):
        return jsonify({'error': 'Title required'}), 400
    
    db = get_db_session()
    try:
        conversation = db.query(Conversation)\
            .filter_by(id=conversation_id, user_id=current_user.id)\
            .first()
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        conversation.title = data['title']
        conversation.updated_at = datetime.utcnow()
        db.commit()
        
        return jsonify({
            'message': 'Title updated',
            'conversation': conversation.to_dict()
        }), 200
    
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Failed to update title: {str(e)}'}), 500
    finally:
        db.close()
