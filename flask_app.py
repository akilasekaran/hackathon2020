from flask import Flask, render_template, request, jsonify, make_response
from dbsetup import create_connection, select_all_items, update_item, display_all_items,main_db, drop_table
from flask_cors import CORS, cross_origin
import pusher
import simplejson

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


# configure pusher object
pusher_client = pusher.Pusher(
  app_id='989732',
  key='08eccae6e2be3b921ec6',
  secret='e052c4fbf9bcc2099d2d',
  cluster='us2',
  ssl=True
)


database = "./pythonsqlite.db"
conn = create_connection(database)


c = conn.cursor()


def main():
    global conn, c


@app.route('/')
def index():
    print("hello")
    return "This app works! Try other GET and POST requests....."

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/live_result')
def results():
    try:
        output = display_all_items(c)
        return output
    except:
        return "No poll is going on!"

@app.route('/vote', methods=['POST'])
def vote():
    try:
        print(request.data)
        # {"member":"Yes"}
        data = simplejson.loads(request.data)
        update_item(c, [data['member']])
        output = select_all_items(c, [data['member']])
        print(output)
        pusher_client.trigger(u'chime-poller', u'vote', output)
        #output = display_all_items(c)
        return output
    except:
        return "You can't vote now!"

@app.route('/create_poll', methods=['POST'])
def create_poll():
    global question,options
    data= simplejson.loads(request.data)
    # data = {"question":"Do you like sweets?", "options":["Yes","No"]}
    print(data["question"])
    print(data["options"])
    question = data["question"]
    options= data["options"]
    main_db(options)
    pusher_client.trigger(u'chime-poller', u'new_poll',data) # triggers the new_poll event whenever a new poll created
    return(data)

@app.route('/get_question')
def get_question():
    try:
        return {"question":question, "options":options}
    except:
        return {"question" : "empty", "options" : [ ] }


@app.route('/end_poll')
def end_poll():
    try:
        output= display_all_items(c)
        drop_table(c)
        print("The poll has ended!")
        return {"poll ended": output}
    except:
        return "You can end a poll only after you create a poll!"


if __name__ == '__main__':
    main()
    app.run(debug=True)
