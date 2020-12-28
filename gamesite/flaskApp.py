from gamesite import createApp
import flask

app = createApp()

@app.route('/')
def home():
    return flask.render_template('home.html')

def run():
    app.run()

if __name__ == '__main__':
    run()
