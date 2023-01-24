
import pandas as pd
import requests
from bs4 import BeautifulSoup
import string
import time
import urllib.request


movie_dict = {"title": [],
              "year": [],
              "mpaa": [],
              "KIM sex": [],
              "KIM violence": [],
              "KIM language": []}

for letter in string.ascii_lowercase:
    url = f"https://kids-in-mind.com/{letter}.htm"

    res = requests.get(url)

    if res:
        soup = BeautifulSoup(res.text, "html.parser")
        a = soup.findAll("div", class_="et_pb_text_inner")

        idx = 0
        for entry in a:
            text = entry.getText()
            if "Movie Reviews by Title" in text:
                idx += 1
                break
            idx += 1
        # All movies on the page, separated by /n
        movies = a[idx].getText().split("\n")

        for movie in movies:

            # some entries had a foreign name in brackets
            if movie.count("]") > 2:
                start_idx = movie.find("]")+1
            else:
                start_idx = 0

            year_idx1 = movie.find("[", start_idx)
            year_idx2 = movie.find("]", start_idx)

            mpaa_idx1 = movie.find("[", year_idx1+1)
            mpaa_idx2 = movie.find("]", year_idx2 + 1)

            year = int(movie[year_idx1+1:year_idx2].strip())
            mpaa = movie[mpaa_idx1+1:mpaa_idx2]

            ratings_split = movie.split("–")
            # sometimes they used a dash, sometimes an en dash
            if len(ratings_split) == 1:
                ratings_split = movie.split("-")

            ratings = [int(x) for x in ratings_split[-1].split(".")]

            title = movie[0:year_idx1]

            movie_dict["title"].append(title)
            movie_dict["year"].append(year)
            movie_dict["mpaa"].append(mpaa)
            movie_dict["KIM sex"].append(ratings[0])
            movie_dict["KIM violence"].append(ratings[1])
            movie_dict["KIM language"].append(ratings[2])

        res.close()

        print(f"Done with {letter}. Waiting 0.5 second")
        time.sleep(0.5)

    else:
        print(f"Error: {res}")

df_movies = pd.DataFrame(movie_dict)

df_movies.to_csv("Movies.csv")