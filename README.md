# GovTech AI Bots Backend Take-home submission
This was written for the takehome assignment for GovTech in 2024 Feb.
Initial implementation thoughts:
My mental model of the user flow was this:
1. User sends in POST to /conversations, which passes them a Conversation id and they are routed to their specific /conversation/{id}.
2. Here, they can send in message and receive messages back through the /queries endpoint, which will update their specific
conversation id in the backend and then return the message back to the user.
3. PUT /conversations/{id} will be fine as they only need it to change system message/temperature. For sake of time atm will only
test with temperature, but imo should be able to let users potentially cut out past messages, provided that there is a check that past message exists.
4 GET: I guess you would issue the user a JWT token/ some sort of session identifier, and GET user conversations based off that
by passing it in as request header. Session cookies work too, but for sake of demo i add this later if i dont add it in time here
Additional modules:
5 GET /conversations/{id} straight forward, but ideally theres better security for this lol, require the correct header/auth
6 DELETE /conversations/{id} similar to GET.
I used tiktoken to count the number of tokens consumed.

### 9.47pm fri
 refactored my personal code to only use app.py D: no more /endpoints, too optimistic, but ideally use routing to /endpoints?
 This would make my main.py easier to read.
### 9pm sat:
By right, should be using AsyncMotorMockClient + pytest with mongomock or smth to test.
However, atm can be testing using manual_conv_api_test.py.
Instructions on WSL2 Ubuntu 20.04, with python 3.10,
- Start in /backend-app.
- Run "docker-compose up" in powershell/Ubuntu. This starts up the fastapi server as well as the mongodb docker image from mongo.
- Then, run "python3.10 -m venv {your venv folder name}" in /backend-app.
- Afterwards, run "source {your venv folder name}/bin/activate" to activate your venv.
- after app and mongodb are running, in a different Terminal on WSL2 on VSCode/ other platforms, 
  cd into cd app/tests, then run "python manual_conv_api_test.py" which will print and show the relevant results for all 
  endpoint methods.
I intend to replace this with automated testing w/ pytest mocks + AsyncMongoMockClient so that this is ready for testing thru
a proper CI/CD when the time for that comes.


### To-do:
- Clean up my @app.(method) so that the OpenAPI docs generated for them are accurate.
- Add tests so that I can confirm my request handlers work.
### Local tests using manual tests on live db as of 10pm Sat:
![alt text](https://i.ibb.co/7KdbdwQ/Screenshot-557.png "photo")

### State of my pytest setup:
My pytest setup is currently incomplete - trying to get it to prepopulate the mock db. If that fails, will set up and make it
connect to MongoDB Altas to test on a live db in worst case scenario. At least it shows I throw 500/400/404 codes as expected though...