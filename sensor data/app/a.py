from flask import Flask, jsonify, send_from_directory
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from datetime import datetime
import os

app = Flask(__name__, static_folder='static')

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('2kapahada')

@app.route('/')
def home():
    return send_from_directory('static', 'tes.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/all-data', methods=['GET'])
def get_all_data():
    try:
        response = table.scan()
        data = response.get('Items', [])
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            data.extend(response.get('Items', []))
        if data:
            return jsonify(data)
        else:
            return jsonify({'message': 'No data found.'})
    except NoCredentialsError:
        return jsonify({'error': 'Credentials not available.'}), 500
    except PartialCredentialsError:
        return jsonify({'error': 'Incomplete credentials provided.'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/one', methods=['GET'])
def get_latest_data():
    try:
        response = table.scan()
        data = response.get('Items', [])
        if data:
            latest_item = max(data, key=lambda x: datetime.fromisoformat(x['time']))
            return jsonify(latest_item)
        else:
            return jsonify({'message': 'No data found.'})
    except NoCredentialsError:
        return jsonify({'error': 'Credentials not available.'}), 500
    except PartialCredentialsError:
        return jsonify({'error': 'Incomplete credentials provided.'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
