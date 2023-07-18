![](https://raw.githubusercontent.com/JMousqueton/ransomware.live/main/.github/ransomware.live.png)

>[`Api.Ransomware.live`](https://api.ransomware.live) is an api to query [`Ransomware.live`](https://ransomware.live)

## 🔬 Description

The Ransomware.live API Server is a Flask-based web application that provides endpoints to query and retrieve data related to ransomware posts and cyberattacks. This API serves as a backend for Ransomware.live, a service that aggregates and displays information about recent ransomware incidents and groups.

[Ransomware.live](https://ransomware.live) is originally a fork of [ransomwatch](https://github.com/joshhighet/ransomwatch) 

[Ransomware.live](https://ransomware.live) is a ransomware leak site monitoring tool. It will scrape all of the entries on various ransomware leak sites and published them.

## 🪄 Features

- Retrieve the 100 most recent ransomware posts.
- Get information about all ransomware groups.
- Fetch details about a specific ransomware group by its name.
- Query posts where the year and month match the 'discovered' field.
- Fetch posts associated with a specific ransomware group.
- Retrieve the last 100 entries from the 'cyberattacks.json' file, sorted by date.

## 📍 Endpoints

- `/recentvictims`: Retrieve the 100 most recent ransomware posts.
- `/groups`: Get information about all ransomware groups.
- `/group/<group_name>`: Fetch details about a specific ransomware group by its name.
- `/victims/<year>/<month>`: Query posts where the year and month match the 'discovered' field.
- `/groupvictims/<group_name>`: Fetch posts associated with a specific ransomware group.
- `/recentcyberattacks`: Retrieve the last 100 entries from the 'cyberattacks.json' file, sorted by date.

## ⚙️ Setup and Usage

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/yourusername/ransomware-live-api.git
   cd ransomware-live-api
   ```

2. Install the required dependencies using pip:

    ```bash
    pip install -r requirements.txt
    ```

3. Run the Flask server:

    ```bash
    python api_server.py
    ```

The server will start running locally, and you can access the API at http://localhost:5000.

## 📚 API Documentation

For detailed information about the available endpoints, parameters, and responses, you can visit the API documentation generated using Swagger. Open your web browser and navigate to:

    ```bash
    http://localhost:5000/apidocs
    ```

## ❤️ Contributing 

We welcome contributions to improve the Ransomware.live API Server. If you find a bug or have an idea for an enhancement, feel free to open an issue or submit a pull request. For major changes, please open an issue first to discuss the proposed changes.

## 👨🏼‍💼 About me 

I'm **Julien Mousqueton**

- I'm **CTO** in Cyber Security 🛡 
- I'm a **lecturer** 🎓 in Cyber Security @ [Ecole 2600](https://www.ecole2600.com) 🏴‍☠️
- I'm a **blogger** ✍🏻 at [julien.io](https://julien.io) in french 🇫🇷 

You can find more in [my resume](https://cv.julien.io) in English (also available in [French](https://cv.julien.io/fr) / aussi disponible en [français](https://cv.julien.io/fr))

## 🤩 Credits

- [Josh Highet](https://github.com/joshhighet) for the original [ransomwatch](https://github.com/joshhighet/ransomwatch) project. 
- [Valéry Rieß-Marchive](https://twitter.com/ValeryMarchive) for ideas and his involvement in the cyber community.

## ⚠️ Disclamer

Please note that this code was developed for educational and informational purposes. The usage of this code or any data obtained from the API is at your own risk. The developers and contributors to this project do not endorse or support any malicious or illegal activities related to ransomware or cyberattacks.

## 📜 License

The Ransomware.live API Server is licensed under the `MIT License`. For more information, see the [LICENSE](https://github.com/jmousqueton/api.ransomware.live/blob/main/LICENSE) file.
