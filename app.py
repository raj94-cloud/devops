from flask import Flask, jsonify, request

app = Flask(__name__)

movies = [
    {"id": 1, "title": "Inception", "genre": "Sci-Fi", "rating": 8.8, "year": 2010},
    {"id": 2, "title": "The Dark Knight", "genre": "Action", "rating": 9.0, "year": 2008},
    {"id": 3, "title": "Interstellar", "genre": "Sci-Fi", "rating": 8.6, "year": 2014},
    {"id": 4, "title": "Avengers", "genre": "Action", "rating": 8.4, "year": 2019},
    {"id": 5, "title": "The Crown", "genre": "Drama", "rating": 8.7, "year": 2020},
]

@app.route("/")
def home():
    return jsonify({"app": "StreamFlix", "version": "1.0"})

@app.route("/movies")
def get_movies():
    genre = request.args.get("genre")
    if genre:
        return jsonify([m for m in movies if m["genre"].lower() == genre.lower()])
    return jsonify(movies)

@app.route("/movies/<int:movie_id>")
def get_movie(movie_id):
    movie = next((m for m in movies if m["id"] == movie_id), None)
    return jsonify(movie) if movie else (jsonify({"error": "Not found"}), 404)

@app.route("/movies/search")
def search():
    q = request.args.get("q", "")
    return jsonify([m for m in movies if q.lower() in m["title"].lower()])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
