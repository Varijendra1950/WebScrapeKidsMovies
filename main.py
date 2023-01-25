import pandas as pd
import requests
from bs4 import BeautifulSoup
import string
import time
from urllib.parse import urljoin
import random
import urllib.request


def scrape_kim_sexcontent(url):
    # Request html from page and find all p elements
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    p_set = soup.findAll("p")

    # TODO -- Add in a search for h2 id=sex and the paragraph just underneath it. Like --> https://kids-in-mind.com/b/beast-parents-guide-movie-review-rating.htm

    res.close()

    # Look for the sex content section and return it when found
    sex_content = ""
    for entry in p_set:
        if 'SEX/NUDITY' in entry.text:
            sex_content = entry.text
            return sex_content

    return sex_content


def parse_movie(movie):
    # some entries had a foreign name in brackets
    if movie.count("]") > 2:
        start_idx = movie.find("]") + 1
    else:
        start_idx = 0

    # year is usually in the first set of brackets
    year_idx1 = movie.find("[", start_idx)
    year_idx2 = movie.find("]", start_idx)

    # mpaa rating was next
    mpaa_idx1 = movie.find("[", year_idx1 + 1)
    mpaa_idx2 = movie.find("]", year_idx2 + 1)

    year = int(movie[year_idx1 + 1:year_idx2].strip())
    mpaa = movie[mpaa_idx1 + 1:mpaa_idx2]

    # the ratings came after a dash and were formatted like #.#.#
    ratings_split = movie.split("–")
    # sometimes they used a dash, sometimes an en dash
    if len(ratings_split) == 1:
        ratings_split = movie.split("-")

    ratings = [int(x) for x in ratings_split[-1].split(".")]

    title = movie[0:year_idx1]

    return year, mpaa, ratings, title


def scrape_kim_ratings(letters):
    movie_dict = {"title": [],
                  "year": [],
                  "mpaa": [],
                  "KIM sex": [],
                  "KIM violence": [],
                  "KIM language": [],
                  "KIM sex content": []}

    for letter in letters:
        # Get a response from each letter page
        url = f"https://kids-in-mind.com/{letter}.htm"
        res = requests.get(url)

        if res:
            # Get the HTML from that page
            soup = BeautifulSoup(res.text, "html.parser")
            # The list of movies is in a div element with class = et_pb_text_inner
            div = soup.findAll("div", class_="et_pb_text_inner")

            # Find the list of movies. It comes after "Movie Reviews by Title"
            idx = 0
            for entry in div:
                text = entry.getText()
                if "Movie Reviews by Title" in text:
                    idx += 1
                    break
                idx += 1

            # All movies on the page, separated by /n (movie names with ratings are stored as text of the div element)
            movies = div[idx].getText().split("\n")

            # href links to each movie page are stored in a elements
            a = div[idx].findAll("a")
            links = [urljoin(url, x["href"]) for x in a]

            # zip these up to make iteration easier in the for loop
            movies_and_links = list(zip(movies, links))

            for movie, link in movies_and_links:
                # get the information available in the list on each letter page
                year, mpaa, ratings, title = parse_movie(movie)

                # follow each movie link to get the sex content description
                start = time.time()
                sex_content = scrape_kim_sexcontent(link)
                delay = time.time() - start

                wait_time = random.uniform(.5, 2) * delay
                print(f'Just finished{title}')
                print(f'wait time is {wait_time}')

                # Build dictionary for conversion to data frame
                movie_dict["title"].append(title)
                movie_dict["year"].append(year)
                movie_dict["mpaa"].append(mpaa)
                movie_dict["KIM sex"].append(ratings[0])
                movie_dict["KIM violence"].append(ratings[1])
                movie_dict["KIM language"].append(ratings[2])
                movie_dict["KIM sex content"].append(sex_content)

            res.close()

            print(f"Done with {letter}. Waiting {wait_time} seconds")
            time.sleep(wait_time)

        else:
            print(f"Error: {res}")

    df_movies = pd.DataFrame(movie_dict)

    df_movies.to_csv("Movies.csv")

    return df_movies


df_movies = scrape_kim_ratings(string.ascii_lowercase[0:2])
