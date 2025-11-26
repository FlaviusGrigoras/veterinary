from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Salut! Proiectul meu este acum pe GitHub."

if __name__ == '__main__':
    app.run(debug=True)