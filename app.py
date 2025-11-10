from flask import Flask, render_template, request
import requests

app = Flask(__name__)

TMDB_API_KEY = "94b00730deb756ceba1b9d2f2cb3aa69"  # <--- ใส่ key ของคุณ

def search_movie(query):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}&language=th-TH"
    r = requests.get(url)
    res = r.json()
    if res.get("results"):
        return res["results"][0]  # เอาหนังที่ตรงสุด
    return None

def get_movie_genres(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=th-TH"
    r = requests.get(url)
    res = r.json()
    return res.get("genres", [])

def recommend_movies_by_genre(genre_id, exclude_id=None, count=5):
    url = (
        f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}"
        f"&with_genres={genre_id}&sort_by=vote_average.desc&vote_count.gte=100"
        f"&language=th-TH"
    )
    r = requests.get(url)
    res = r.json()
    movies = []
    for m in res.get("results", []):
        if m["id"] != exclude_id:
            movies.append(m)
        if len(movies) >= count:
            break
    return movies

@app.route("/", methods=["GET", "POST"])
def index():
    movie = None
    recommendations = []
    error = None

    # รองรับทั้ง POST และ GET
    movie_name = ""
    if request.method == "POST":
        movie_name = request.form.get("movie_name", "").strip()
    else:
        movie_name = request.args.get("movie_name", "").strip()

    if movie_name:
        movie = search_movie(movie_name)
        if movie:
            genres = get_movie_genres(movie["id"])
            if genres:
                genre_id = genres[0]["id"]
                recommendations = recommend_movies_by_genre(genre_id, exclude_id=movie["id"], count=5)
            else:
                error = "หนังนี้ไม่มีข้อมูลแนวหนัง"
        else:
            error = "ไม่พบหนังที่ค้นหา"
    elif request.method == "POST":
        error = "กรุณากรอกชื่อหนัง"

    return render_template(
        "index.html",
        movie=movie,
        recommendations=recommendations,
        error=error,
    )

if __name__ == "__main__":
    app.run(debug=True)
