import io from 'socket.io-client';

const SOCKET_URL = import.meta.env.VITE_API_URL || 'http://localhost:6000';

class SocketService {
  constructor() {
    this.socket = null;
    this.listeners = new Map();
  }

  connect() {
    if (this.socket) return;
    
    this.socket = io(SOCKET_URL, {
      transports: ['websocket'],  // Use WebSocket only
      reconnectionDelay: 1000,
      reconnection: true,
      reconnectionAttempts: 10,
      timeout: 20000,
    });

    this.socket.on('connected', (data) => {
      console.log('Connected to WebSocket:', data);
    });

    this.socket.on('generation_update', (data) => {
      this.emit('generation_update', data);
    });

    this.socket.on('disconnect', () => {
      console.log('Disconnected from WebSocket');
    });

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
    });
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  joinGeneration(generationId) {
    if (this.socket?.connected) {
      this.socket.emit('join_generation', { generation_id: generationId });
    }
  }

  leaveGeneration(generationId) {
    if (this.socket?.connected) {
      this.socket.emit('leave_generation', { generation_id: generationId });
    }
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  emit(event, data) {
    const callbacks = this.listeners.get(event) || [];
    callbacks.forEach(cb => cb(data));
  }
}

export const socketService = new SocketService();
