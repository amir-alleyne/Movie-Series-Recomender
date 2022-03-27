"""
This file is Copyright (c) 2021 Amir Alleyne, Kai Alleyne, Jaren Worme, Justin Zheng
"""
import tkinter as tk
from tkinter import Frame, Entry, Button, LEFT
from tkinter import ttk
from tkinter import messagebox
from typing import Union
import cs_project

GRAPH = cs_project.load_review_graph("disney_plus_shows.csv", 'users.csv')


def labelmaker(win: Frame) -> None:
    """ Creates Labels for the dropdown menus"""
    ttk.Label(win, text="Select Your Type :",
              font=("Times New Roman", 10)).grid(column=0,
                                                 row=1, padx=10, pady=20)

    ttk.Label(win, text="Select Your Genre :",
              font=("Times New Roman", 10)).grid(column=0,
                                                 row=2, padx=10, pady=15)

    ttk.Label(win, text="Select Your Genre :",
              font=("Times New Roman", 10)).grid(column=0,
                                                 row=3, padx=10, pady=15)

    ttk.Label(win, text="Select Your Genre :",
              font=("Times New Roman", 10)).grid(column=0,
                                                 row=4, padx=10, pady=15)

    ttk.Label(win, text="Select Rating Range:",
              font=("Times New Roman", 10)).grid(column=0,
                                                 row=5, padx=10, pady=15)


def clearframe(win: Frame) -> None:
    """ Destroy all widgets from Frame. This function acts as a page 'refresher'.

    """

    for widget in win.winfo_children():
        widget.destroy()


def page1(win: Frame) -> None:
    """Page 1 of Tkinter Window """

    clearframe(win)

    labelmaker(win)

    list1 = placecombobox(win)
    btn = ttk.Button(win, text="Find your Recommended Movies", command=lambda: checkmovies(list1))
    btn.grid(row=1, column=5)


def page2(win: Frame) -> None:
    """Page 2 of Tkinter Window """
    clearframe(win)
    # adding of single line text box
    edit = Entry(win)

    # positioning of text box
    edit.grid(column=0, row=0)

    # setting focus
    edit.focus_set()
    butt = Button(win, text='Find by title', command=lambda: find(edit))
    butt.grid(column=1, row=0)


def find(search_box: tk.Entry) -> None:
    """Takes in user input and recommend films based on user input """
    string = search_box.get()
    recommend_movies = GRAPH.recommend_films(string, 10, 'genre')
    messagebox.showinfo("Your Movies Are", recommend_movies)


def page3(win: Frame) -> None:
    """Page 3 of Tkinter Window """
    clearframe(win)
    btn = ttk.Button(win, text="Visualise our Graph", command=visualiser_graph)

    btn.grid(row=2, column=4)
    lst = cluster_dropdownmenu(win)

    btn1 = ttk.Button(win, text="Visualise our Graph Clusters",
                      command=lambda: visualiser_cluster(lst))

    btn1.place(x=250, y=100)

    btn2 = ttk.Button(win, text="Visualise our Bar Charts", command=bar_charts)
    btn2.grid(row=2, column=6)


def cluster_dropdownmenu(win: Frame) -> list:
    """Creates and Places comboboxes at proper positions.
       Returns a list of comboboxes placed.

    """
    templist = list()
    ttk.Label(win, text="Select Type of Cluster :",
              font=("Times New Roman", 10)).place(x=0, y=100)

    cmb = ttk.Combobox(win, width="10", values=("release year", "rating", "duration", "genre"))
    cmb.place(x=150, y=100)

    templist.append(cmb)

    return templist


def visualiser_cluster(lst: list) -> None:
    """ Visualises Graph Clusters in a new window"""
    string = lst[0].get().lower()

    stringset = {'release year', 'rating', 'duration', 'genre'}

    if string not in stringset:
        messagebox.showinfo("ERROR", 'Please Choose a cluster type')
        return

    graph1 = cs_project.load_review_graph_for_clusters("disney_plus_shows.csv", 'users.csv')
    new_list = graph1.get_attribute_tuple_set_for_clusters(string)

    if string == 'release year':
        new_graph = cs_project.generate_cluster_movie_release_year(new_list)
    elif string == 'rating':
        new_graph = cs_project.generate_cluster_movie_rating(new_list)
    elif string == 'duration':
        new_graph = cs_project.generate_cluster_movie_duration(new_list)
    else:
        new_graph = cs_project.generate_cluster_movie_genre(new_list)

    cs_project.visualize_graph(new_graph)


def visualiser_graph() -> None:
    """ Visualises Graph in a new window"""
    graph1 = cs_project.load_review_graph("disney_plus_shows.csv", 'users.csv')
    cs_project.visualize_graph(graph1)


def bar_charts() -> None:
    """ Visualise Bar Charts in a new window"""
    graph = cs_project.Graph()
    graph.add_vertex('movie', 'tt6139732', 'Aladdin', 7, 2019, 'PG',
                     {'Adventure', 'Family', 'Fantasy', 'Musical', 'Romance'}, '128')
    graph.add_vertex('movie', 'tt12076020',
                     'A Celebration of the Music from Coco', 7.6, 2020, 'N/A', {'music'}, 'N/A')
    graph.add_vertex('movie', 'tt0287003',
                     'A Tale of Two Critters', 7.1, 1977, 'G', {'Adventure', 'Family'}, '48')
    graph.add_vertex('movie', 'tt0417415',
                     'Aliens of the Deep', 6.4, 2005, 'G', {'Documentary', 'Family'}, '100')
    graph.add_vertex('movie', 'tt0381006',
                     "America's Heart & Soul", 4.8, 2004, 'PG', {'Documentary'}, '84')

    graph.add_vertex('movie', 'tt0266543', 'Finding Nemo',
                     8.1, 2003, 'G', {'Comedy', 'Adventure', 'Animation', 'Family'}, '100')
    elements_list = graph.get_list_review_scores_all()

    cs_project.display_bar_chart(elements_list)


def page4(win: Frame) -> None:
    """Page 4 of Tkinter Window """
    clearframe(win)
    btn = ttk.Button(win, text="Display Trending Movies", command=lambda: find_trending(win))
    btn.grid(row=1, column=5)


def find_trending(win: Frame) -> None:
    """ This function calls GRAPH.trending films and
    displays trending films onto the tkinter window """
    trending_films = GRAPH.trending_films()

    for i in range(len(trending_films)):
        txt = str(trending_films[i])
        label = ttk.Label(win, text=txt,
                          font=("Times New Roman", 10)).grid(column=0, row=i + 1, padx=10)
        if label is not None:
            label.pack(side=LEFT)


def placecombobox(win: Frame) -> list:
    """Creates and Places comboboxes at proper positions.
       Returns a list of comboboxes placed.

    """

    templist = list()
    cmb = ttk.Combobox(win, width="10", values=("Movie", "Series"))
    cmb.grid(column=2, row=1, padx=10, pady=20)
    templist.append(cmb)

    for i in range(3):
        cmb = ttk.Combobox(win, width="10",
                           values=("Comedy", "Adventure", "Action",
                                   "Romance", "Sci-Fi", "Sport", "Crime",
                                   "Fantasy", "Animation", "Drama", "Musical", "Family"))
        cmb.grid(column=2, row=1 + i + 1, padx=10, pady=20)
        templist.append(cmb)

    cmb = ttk.Combobox(win, width="10", values=("8-10", "7-8",
                                                "6-7", "5 and below"))
    cmb.grid(column=2, row=5, padx=10, pady=20)
    templist.append(cmb)

    return templist


def findmovie(lst: list) -> Union[str, list]:
    """Takes in a list of comboboxes.
    Loads graph from read_disney_plus in get_graph_data
    Takes in user input of what type, genere and rating of the flim they want.
    Returns a set of strings of recommended movies

    """

    type_set = {'Movie', 'Series'}
    genre_set = {"Comedy", "Adventure", "Action", "Romance", "Sci-Fi", "Sport", "Crime",
                 "Fantasy", "Animation", "Drama", "Musical", "Family"}
    rating_set = {"8-10", "7-8", "6-7", "5 and below"}

    movielist = list()
    if lst[0].get() not in type_set:
        return "Choose a Movie/Series"

    if lst[-1].get() not in rating_set:
        return " Choose an appropriate rating"

    if all({x.get() not in genre_set for x in lst[1:4]}):
        return " Choose a Genre"

    type_film = lst[0].get().lower()

    # Movie or Series

    for cmb in lst[1:]:
        value = cmb.get()  # Genre or Rating
        movielist.append(value)

    movies_recommended = GRAPH.recommend_combobox(type_film, 100, movielist)

    if len(movies_recommended) == 0:
        return 'There are no such recommended movies'

    return movies_recommended


def checkmovies(lst: list) -> None:
    """Function for user to activate by pressing the button.
       Shows a Recommended Movies in a messagebox
     """
    string = findmovie(lst)
    messagebox.showinfo("Your Movies Are", string)


def mainloop1() -> None:
    """ Main loop to run the program """

    window = tk.Tk()
    window.title('Movie Recommender')

    window.geometry("500x500")

    menuframe = tk.Frame(window, bg='red')
    menuframe.pack(side="top", expand=False, fill="both")

    itemframe = tk.Frame(window, bg='lightblue')
    itemframe.pack(side="top", expand=True, fill="both")

    page_one = tk.Button(menuframe,
                         text='Choose your Movie Category', command=lambda: page1(itemframe))
    page_one.grid(column=0, row=0)

    page_two = tk.Button(menuframe, text='Films You Might Like', command=lambda: page2(itemframe))
    page_two.grid(row=0, column=1)

    page_three = tk.Button(menuframe, text='Graph Visualisation', command=lambda: page3(itemframe))
    page_three.grid(row=0, column=2)

    page_four = tk.Button(menuframe, text='Trending Films', command=lambda: page4(itemframe))
    page_four.grid(row=0, column=3)

    window.mainloop()


mainloop1()

if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'extra-imports': ['tkinter', 'cs_project'],  # the names (strs) of imported modules
        'allowed-io': [],  # the names (strs) of functions that call print/open/input
        'max-line-length': 100,
        'disable': ['E1136']
    })
