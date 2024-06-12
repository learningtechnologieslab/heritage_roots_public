# _HeritageRoots_ Indigenous Traditional Knowledge (ITK)

Around the world, many cultures are significantly threatened by the erosion of cultural integrity, climate change, loss of habitat, the environmental impact of globalization, and the ravages of epidemics. Cultures that do not have a strong written tradition are especially threatened – as younger generations move away in search of education and jobs, and as globalization forces linguistic shifts to more “global” languages such as English and Spanish, rich oral traditions either disappear completely or become artifacts in university or library archives, accessible only to small groups of academics. Many initiatives have been activated to preserve and revitalize indigenous cultures, traditions, and languages. While quite a few of these initiatives involve the use of computational technologies and multimedia to document and archive indigenous languages, knowledge, and cultures, much of what has been created to date is primarily designed to serve academic communities and does not provide access to either the broader public (e.g., anyone who wishes to learn about a particular culture) or to the indigenous communities that provided the data in the first place. Moreover, existing systems tend to focus on a single corpus of stories and do not provide possibilities to connect and map stories, characters, and concepts across multiple cultures and languages.

Our team has collaborated with indigenous communities in Ecuador and with scholars from several universities to develop StoryWorlds ITK (Indigenous Traditional Knowledge), an innovative software infrastructure designed for cultural preservation and education. StoryWorlds ITK consists of two interconnected systems - (1) a web-based knowledge graph (KG) data collection and management system which stores, connects, and presents Indigenous traditional knowledge (ITK) in the form of stories, myths, and testimonies from multiple cultures and languages; (2) a virtual environment rendering pipeline which utilizes large language models (LLM), Unity3D, and Meta Quest software development kit (SDK) to procedurally generate virtual worlds from the KG data.

## Installation/Deployment
**StoryWorlds ITK** is a web-based application written in Python and designed to run on Flask.

### Flask + Visual Studio Code
https://code.visualstudio.com/docs/python/tutorial-flask

### Flask + Virtual Environments
1. Clone this repository
2. In the terminal/command prompt, change directory to the repository's directory. For example, if you are a MacOS user, and your folder is called "story_worlds_web" and it is located on your Desktop, you will run the following command in the terminal: > cd /Users/<your_user_name>/Desktop/story_worlds_web.  If you are a Windows user, you will run the following command in the command propmt window: > cd C:\users\<your_user_name>\Desktop\story_worlds_web
4. In the local repository (on your local computer), initialize a Python virtual environment.  Follow this tutorial (https://docs.python.org/3/library/venv.html) to learn about Python virtual environments. Note that all the following commands assume that you named your virtual environment folder **venv**.
5. Activate virtual environment: > _source ./venv/bin/activate_
6. Install pandas, flask, neo4j, Jupyter, openai, spacy, and en_core_web_sm for spacy.  You can install all dependencies by running > _./venv/bin/pip3 install requirements.txt_
13. Launch the web application: > _./venv/bin/python3 app.py_
14. Open your web browser and navigate to http://localhost:5000
