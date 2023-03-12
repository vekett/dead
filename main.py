from datetime import datetime
from flask import Flask, request, abort
from humanize import precisedelta
import ujson as json
import os


TIME_FILE_NAME = "checkintime"
AUTH_PASSWORD = "123"
LAST_CHECK_IN = 0
ONE_WEEK = 604800

# Load the messages for each person
with open('messages.json') as f:
    dmmessage = json.load(f)

app = Flask(__name__)

def checkIn(additionalTime: int = 0): # The additionalTime argument is futureproof incase you might be longer than a week
    global LAST_CHECK_IN # a brainfart
    checkInTime = datetime.now().timestamp() + additionalTime
    LAST_CHECK_IN = checkInTime
    with open(TIME_FILE_NAME, 'w') as f:
        f.write(str(checkInTime))
        f.close()

    return checkInTime


def checkAlive():
    global LAST_CHECK_IN # same brainfart
    if not os.path.exists(f'./{TIME_FILE_NAME}'):
        LAST_CHECK_IN = checkIn()
    else:
        with open(TIME_FILE_NAME, 'r') as f:
            buf = f.read()
            LAST_CHECK_IN = float(buf)
            if datetime.now().timestamp() > LAST_CHECK_IN + ONE_WEEK:
                return False
    return True

# Call checkAlive once on startup to create the file if it does not already exist
checkAlive()

@app.route("/alive/<password>")
def alive(password):
    if password == AUTH_PASSWORD:
        checkIn()
        return "Successfully checked in, make sure to check in again within a week."
    abort(404)

# A route made just to be able to make sure a check in has actually worked.
@app.route("/remaining")
def remaining():
    return precisedelta(datetime.now() - datetime.fromtimestamp(LAST_CHECK_IN + ONE_WEEK))

# This route becomes public when you are considered dead.
@app.route("/p/<person>")
def note(person):
    if not checkAlive and person in dmmessage.keys():
        return dmmessage[person]
    abort(404)


if __name__ == "__main__":
    app.run()
