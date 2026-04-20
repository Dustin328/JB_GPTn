"""
Conversation summarization module.
Reduces context window usage by summarizing older messages.
"""
from models import Message, Conversation, get_db_session

def summarize_conversation(model_loader, conversation_id, keep_last_n=5):
    """
    Summarize a conversation by condensing older messages.
    
    Args:
        model_loader: The model loader instance
        conversation_id: ID of the conversation to summarize
        keep_last_n: Number of recent messages to keep unsummarized
    
    Returns:
        dict: Summary information
    """
    db = get_db_session()
    try:
        conversation = db.query(Conversation).filter_by(id=conversation_id).first()
        if not conversation:
            return {'error': 'Conversation not found'}
        
        messages = conversation.messages
        
        # If fewer than keep_last_n + 3 messages, no need to summarize
        if len(messages) <= keep_last_n + 3:
            return {'summarized': False, 'reason': 'Not enough messages'}
        
        # Get messages to summarize (all except last keep_last_n)
        messages_to_summarize = messages[:-keep_last_n]
        
        # Build conversation text
        conversation_text = "\n".join([
            f"{msg.role.upper()}: {msg.content}"
            for msg in messages_to_summarize
        ])
        
        # Generate summary using the model
        summary_prompt = f"""Summarize the following conversation concisely, preserving key information and context:

{conversation_text}

Provide a brief summary (2-3 sentences):"""
        
        try:
            summary = model_loader.generate(
                prompt=summary_prompt,
                max_tokens=150,
                temperature=0.3
            )
            
            # Update conversation summary
            if conversation.summary:
                # Append to existing summary
                conversation.summary = f"{conversation.summary}\n\n{summary}"
            else:
                conversation.summary = summary
            
            db.commit()
            
            return {
                'summarized': True,
                'summary': summary,
                'messages_summarized': len(messages_to_summarize),
                'messages_kept': keep_last_n
            }
        
        except Exception as e:
            return {'error': f'Failed to generate summary: {str(e)}'}
    
    finally:
        db.close()


def get_context_for_generation(conversation_id, max_messages=10):
    """
    Get conversation context for model generation.
    Returns summary + recent messages.
    
    Args:
        conversation_id: ID of the conversation
        max_messages: Maximum number of recent messages to include
    
    Returns:
        str: Context string for model prompt
    """
    db = get_db_session()
    try:
        conversation = db.query(Conversation).filter_by(id=conversation_id).first()
        if not conversation:
            return ""
        
        context_parts = []
        
        # Add summary if exists
        if conversation.summary:
            context_parts.append(f"Previous conversation summary:\n{conversation.summary}\n")
        
        # Add recent messages
        recent_messages = conversation.messages[-max_messages:]
        if recent_messages:
            context_parts.append("Recent conversation:")
            for msg in recent_messages:
                context_parts.append(f"{msg.role.upper()}: {msg.content}")
        
        return "\n".join(context_parts)
    
    finally:
        db.close()


def should_summarize(conversation_id, threshold=15):
    """
    Check if a conversation should be summarized.
    
    Args:
        conversation_id: ID of the conversation
        threshold: Number of messages before triggering summarization
    
    Returns:
        bool: True if should summarize
    """
    db = get_db_session()
    try:
        conversation = db.query(Conversation).filter_by(id=conversation_id).first()
        if not conversation:
            return False
        
        message_count = len(conversation.messages)
        return message_count >= threshold
    
    finally:
        db.close()


def auto_generate_title(model_loader, conversation_id):
    """
    Auto-generate a title for a conversation based on first few messages.
    
    Args:
        model_loader: The model loader instance
        conversation_id: ID of the conversation
    
    Returns:
        str: Generated title or None if failed
    """
    db = get_db_session()
    try:
        conversation = db.query(Conversation).filter_by(id=conversation_id).first()
        if not conversation or len(conversation.messages) < 2:
            return None
        
        # Don't regenerate if title was manually set
        if conversation.title != 'New Chat':
            return None
        
        # Get first few messages
        first_messages = conversation.messages[:4]
        conversation_text = "\n".join([
            f"{msg.role}: {msg.content[:100]}"  # Truncate long messages
            for msg in first_messages
        ])
        
        # Generate title
        title_prompt = f"""Based on this conversation, create a short, descriptive title (3-5 words):

{conversation_text}

Title:"""
        
        try:
            title = model_loader.generate(
                prompt=title_prompt,
                max_tokens=20,
                temperature=0.5
            ).strip()
            
            # Clean up title (remove quotes, truncate)
            title = title.replace('"', '').replace("'", '').strip()
            if len(title) > 50:
                title = title[:50] + '...'
            
            # Update conversation title
            conversation.title = title or 'New Chat'
            db.commit()
            
            return title
        
        except Exception as e:
            print(f"Failed to generate title: {e}")
            return None
    
    finally:
        db.close()
