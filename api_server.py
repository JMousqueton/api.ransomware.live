#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
API Server for Ransomware.live 
By Julien Mousqueton 
'''
from flask import Flask, jsonify, redirect,  url_for
import json
from flask_restx import Api, Resource, Namespace
from flasgger import Swagger, swag_from
import datetime
import hashlib
import os.path
import requests

''' 
   Configuration for API Server of Ransomware.live 
'''
posts_url = "https://data.ransomware.live/posts.json"
groups_url = "https://data.ransomware.live/groups.json"
cyberattacks_url = "https://raw.githubusercontent.com/Casualtek/Cyberwatch/main/cyberattacks.json"
screenshot_path =  "/var/www/ransomware.live/docs/screenshots/posts/" 
screenshot_url = "https://images.ransomware.live/screenshots/posts/"


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
        #with open('posts.json') as file:
        #    posts_data = json.load(file)
        response = requests.get(posts_url)
        if response.status_code == 200:
            posts_data = response.json()
            for post in posts_data:
                post['screenshot']=''
                if post['post_url'] is not None:
                    post_url_bytes = post["post_url"].encode('utf-8')
                    post_md5 = hashlib.md5(post_url_bytes).hexdigest()
                    # Check if a screenshot file exists for the post
                    screenshot_file = f"{screenshot_path}{post_md5}.png"
                    if os.path.exists(screenshot_file):
                        # If a screenshot file does  exist
                        post['screenshot']=f"{screenshot_url}{post_md5}.png"
            sorted_posts = sorted(posts_data[-100:], key=lambda post: post['published'], reverse=True)
            return jsonify(sorted_posts)
        else:
            return jsonify({"error": "Failed to fetch data from the source"}), response.status_code

# Endpoint for retrieving all groups
class AllGroups(Resource):
    """Retrieve all groups."""
    @swag_from('swagger_docs/all_groups.yml')
    def get(self):
        #with open('groups.json') as file:
        #        groups_data = json.load(file)
        response = requests.get(groups_url)
        if response.status_code == 200:
            groups_data = response.json()
            return jsonify(groups_data)
        else:
            return jsonify({"error": "Failed to fetch data from the source"}), response.status_code

# Endpoint for retrieving a specific group
class SpecificGroup(Resource):
    """Retrieve a specific group by its name."""
    @swag_from('swagger_docs/specific_group.yml')
    def get(self, group_name):
        #with open('groups.json') as file:
        #        groups_data = json.load(file)
        response = requests.get(groups_url)
        if response.status_code == 200:
            groups_data = response.json()
            for group in groups_data:
                if group['name'] == group_name:
                    return jsonify(group)
            return jsonify({"error": "Group not found"}), 404
        else:
            return jsonify({"error": "Failed to fetch data from the source"}), response.status_code

# Endpoint for retrieving posts matching year and month
class Victims(Resource):
    """Retrieve posts where year and month match the 'discovered' field."""
    @swag_from('swagger_docs/victims.yml')
    def get(self, year, month):
        #with open('posts.json') as file:
        #    posts_data = json.load(file)
        response = requests.get(posts_url)
        if response.status_code == 200:
            posts_data = response.json()
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
                    screenshot_file = f"{screenshot_path}{post_md5}.png"
                    if os.path.exists(screenshot_file):
                        # If a screenshot file does  exist
                        post['screenshot']=f"{screenshot_url}{post_md5}.png"
            return jsonify(matching_posts)
        else:
            return jsonify({"error": "Failed to fetch data from the source"}), response.status_code

# Endpoint for retrieving posts of a specific group
class GroupVictims(Resource):
    """Retrieve posts where group_name matches the 'group_name' field."""
    @swag_from('swagger_docs/group_victims.yml')
    def get(self, group_name):
        response = requests.get(posts_url)
        if response.status_code == 200:
            posts_data = response.json()
        #with open('posts.json') as file:
        #    posts_data = json.load(file)
            matching_posts = [post for post in posts_data if post['group_name'] == group_name]
            for post in matching_posts:
                post['screenshot']=''
                if post['post_url'] is not None:
                    post_url_bytes = post["post_url"].encode('utf-8')
                    post_md5 = hashlib.md5(post_url_bytes).hexdigest()
                    # Check if a screenshot file exists for the post
                    screenshot_file = f"{screenshot_path}{post_md5}.png"
                    if os.path.exists(screenshot_file):
                        # If a screenshot file does  exist
                        post['screenshot']=f"{screenshot_url}{post_md5}.png"
            return jsonify(matching_posts)
        else:
            return jsonify({"error": "Failed to fetch data from the source"}), response.status_code

# Endpoint for retrieving the last 100 entries from the cyberattacks.json file
class RecentCyberattacks(Resource):
    """Retrieve the last 100 entries from the cyberattacks.json file sorted by date."""
    @swag_from('swagger_docs/recent_cyberattacks.yml')
    def get(self):
        response = requests.get(cyberattacks_url)
        if response.status_code == 200:
            cyberattacks_data = response.json()
            #sorted_cyberattacks = sorted(cyberattacks_data, key=lambda entry: entry['date'], reverse=False)
            sorted_cyberattacks = sorted(cyberattacks_data, key=lambda x: x['date'], reverse=True)
            recentnews = []
            for attack in sorted_cyberattacks:
                recentnews.append(attack)
                if len(recentnews) == 100:
                    break
            return recentnews
            # return jsonify(sorted_cyberattacks[-100:])
        else:
            return jsonify({"error": "Failed to fetch data from the source"}), response.status_code

# Endpoint definitions
api.add_resource(RecentPosts, '/recentvictims', endpoint='recent')
api.add_resource(AllGroups, '/groups', endpoint='groups')
api.add_resource(SpecificGroup, '/group/<string:group_name>', endpoint='group')
api.add_resource(Victims, '/victims/<int:year>/<int:month>', endpoint='victims')
api.add_resource(GroupVictims, '/groupvictims/<string:group_name>', endpoint='groupvictims')
api.add_resource(RecentCyberattacks, '/recentcyberattacks', endpoint='cyberattacks')

# Custom error handler for 404 Not Found
@app.errorhandler(404)
def not_found_error_handler(error):
    return redirect(url_for('flasgger.apidocs'))

if __name__ == '__main__':
    print(
    '''
       _______________                         |*\_/*|________
      |  ___________  |                       ||_/-\_|______  |
      | |           | |                       | |           | |
      | |   0   0   | |                       | |   0   0   | |
      | |     -     | |                       | |     -     | |
      | |   \___/   | |                       | |   \___/   | |
      | |___     ___| |                       | |___________| |
      |_____|\_/|_____|                       |_______________|
        _|__|/ \|_|_.............💔.............._|________|_
       / ********** \                           / ********** \ 
     /  ************  \  Ransomware.live API  /  ************  \ 
    --------------------                     --------------------
    '''
    )   
    app.run()
