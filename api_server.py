import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request
import json 
import datetime

app = Flask(__name__)

# Configure logging with log rotation
log_file = '/var/log/api_error.log'
max_log_size = 10 * 1024 * 1024  # 10 MB
backup_count = 5  # Number of backup log files
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

rotating_handler = RotatingFileHandler(log_file, maxBytes=max_log_size, backupCount=backup_count)
rotating_handler.setFormatter(formatter)
rotating_handler.setLevel(logging.ERROR)

app.logger.addHandler(rotating_handler)

@app.route('/v1.0/groups', methods=['GET'])
def get_groups():
    try:
        # Read the groups.json file
        with open('groups.json') as file:
            groups_data = json.load(file)

        # Check if a group name is provided in the request query parameters
        group_name = request.args.get('name')
        # Check if location_available parameter is set to true
        available = request.args.get('available')

        # If a group name is provided, filter the groups based on the name
        if group_name:
            filtered_groups = [group for group in groups_data if group['name'] == group_name]
        else:
            filtered_groups = groups_data

        # If location_available is set to true, filter the groups based on the availability of at least one location
        if available == 'true':
            filtered_groups = [group for group in filtered_groups if any(location['available'] for location in group['locations'])]

        return jsonify(filtered_groups)
    except Exception as e:
        app.logger.error(f"Error in get_groups: {str(e)}")
        return jsonify({'error': 'An error occurred while processing the request.'}), 500

@app.route('/v1.0/victims', methods=['GET'])
def get_posts():
    try:
        # Read the posts.json file
        with open('posts.json') as file:
            posts_data = json.load(file)

        # Check if a group_name is provided in the request query parameters
        group_name = request.args.get('group')
        year = request.args.get('year')
        month = request.args.get('month')

        # If a group_name is provided, filter the posts based on the group_name
        if group_name:
            filtered_posts = [post for post in posts_data if post['group_name'] == group_name]
        else:
            filtered_posts = posts_data

        # If both year and month are provided, filter the posts based on the published date
        if year and month:
            year = int(year)
            month = int(month)
            filtered_posts = [
                post for post in filtered_posts
                if datetime.datetime.strptime(post['published'], '%Y-%m-%d %H:%M:%S.%f').year == year
                and datetime.datetime.strptime(post['published'], '%Y-%m-%d %H:%M:%S.%f').month == month
            ]
        
        return jsonify(filtered_posts)
    except Exception as e:
        app.logger.error(f"Error in get_posts: {str(e)}")
        return jsonify({'error': 'An error occurred while processing the request.'}), 500


@app.route('/v1.0/stats', methods=['GET'])
def get_stats():
    try:
        # Read the stats.json file
        with open('stats.json') as file:
            stats_data = json.load(file)

        return jsonify(stats_data)
    except Exception as e:
        app.logger.error(f"Error in get_stats: {str(e)}")
        return jsonify({'error': 'An error occurred while processing the request.'}), 500



if __name__ == '__main__':
    app.run()  

