from flask import Flask, jsonify, request
import psycopg2
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import os

# ... (rest of the imports)

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'database': 'sensor_db',
    'user': 'postgres',
    'password': os.environ.get('DB_PASSWORD', 'password'),
    'port': '5432'
}

def get_db_connection():
    """Get database connection"""
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'sensor-data-api',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/data/latest')
def get_latest_data():
    """Get latest sensor readings"""
    try:
        limit = request.args.get('limit', 100, type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT sensor_id, temperature, humidity, pressure, location, timestamp, created_at
            FROM sensor_data
            ORDER BY created_at DESC
            LIMIT %s
        """
        
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        data = []
        for row in rows:
            data.append({
                'sensor_id': row[0],
                'temperature': row[1],
                'humidity': row[2],
                'pressure': row[3],
                'location': row[4],
                'timestamp': row[5].isoformat() if row[5] else None,
                'created_at': row[6].isoformat() if row[6] else None
            })
        
        return jsonify({
            'data': data,
            'count': len(data),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error fetching latest data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/data/stats')
def get_stats():
    """Get aggregated statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT sensor_id) as unique_sensors,
                AVG(temperature) as avg_temperature,
                MIN(temperature) as min_temperature,
                MAX(temperature) as max_temperature,
                AVG(humidity) as avg_humidity,
                MIN(humidity) as min_humidity,
                MAX(humidity) as max_humidity
            FROM sensor_data
            WHERE created_at >= %s
        """
        
        # Stats for last 24 hours
        since = datetime.now() - timedelta(hours=24)
        cursor.execute(query, (since,))
        row = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        stats = {
            'total_records': row[0] if row[0] else 0,
            'unique_sensors': row[1] if row[1] else 0,
            'temperature': {
                'average': round(float(row[2]), 2) if row[2] else 0,
                'minimum': float(row[3]) if row[3] else 0,
                'maximum': float(row[4]) if row[4] else 0
            },
            'humidity': {
                'average': round(float(row[5]), 2) if row[5] else 0,
                'minimum': float(row[6]) if row[6] else 0,
                'maximum': float(row[7]) if row[7] else 0
            },
            'period': '24 hours',
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/data/by-sensor/<sensor_id>')
def get_sensor_data(sensor_id):
    """Get data for a specific sensor"""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT temperature, humidity, pressure, location, timestamp, created_at
            FROM sensor_data
            WHERE sensor_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        
        cursor.execute(query, (sensor_id, limit))
        rows = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        data = []
        for row in rows:
            data.append({
                'temperature': row[0],
                'humidity': row[1],
                'pressure': row[2],
                'location': row[3],
                'timestamp': row[4].isoformat() if row[4] else None,
                'created_at': row[5].isoformat() if row[5] else None
            })
        
        return jsonify({
            'sensor_id': sensor_id,
            'data': data,
            'count': len(data)
        })
        
    except Exception as e:
        logger.error(f"Error fetching sensor data: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)