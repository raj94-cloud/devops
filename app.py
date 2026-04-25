from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

movies = [
    {"id": 1, "title": "Inception", "genre": "Sci-Fi", "rating": 8.8, "year": 2010,
     "thumbnail": "https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg",
     "description": "A thief who steals corporate secrets through dream-sharing technology.",
     "trailer": "https://www.youtube.com/embed/YoHD9XEInc0"},
    {"id": 2, "title": "The Dark Knight", "genre": "Action", "rating": 9.0, "year": 2008,
     "thumbnail": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
     "description": "Batman faces the Joker, a criminal mastermind who wants to plunge Gotham into anarchy.",
     "trailer": "https://www.youtube.com/embed/EXeTwQWrcwY"},
    {"id": 3, "title": "Interstellar", "genre": "Sci-Fi", "rating": 8.6, "year": 2014,
     "thumbnail": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
     "description": "A team of explorers travel through a wormhole in space.",
     "trailer": "https://www.youtube.com/embed/zSWdZVtXT7E"},
    {"id": 4, "title": "Avengers Endgame", "genre": "Action", "rating": 8.4, "year": 2019,
     "thumbnail": "https://image.tmdb.org/t/p/w500/or06FN3Dka5tukK1e9sl16pB3iy.jpg",
     "description": "The Avengers assemble to reverse Thanos' actions.",
     "trailer": "https://www.youtube.com/embed/TcMBFSGVi1c"},
    {"id": 5, "title": "The Crown", "genre": "Drama", "rating": 8.7, "year": 2020,
     "thumbnail": "https://image.tmdb.org/t/p/w500/1M876KPjulVwppEpldhdc8V4o68.jpg",
     "description": "Follows the political rivalries and romance of Queen Elizabeth II's reign.",
     "trailer": "https://www.youtube.com/embed/JWtnJjn6ng0"},
]

@app.route("/")
def home():
    return render_template("index.html", movies=movies)

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
