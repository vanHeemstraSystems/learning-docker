import os

class Config:
“”“Application configuration”””

```
# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://dbuser:changeme@localhost:5432/taskdb')

# Redis configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://:redispass@localhost:6379/0')

# Flask configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.getenv('FLASK_ENV', 'production') == 'development'

# Security settings
JSON_SORT_KEYS = False
PROPAGATE_EXCEPTIONS = True
```
