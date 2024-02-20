Instructions on WSL2 Ubuntu 20.04, with python 3.10,
- Make sure your .env file has two variables:
- OPENAI_API_KEY= (your openai key)
- MONGODB_URL=mongodb://root:example@mongo:27017/
- ^ based off [mongo db](https://hub.docker.com/_/mongo)
- Start in / (your root folder).
- Run "docker-compose up" in powershell/Ubuntu. This starts up the fastapi server as well as the mongodb docker image from mongo.
- Then, run "python3.10 -m venv {your venv folder name}" in /backend-app.
- Afterwards, run "source {your venv folder name}/bin/activate" to activate your venv.
- cd into /app and run "pip install -r requirements.txt" to install the necessary dependecies.
- after app and mongodb are running, in a different Terminal on WSL2 on VSCode/ other platforms, 
  cd into app/tests, then run "python manual_conv_api_test.py" which will print and show the relevant results for all 
  endpoint methods.
- (Optional) At the moment, test_conversations is incomplete, but is used to mock and test to see if they throw the expected
  errors when errors occur - cd to /app and run with "python -m pytest /tests"
I intend to replace this with automated testing w/ pytest mocks + AsyncMongoMockClient so that this is ready for testing thru
a proper CI/CD when the time for that comes.
