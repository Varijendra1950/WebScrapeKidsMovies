
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import urllib.request
from csv import reader, writer



start_page = "https://kids-in-mind.com/a.htm"

res = requests.get(start_page)

movie_dict = {"title": [],
              "year": [],
              "mpaa": [],
              "KIM sex": [],
              "KIM violence": [],
              "KIM language": []}

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

    # TODO Assemble a movie dictionary

    for movie in movies:

        year_idx1 = movie.find("[")
        year_idx2 = movie.find("]")

        mpaa_idx1 = movie.find("[", year_idx1+1)
        mpaa_idx2 = movie.find("]", year_idx2 + 1)

        year = int(movie[year_idx1+1:year_idx2].strip())
        mpaa = movie[mpaa_idx1+1:mpaa_idx2]

        ratings = movie.split("–")[-1].split(".")
        ratings = [int(x) for x in ratings]

        title = movie[0:year_idx1]

        movie_dict["title"].append(title)
        movie_dict["year"].append(year)
        movie_dict["mpaa"].append(mpaa)
        movie_dict["KIM sex"].append(ratings[0])
        movie_dict["KIM violence"].append(ratings[1])
        movie_dict["KIM language"].append(ratings[2])

    res.close()

else:
    print(f"Error: {res}")

df_movies = pd.DataFrame(movie_dict)

df_movies.to_csv("Movies.csv")