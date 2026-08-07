from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
import logging

logger = logging.getLogger(__name__)

# WebSocket with threading mode - supports both polling and websocket
socketio = SocketIO(
    cors_allowed_origins="*", 
    async_mode="threading",
    logger=True,
    engineio_logger=False,
    ping_timeout=60,
    ping_interval=25
)

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'data': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('join_generation')
def on_join(data):
    """Join a room for generation updates"""
    generation_id = data.get('generation_id')
    join_room(f'generation_{generation_id}')
    emit('joined', {'generation_id': generation_id})
    logger.info(f"Client joined generation room: {generation_id}")

@socketio.on('leave_generation')
def on_leave(data):
    """Leave a generation room"""
    generation_id = data.get('generation_id')
    leave_room(f'generation_{generation_id}')
    emit('left', {'generation_id': generation_id})
    logger.info(f"Client left generation room: {generation_id}")

def emit_generation_update(generation_id, status, data=None):
    """Emit real-time generation status update"""
    socketio.emit('generation_update', {
        'generation_id': generation_id,
        'status': status,
        'data': data or {}
    }, room=f'generation_{generation_id}')
