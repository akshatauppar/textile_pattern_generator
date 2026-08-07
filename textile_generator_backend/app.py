from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    # Run with socketio
    socketio.run(app, debug=True, host='0.0.0.0', port=8000, use_reloader=False, allow_unsafe_werkzeug=True)

