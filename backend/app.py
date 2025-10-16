from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import redis
import os
import json
from datetime import datetime
from config import Config

app = Flask(**name**)
app.config.from_object(Config)
CORS(app)

# Database connection

def get_db_connection():
conn = psycopg2.connect(app.config[‘DATABASE_URL’])
return conn

# Redis connection

try:
redis_client = redis.from_url(app.config[‘REDIS_URL’], decode_responses=True)
except Exception as e:
print(f”Redis connection error: {e}”)
redis_client = None

# Initialize database

def init_db():
conn = get_db_connection()
cur = conn.cursor()
cur.execute(’’’
CREATE TABLE IF NOT EXISTS tasks (
id SERIAL PRIMARY KEY,
title VARCHAR(255) NOT NULL,
description TEXT,
completed BOOLEAN DEFAULT FALSE,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
‘’’)
conn.commit()
cur.close()
conn.close()

# Security headers middleware

@app.after_request
def add_security_headers(response):
response.headers[‘X-Content-Type-Options’] = ‘nosniff’
response.headers[‘X-Frame-Options’] = ‘DENY’
response.headers[‘X-XSS-Protection’] = ‘1; mode=block’
response.headers[‘Strict-Transport-Security’] = ‘max-age=31536000; includeSubDomains’
response.headers[‘Content-Security-Policy’] = “default-src ‘self’”
return response

# Health check endpoint

@app.route(’/api/health’, methods=[‘GET’])
def health_check():
health_status = {
‘status’: ‘healthy’,
‘timestamp’: datetime.now().isoformat(),
‘service’: ‘backend-api’
}

```
# Check database connection
try:
    conn = get_db_connection()
    conn.close()
    health_status['database'] = 'connected'
except Exception as e:
    health_status['database'] = 'disconnected'
    health_status['status'] = 'unhealthy'

# Check Redis connection
if redis_client:
    try:
        redis_client.ping()
        health_status['redis'] = 'connected'
    except Exception as e:
        health_status['redis'] = 'disconnected'
else:
    health_status['redis'] = 'not_configured'

status_code = 200 if health_status['status'] == 'healthy' else 503
return jsonify(health_status), status_code
```

# Get all tasks

@app.route(’/api/tasks’, methods=[‘GET’])
def get_tasks():
cache_key = ‘all_tasks’

```
# Try to get from cache
if redis_client:
    try:
        cached_tasks = redis_client.get(cache_key)
        if cached_tasks:
            return jsonify(json.loads(cached_tasks)), 200
    except Exception as e:
        print(f"Redis error: {e}")

# Get from database
conn = get_db_connection()
cur = conn.cursor(cursor_factory=RealDictCursor)
cur.execute('SELECT * FROM tasks ORDER BY created_at DESC')
tasks = cur.fetchall()
cur.close()
conn.close()

# Convert datetime objects to strings
tasks_list = []
for task in tasks:
    task_dict = dict(task)
    task_dict['created_at'] = task_dict['created_at'].isoformat() if task_dict['created_at'] else None
    task_dict['updated_at'] = task_dict['updated_at'].isoformat() if task_dict['updated_at'] else None
    tasks_list.append(task_dict)

# Cache the result
if redis_client:
    try:
        redis_client.setex(cache_key, 60, json.dumps(tasks_list))
    except Exception as e:
        print(f"Redis error: {e}")

return jsonify(tasks_list), 200
```

# Get single task

@app.route(’/api/tasks/<int:task_id>’, methods=[‘GET’])
def get_task(task_id):
conn = get_db_connection()
cur = conn.cursor(cursor_factory=RealDictCursor)
cur.execute(‘SELECT * FROM tasks WHERE id = %s’, (task_id,))
task = cur.fetchone()
cur.close()
conn.close()

```
if task:
    task_dict = dict(task)
    task_dict['created_at'] = task_dict['created_at'].isoformat() if task_dict['created_at'] else None
    task_dict['updated_at'] = task_dict['updated_at'].isoformat() if task_dict['updated_at'] else None
    return jsonify(task_dict), 200
else:
    return jsonify({'error': 'Task not found'}), 404
```

# Create new task

@app.route(’/api/tasks’, methods=[‘POST’])
def create_task():
data = request.get_json()

```
if not data or 'title' not in data:
    return jsonify({'error': 'Title is required'}), 400

title = data['title']
description = data.get('description', '')

conn = get_db_connection()
cur = conn.cursor(cursor_factory=RealDictCursor)
cur.execute(
    'INSERT INTO tasks (title, description) VALUES (%s, %s) RETURNING *',
    (title, description)
)
new_task = cur.fetchone()
conn.commit()
cur.close()
conn.close()

# Invalidate cache
if redis_client:
    try:
        redis_client.delete('all_tasks')
    except Exception as e:
        print(f"Redis error: {e}")

task_dict = dict(new_task)
task_dict['created_at'] = task_dict['created_at'].isoformat() if task_dict['created_at'] else None
task_dict['updated_at'] = task_dict['updated_at'].isoformat() if task_dict['updated_at'] else None

return jsonify(task_dict), 201
```

# Update task

@app.route(’/api/tasks/<int:task_id>’, methods=[‘PUT’])
def update_task(task_id):
data = request.get_json()

```
conn = get_db_connection()
cur = conn.cursor(cursor_factory=RealDictCursor)

# Check if task exists
cur.execute('SELECT * FROM tasks WHERE id = %s', (task_id,))
task = cur.fetchone()

if not task:
    cur.close()
    conn.close()
    return jsonify({'error': 'Task not found'}), 404

# Update task
title = data.get('title', task['title'])
description = data.get('description', task['description'])
completed = data.get('completed', task['completed'])

cur.execute(
    '''UPDATE tasks 
       SET title = %s, description = %s, completed = %s, updated_at = CURRENT_TIMESTAMP 
       WHERE id = %s 
       RETURNING *''',
    (title, description, completed, task_id)
)
updated_task = cur.fetchone()
conn.commit()
cur.close()
conn.close()

# Invalidate cache
if redis_client:
    try:
        redis_client.delete('all_tasks')
    except Exception as e:
        print(f"Redis error: {e}")

task_dict = dict(updated_task)
task_dict['created_at'] = task_dict['created_at'].isoformat() if task_dict['created_at'] else None
task_dict['updated_at'] = task_dict['updated_at'].isoformat() if task_dict['updated_at'] else None

return jsonify(task_dict), 200
```

# Delete task

@app.route(’/api/tasks/<int:task_id>’, methods=[‘DELETE’])
def delete_task(task_id):
conn = get_db_connection()
cur = conn.cursor()
cur.execute(‘DELETE FROM tasks WHERE id = %s RETURNING id’, (task_id,))
deleted = cur.fetchone()
conn.commit()
cur.close()
conn.close()

```
if deleted:
    # Invalidate cache
    if redis_client:
        try:
            redis_client.delete('all_tasks')
        except Exception as e:
            print(f"Redis error: {e}")
    
    return jsonify({'message': 'Task deleted successfully'}), 200
else:
    return jsonify({'error': 'Task not found'}), 404
```

if **name** == ‘**main**’:
init_db()
app.run(host=‘0.0.0.0’, port=5000, debug=app.config[‘DEBUG’])
