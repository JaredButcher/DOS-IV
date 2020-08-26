from gamesite import createApp
import flask

app = createApp()

@app.route('/')
def home():
    return flask.render_template('home.html')

if __name__ == '__main__':
    app.run()
