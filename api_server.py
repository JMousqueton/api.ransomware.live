from flask import Flask, jsonify, redirect,  url_for
import json
#from flask_restful import Api, Resource
from flask_restx import Api, Resource, Namespace
from flasgger import Swagger, swag_from
import datetime
import hashlib
import os.path
import requests





app = Flask(__name__)
api = Api(app, title='Ransomware.live API',
          description='API to query Ransomware.live data.',
          doc='/apidocs/',
          version='1.1')
swagger = Swagger(app)

# Endpoint for retrieving recent posts
class RecentPosts(Resource):
    """Retrieve the 100 most recent posts."""

    @swag_from('swagger_docs/recent_posts.yml')
    def get(self):
        with open('posts.json') as file:
            posts_data = json.load(file)
        for post in posts_data:
            post['screenshot']=''
            if post['post_url'] is not None:
                post_url_bytes = post["post_url"].encode('utf-8')
                post_md5 = hashlib.md5(post_url_bytes).hexdigest()
                # Check if a screenshot file exists for the post
                screenshot_file = f"/var/www/ransomware.live/docs/screenshots/posts/{post_md5}.png"
                if os.path.exists(screenshot_file):
                    # If a screenshot file does  exist
                    post['screenshot']=f"https://images.ransomware.live/screenshots/posts/{post_md5}.png"
        sorted_posts = sorted(posts_data[-100:], key=lambda post: post['published'], reverse=True)
        return jsonify(sorted_posts)

api.add_resource(RecentPosts, '/recent', endpoint='recent')

# Endpoint for retrieving all groups
class AllGroups(Resource):
    """Retrieve all groups."""

    @swag_from('swagger_docs/all_groups.yml')
    def get(self):
        with open('groups.json') as file:
                groups_data = json.load(file)
        return jsonify(groups_data)

api.add_resource(AllGroups, '/groups', endpoint='groups')

# Endpoint for retrieving a specific group
class SpecificGroup(Resource):
    """Retrieve a specific group by its name."""

    @swag_from('swagger_docs/specific_group.yml')
    def get(self, group_name):
        with open('groups.json') as file:
                groups_data = json.load(file)
        for group in groups_data:
            if group['name'] == group_name:
                return jsonify(group)
        return jsonify({"error": "Group not found"}), 404

api.add_resource(SpecificGroup, '/group/<string:group_name>', endpoint='group')

# Endpoint for retrieving posts matching year and month
class Victims(Resource):
    """Retrieve posts where year and month match the 'discovered' field."""

    @swag_from('swagger_docs/victims.yml')
    def get(self, year, month):
        with open('posts.json') as file:
            posts_data = json.load(file)
        for post in posts_data:
            post['discovered'] = str(post['discovered'])
        month = str(month).zfill(2)
        matching_posts = [post for post in posts_data if post['discovered'].startswith(f"{str(year)}-{str(month)}")]
        for post in matching_posts:
            post['screenshot']=''
            if post['post_url'] is not None:
                post_url_bytes = post["post_url"].encode('utf-8')
                post_md5 = hashlib.md5(post_url_bytes).hexdigest()
                # Check if a screenshot file exists for the post
                screenshot_file = f"/var/www/ransomware.live/docs/screenshots/posts/{post_md5}.png"
                if os.path.exists(screenshot_file):
                    # If a screenshot file does  exist
                    post['screenshot']=f"https://images.ransomware.live/screenshots/posts/{post_md5}.png"
        return jsonify(matching_posts)

api.add_resource(Victims, '/victims/<int:year>/<int:month>', endpoint='victims')

# Endpoint for retrieving posts of a specific group
class GroupVictims(Resource):
    """Retrieve posts where group_name matches the 'group_name' field."""

    @swag_from('swagger_docs/group_victims.yml')
    def get(self, group_name):
        with open('posts.json') as file:
            posts_data = json.load(file)
        matching_posts = [post for post in posts_data if post['group_name'] == group_name]
        for post in matching_posts:
            post['screenshot']=''
            if post['post_url'] is not None:
                post_url_bytes = post["post_url"].encode('utf-8')
                post_md5 = hashlib.md5(post_url_bytes).hexdigest()
                # Check if a screenshot file exists for the post
                screenshot_file = f"/var/www/ransomware.live/docs/screenshots/posts/{post_md5}.png"
                if os.path.exists(screenshot_file):
                    # If a screenshot file does  exist
                    post['screenshot']=f"https://images.ransomware.live/screenshots/posts/{post_md5}.png"
        return jsonify(matching_posts)

api.add_resource(GroupVictims, '/groupvictims/<string:group_name>', endpoint='groupvictims')


# Custom error handler for 404 Not Found
@app.errorhandler(404)
def not_found_error_handler(error):
    return redirect(url_for('flasgger.apidocs'))

if __name__ == '__main__':
    app.run()
