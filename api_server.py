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
# Cache 
from flask_caching import Cache
# Limiter 
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import warnings # to remove warning about in memory 

# Suppress the specific UserWarning about in-memory storage for Flask-Limiter
warnings.filterwarnings("ignore", category=UserWarning, message=".*Using the in-memory storage.*")

posts_url = "https://data.ransomware.live/victims.json"
posts_path = "/var/www/ransomware-ng/data/victims.json"
groups_url = "https://data.ransomware.live/groups.json"
groups_path = "/var/www/ransomware-ng/data/groups.json"
cyberattacks_url = "https://raw.githubusercontent.com/Casualtek/Cyberwatch/main/cyberattacks.json"
screenshot_path =  "/var/www/ransomware-ng/docs/screenshots/posts/" 
screenshot_url = "https://images.ransomware.live/screenshots/posts/"
hudsonrock_path = "/var/www/ransomware-ng/data/hudsonrock.json"
ttps_path = "/var/www/ransomware-ng/data/ttps.json" 
headers = {
    'User-Agent': 'Ransomware.live API v0.2'
}

# Configure cache
cache_config = {
    "CACHE_TYPE": "SimpleCache",  # Use simple in-memory caching
    "CACHE_DEFAULT_TIMEOUT": 1800  # 1800 seconds = 30 minutes
}


app = Flask(__name__)
api = Api(app, title='Ransomware.live API',
          description='API to query Ransomware.live data.',
          doc='/apidocs/',
          version='1.1')
swagger = Swagger(app)

# initalize Cache
app.config.from_mapping(cache_config)
cache = Cache(app)

# Initialize Limiter
limiter = Limiter(
    app=app,  # Specify 'app' as a keyword argument for clarity
    key_func=get_remote_address,  # Use the client IP address as the rate limit key
    default_limits=[]  # Optional: Define default rate limits
)

# Endpoint for retrieving recent posts
class RecentPosts(Resource):
    """Retrieve the 100 most recent posts."""

    @swag_from('swagger_docs/recent_posts.yml')
    @cache.cached(timeout=1800, key_prefix='recent_posts')
    @limiter.limit("1 per minute")
    def get(self):
        with open(posts_path) as file:
            posts_data = json.load(file)
        # Load Hudson Rock data
        with open(hudsonrock_path) as file:
            hudsonrock_data = json.load(file)
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
                if post.get('website'):
                    # Remove 'http://', 'https://', and trailing '/'
                    clean_website = post['website'].replace('http://', '').replace('https://', '').rstrip('/')
                    if clean_website in hudsonrock_data:
                        post['infostealer'] = hudsonrock_data[clean_website]    
        sorted_posts = sorted(posts_data[-100:], key=lambda post: post['published'], reverse=True)
        return jsonify(sorted_posts)

# Endpoint for retrieving all groups
class AllGroups(Resource):
    """Retrieve all groups."""
    @swag_from('swagger_docs/all_groups.yml')
    def get(self):
        with open(groups_path) as file:
                groups_data = json.load(file)
        return jsonify(groups_data)

# Endpoint for retrieving a specific group
#class SpecificGroup(Resource):
#    """Retrieve a specific group by its name."""
#    @swag_from('swagger_docs/specific_group.yml')
#    def get(self, group_name):
#        with open(groups_path) as file:
#            groups_data = json.load(file)
#        for group in groups_data:
#            if group['name'] == group_name:
#                return jsonify(group)
#        return {"error": "Group not found"}, 404


class SpecificGroup(Resource):
    """Retrieve a specific group by its name."""
    @swag_from('swagger_docs/specific_group.yml')
    def get(self, group_name):
        # Load the existing group data
        with open(groups_path) as file:
            groups_data = json.load(file)
        
        # Load the ttps.json data
        with open(ttps_path) as ttps_file:
            ttps_data = json.load(ttps_file)

        # Find the specific group
        for group in groups_data:
            if group['name'] == group_name:
                # Find the corresponding ttps data
                ttps_list = []
                for ttps_group in ttps_data:
                    if ttps_group['group_name'] == group_name.lower().replace(" ", ""):
                        # Remove the "group_name" entry from the ttps_group
                        ttps_group_without_name = {k: v for k, v in ttps_group.items() if k != 'group_name'}
                        # Add the ttps information to the ttps_list
                        ttps_list.append(ttps_group_without_name)
                
                # Add the ttps list to the group information
                group['ttps'] = ttps_list

                # Return the updated group data with ttps information
                return jsonify(group)
        
        # If the group is not found, return an error
        return {"error": "Group not found"}, 404



# Endpoint for retrieving posts matching year and month
class Victims(Resource):
    """Retrieve posts where year and month match the 'discovered' field."""
    @swag_from('swagger_docs/victims.yml')
    def get(self, year, month=None):
        with open(posts_path) as file:
            posts_data = json.load(file)
        # Load Hudson Rock data
        with open(hudsonrock_path) as file:
            hudsonrock_data = json.load(file)
        for post in posts_data:
            post['discovered'] = str(post['discovered'])
            if month: 
                month = str(month).zfill(2)
                matching_posts = [post for post in posts_data if post['discovered'].startswith(f"{str(year)}-{str(month)}")]
            else: 
                matching_posts = [post for post in posts_data if post['discovered'].startswith(f"{str(year)}-")]
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
                if post.get('website'):
                    # Remove 'http://', 'https://', and trailing '/'
                    clean_website = post['website'].replace('http://', '').replace('https://', '').rstrip('/')
                    if clean_website in hudsonrock_data:
                        post['infostealer'] = hudsonrock_data[clean_website]    
            return jsonify(matching_posts)

# Endpoint for retrieving posts of a specific group
class GroupVictims(Resource):
    """Retrieve posts where group_name matches the 'group_name' field."""
    @swag_from('swagger_docs/group_victims.yml')
    def get(self, group_name):
        with open(posts_path) as file:
            posts_data = json.load(file)
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


class AllCyberattacks(Resource):
    """Retrieve the last 100 entries from the cyberattacks.json file sorted by date."""
    @swag_from('swagger_docs/all_cyberattacks.yml')
    def get(self):
        response = requests.get(cyberattacks_url)
        if response.status_code == 200:
            cyberattacks_data = response.json()
            #sorted_cyberattacks = sorted(cyberattacks_data, key=lambda entry: entry['date'], reverse=False)
            sorted_cyberattacks = sorted(cyberattacks_data, key=lambda x: x['date'], reverse=True)
            recentnews = []
            for attack in sorted_cyberattacks:
                recentnews.append(attack)
            return recentnews
            # return jsonify(sorted_cyberattacks[-100:])
        else:
            return jsonify({"error": "Failed to fetch data from the source"}), response.status_code

class Country(Resource):
    @swag_from('swagger_docs/country.yml')
    def get(self, id):
        with open('country.json', 'r') as file:
            country_data = json.load(file)
        for country in country_data:
            if country['id'] == id:
                return jsonify({"title": country["title"]})
                break
        return jsonify({"error": "Country not found"}), 404

class CountryAttacks(Resource):
    @swag_from('swagger_docs/country_attacks.yml')
    def get(self, country_code):
        response = requests.get(posts_url)
        if response.status_code == 200:
            posts_data = response.json()
            country_attacks = [
                post for post in posts_data
                if post.get('country') == country_code.upper()
            ]
            return jsonify(country_attacks)
        else:
            return jsonify({"error": "Failed to fetch data from the source"}), response.status_code


# Endpoint definitions
api.add_resource(RecentPosts, '/recentvictims', endpoint='recent')
api.add_resource(AllGroups, '/groups', endpoint='groups')
api.add_resource(SpecificGroup, '/group/<string:group_name>', endpoint='group')
# api.add_resource(Victims, '/victims/<int:year>/<int:month>', endpoint='victims')
api.add_resource(Victims, '/victims/<int:year>', '/victims/<int:year>/<int:month>')
api.add_resource(GroupVictims, '/groupvictims/<string:group_name>', endpoint='groupvictims')
api.add_resource(RecentCyberattacks, '/recentcyberattacks', endpoint='cyberattacks')
api.add_resource(AllCyberattacks, '/allcyberattacks', endpoint='allcyberattacks')
api.add_resource(Country, '/country/<string:id>', endpoint='country')
api.add_resource(CountryAttacks, '/countryattacks/<string:country_code>', endpoint='countryattacks')

# Custom error handler for 404 Not Found
@app.errorhandler(404)
def not_found_error_handler(error):
    return redirect(url_for('flasgger.apidocs'))

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(error="Rate limit exceeded, please try again later."), 429

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
