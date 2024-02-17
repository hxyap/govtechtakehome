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
 Single Responsibility and all that!!!
### 1am sat: decided to return a str (mongodb's ObjectID) instead of a UUID since no time.
link to discussion on SO:     https://stackoverflow.com/questions/28895067/using-uuids-instead-of-objectids-in-mongodb
### 1pm sat
may consider consider using Pydantic BaseException (no docs on this???) or Exception that inherits from smth else.