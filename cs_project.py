"""

Amir Alleyne, Kai Alleyne, Justin Zheng, Jaren Worme
"""
from __future__ import annotations
import csv
import random
from typing import Any, Optional, Union
from collections import Counter
from plotly.graph_objs import Scatter, Figure

# Make sure you've installed the necessary Python libraries (see assignment handout
# "Installing new libraries" section)
import networkx as nx  # Used for visualizing graphs (by convention, referred to as "nx")

SIMILARITY_THRESHOLD = 0.75

COLOUR_SCHEME = [
    '#2E91E5', '#E15F99', '#1CA71C', '#FB0D0D', '#DA16FF', '#222A2A', '#B68100',
    '#750D86', '#EB663B', '#511CFB', '#00A08B', '#FB00D1', '#FC0080', '#B2828D',
    '#6C7C32', '#778AAE', '#862A16', '#A777F1', '#620042', '#1616A7', '#DA60CA',
    '#6C4516', '#0D2A63', '#AF0038'
]

LINE_COLOUR = 'rgb(210,210,210)'
VERTEX_BORDER_COLOUR = 'rgb(50, 50, 50)'
MOVIE_COLOUR = 'rgb(89, 205, 105)'
USER_COLOUR = 'rgb(105, 89, 205)'


class VertexMovie:
    """A vertex in a book review graph, used to represent a user or a book.

    Each vertex item is either movie id or series id. Both are represented as strings.


    Instance Attributes:
        - idnum: The id of the movie/series
        - kind: The type of this vertex: 'movie' or 'series'.
        - rating: The review score given by IMDb
        - title: The title of the movie or show
        - release_year: The year of release of the show or movie
        - genre: A set consisting of different genres that the movie/show is classified under
        - duration: The length of the movie/series
        - neighbours: The vertices that are adjacent to this vertex.

    Representation Invariants:
        - self not in self.neighbours
        - all(self in u.neighbours for u in self.neighbours)
        - self.kind in {'series', 'movie', 'user'}

    """
    duration: Any
    kind: str
    idnum: str
    rating: float
    rated: str
    title: str
    release_year: int
    genre: set
    duration: str
    neighbours: set[VertexMovie]

    def __init__(self, kind: Optional[str], idnum: Optional[str],
                 title: Optional[str], rating: Optional[float], release_year: Optional[int],
                 rated: Optional[str], genre: Optional[set], duration: Optional[str]) -> None:
        """Initialize a new vertex with the given attributes.

        This vertex is initialized with no neighbours.

        Preconditions:
            - kind in {'series', 'movie', 'user'}
        """
        self.idnum = idnum
        self.genre = genre
        self.rating = rating
        self.title = title
        self.kind = kind
        self.rated = rated
        self.release_year = release_year
        self.duration = duration
        self.neighbours = set()

    def degree(self) -> int:
        """Return the degree of this vertex."""
        return len(self.neighbours)

    def delete_user_vertex(self) -> None:
        """ Deletes vertex from neighbours that are users"""
        for item in self.neighbours.copy():
            if item.kind == 'user':
                self.neighbours.remove(item)

    def similarity_score_age(self, other: VertexMovie) -> float:
        """Return the  similarity score  based on year of release between this vertex and other.
            It is calculated using the absolute difference between the self.release year and
            other.release year. Since the smaller abs difference is better we divide by a very big
            number to
        >>> vert1 = VertexMovie('movie', 'vertex.idnum', "vertex.title", 0.8,\
        2000,'PG', set(), '197 mins')
        >>> vert2 = VertexMovie('movie', 'vertex.idnum', "vertex.title", 0.8,\
        2000,'PG', set(), '197 mins')
        >>> vert1.similarity_score_age(vert2)
        1.0
        >>> vert3 = VertexMovie('movie', 'vertex.idnum', "vertex.title", 0.8,\
        2018,'PG', set(), '197 mins')
        >>> vert4 = VertexMovie('movie', 'vertex.idnum', "vertex.title", 0.8,\
        2016,'TV-PG', set(), '197 mins')
        >>> vert3.similarity_score_age(vert4)
        0.8
        """
        score = abs(self.release_year - other.release_year)
        if score == 0:
            return 1.0
        elif score in range(5):
            return 0.8
        elif score in range(5, 10):
            return 0.6
        elif score in range(10, 20):
            return 0.4
        elif score in range(20, 40):
            return 0.2
        else:
            return 0.0

    def similarity_score_rated(self, other: VertexMovie) -> float:
        """Return the rated similarity score between this vertex and other.

        Similarity Scores:
        self.rated == other.rated  = 1
        Any of {'PG', 'TV-PG', 'PG-13'} = 0.75 iff self.rated and other.rated in that set
        Any of {'TV-14', 'TV-Y'} = 0.75 iff self.rated and other.rated in that set
        >>> vert1 = VertexMovie('movie', 'vertex.idnum', "vertex.title", 0.8,\
        2000,'PG', set(), '197 mins')
        >>> vert2 = VertexMovie('movie', 'vertex.idnum', "vertex.title", 0.8,\
        2000,'PG', set(), '197 mins')
        >>> vert1.similarity_score_rated(vert2)
        1.0
        >>> vert3 = VertexMovie('movie', 'vertex.idnum', "vertex.title", 0.8,\
        2000,'PG', set(), '197 mins')
        >>> vert4 = VertexMovie('movie', 'vertex.idnum', "vertex.title", 0.8,\
        2000,'TV-PG', set(), '197 mins')
        >>> vert3.similarity_score_rated( vert4)
        0.75
        """
        pg_rated = {'PG', 'TV-PG', 'PG-13'}
        children_rated = {'TV-14', 'TV-Y'}
        if self.rated == other.rated:
            return 1.0
        elif self.rated in pg_rated and other.rated in pg_rated:
            return 0.75
        elif self.rated in children_rated and other.rated in children_rated:
            return 0.75
        elif self.rated in children_rated.union(pg_rated) \
                and other.rated in children_rated.union(pg_rated):
            return 0.5
        else:
            return 0.0

    def similarity_score_genre(self, other: VertexMovie) -> float:
        """Return the similarity score  based on genre between this vertex and other.
            It is calculated based on the number of common genres assigned to the vertices, i.e.
            a perfect similarity score of 1 implies that all genres are identical, otherwise a float
            is produced based on the number of common genres divided by the number of genre's
            assigned to the film with the more genres assigned.
        >>> vert1 = VertexMovie('movie', 'vertex.idnum', "vertex.title", 0.8,\
        2000,'PG', {'Adventure','Comedy','Crime'}, '197 mins')
        >>> vert2 = VertexMovie('movie', 'vertex.idnum', "vertex.title", 0.8,\
        2000,'PG', {'Adventure','Comedy'}, '197 mins')
        >>> vert1.similarity_score_genre(vert2)
        0.6666666666666666
        >>> vert3 = VertexMovie('movie', 'vertex.idnum', "vertex.title", 0.8,\
        2000,'PG',{'Musical','Adventure', 'Romance'}, '197 mins')
        >>> vert4 = VertexMovie('movie', 'vertex.idnum', "vertex.title", 0.8,\
        2000,'PG',{'Comedy', 'Family'}, '197 mins')
        >>> vert3.similarity_score_genre( vert4)
        0.0
        """

        denominator = max(len(self.genre), len(other.genre))
        self_list = list(self.genre)
        other_list = list(other.genre)
        identical_genres = [i for i in self_list for o in other_list if i == o]
        numerator = len(identical_genres)
        return numerator / denominator

    def similarity_score_avg(self, other: VertexMovie) -> float:
        """Find and return the average similarity score between all possible similarity scores
        between two vertices.
        >>> vert1 = VertexMovie('movie', 'vertex.idnum', "vertex.title", 0.8,\
        2000,'PG',{'Comedy', 'Family'}, '197 mins')
        >>> vert2 = VertexMovie('movie', 'vertex.idnum', "vertex.title", 0.8,\
        2001,'PG-13', {'Adventure','Comedy'}, '197 mins')
        >>> vert1.similarity_score_genre(vert2)
        0.5
        """
        sum_score = self.similarity_score_age(other) + self.similarity_score_rating(other) \
            + self.similarity_score_genre(other) + self.similarity_score_rated(other)

        return sum_score / 4

    def similarity_score_rating(self, other: VertexMovie) -> float:
        """Return the similarity score between the imdb ratings
        >>> vert1 = VertexMovie('movie', 'vertex.idnum', "vertex.title", 8,\
        2000,'PG',{'Comedy', 'Family'}, '197 mins')
        >>> vert2 = VertexMovie('movie', 'vertex.idnum', "vertex.title", 6,\
        2000,'PG',{'Comedy', 'Family'}, '197 mins')
        >>> vert1.similarity_score_rating(vert2)
        0.6
        """

        score = abs(self.rating - other.rating)
        if score == 0:
            return 1
        elif score in range(2):
            return 0.8
        elif score in range(3):
            return 0.6
        elif score in range(5):
            return 0.4
        elif score in range(7):
            return 0.2
        else:
            return 0.0


class Graph:
    """A graph used to represent a movie and series network.

    Private Instance Attributes:
        - _list_for_bar_chart_titles:
            A list to accumulate titles of vertices to input into bar chart
        - _list_for_bar_chart_score:
            A list to accumulate the matching corresponding element of _list_for_bar_chart_titles.
            Can be similarity scores, review scores or dates of release
        - _vertices:
            A collection of the vertices contained in this graph.
            Maps id to _Vertex object.

    Representation Invariants:
        - len(_list_for_bar_chart_titles) <= 15
        - len(_list_for_bar_chart_score) <= 15
    """

    _vertices: dict[Any, VertexMovie]
    _list_for_bar_chart_score: list
    _list_for_bar_chart_titles: list

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}
        self._list_for_bar_chart_titles = []
        self._list_for_bar_chart_score = []

    def add_vertex(self, kind: Optional[str], idnum: Optional[str],
                   title: Optional[str], rating: Optional[float], release_year: Optional[int],
                   rated: Optional[str], genre: Optional[set], duration: Optional[str]) -> None:
        """Add a vertex with the given ID number and its related attributes to this graph.

        The new vertex is not adjacent to any other vertices.
        Do nothing if the given item is already in this graph.

        Preconditions:
            - kind in {'series', 'movie', 'user'}
        """
        if idnum not in self._vertices:
            self._vertices[idnum] = VertexMovie(kind,
                                                idnum, title, rating, release_year, rated,
                                                genre, duration)

    def delete_allvertex(self, typ: str) -> None:
        """ removes all vertex with the same 'typ' from the graph
           type = 'movie', 'series' or 'user'
        """

        for item in self._vertices.copy():
            if self._vertices[item].kind == typ:
                self._vertices.pop(item)

    def delete_all_user_edges(self) -> None:
        """ removes all neighbours from all vertex that are 'users'
        """
        for item in self._vertices:
            self._vertices[item].delete_user_vertex()

    def add_vertex_given_vertex_format(self, vertex: VertexMovie) -> None:
        """
        Add a vertex given an input already in the vertex format
        """
        self._vertices[vertex.idnum] = vertex

    def add_edge(self, id1: Any, id2: Any) -> None:
        """Add an edge between the two vertices with the given ids in this graph.

        Raise a ValueError if id1 or id2 do not appear as vertices in this graph.

        Preconditions:
            - id1 != id2
        """
        if id1 in self._vertices and id2 in self._vertices:
            v1 = self._vertices[id1]
            v2 = self._vertices[id2]

            v1.neighbours.add(v2)
            v2.neighbours.add(v1)
        else:
            raise ValueError

    def adjacent(self, id1: Any, id2: Any) -> bool:
        """Return whether id1 and id2 are adjacent vertices in this graph.

        Return False if id1 or id2 do not appear as vertices in this graph.
        """
        if id1 in self._vertices and id2 in self._vertices:
            v1 = self._vertices[id1]
            return any(v2.idnum == id2 for v2 in v1.neighbours)
        else:
            return False

    def get_neighbours(self, id_item: Any) -> set:
        """Return a set of the neighbours of the given item.

        Note that the *items* are returned, not the _Vertex objects themselves.

        Raise a ValueError if item does not appear as a vertex in this graph.
        """
        if id_item in self._vertices:
            v = self._vertices[id_item]
            return {neighbour.idnum for neighbour in v.neighbours}
        else:
            raise ValueError

    def get_all_vertices(self, kind: str = '') -> set:
        """Return a set of all vertex items in this graph.

        If kind != '', only return the items of the given vertex kind.

        Preconditions:
            - kind in {'', 'series', 'movie', 'user'}
        """
        if kind != '':
            return {v.idnum for v in self._vertices.values() if v.kind == kind}
        else:
            return set(self._vertices.keys())

    def get_all_vertices_as_vertices(self, kind: str = '') -> set:
        """Return a set of all vertex items in this graph in their vertex structure, not the ids.

        If kind != '', only return the items of the given vertex kind.

        Preconditions:
            - kind in {'', 'series', 'movie', 'user'}
        """
        if kind != '':
            return {v for v in self._vertices.values() if v.kind == kind}
        else:
            return set(self._vertices.values())

    def get_vertex(self, idnum: str) -> VertexMovie:
        """Return a vertex based on the id given"""
        if idnum in self._vertices:
            return self._vertices[idnum]
        else:
            raise ValueError

    def get_similarity_score(self, id1: Any, id2: Any,
                             score_type: str = 'rating') -> float:
        """Return the similarity score between the two given ids in this graph.

         score_type is one of 'rating', 'rated', 'age','genre' corresponding to the
        different ways of calculating movie graph vertex similarity.

        Raise a ValueError if id1 or id2 do not appear as vertices in this graph.

        Preconditions:
            - score_type in {'rating', 'rated', 'age','genre', 'average}
        """
        if id1 in self._vertices and id2 in self._vertices:
            v1 = self._vertices[id1]
            v2 = self._vertices[id2]
            if score_type == 'rated':
                return v1.similarity_score_rated(v2)
            elif score_type == 'rating':
                return v1.similarity_score_rating(v2)
            elif score_type == 'genre':
                return v1.similarity_score_genre(v2)
            elif score_type == 'average':
                return v1.similarity_score_avg(v2)
            else:
                return v1.similarity_score_age(v2)
        else:
            raise ValueError

    def recommend_films(self, film: str, limit: int,
                        score_type: str = 'rating') -> Union[str, list[str]]:
        """Return a list of up to <limit> recommended movies/series
         based on similarity to the given input.

        score_type is one of 'rating', 'rated', 'age','genre' corresponding to the
        different ways of calculating movie graph vertex similarity. The corresponding
        similarity score formula is used
        in this method (whenever the phrase "similarity score" appears below).

        The return value is a list of the titles of recommended films(Dependent on whether
        film is a movie or series), sorted in *descending order* of similarity score.
        Ties are broken in descending order of film title.
        That is, if v1 and v2 have the same similarity score, then
        v1 comes before v2 if and only if v1.item > v2.item.

        The returned list should NOT contain:
            - the input film itself
            - any film with a similarity score of 0 to the input book
            - any duplicates
            - any vertices that represents a series/movies dependent on film.
            i.e if film is a series we should only recommend series and not movies and vise versa


        Up to <limit> films are returned, starting with the film with the highest similarity score,
        then the second-highest similarity score, etc. Fewer than <limit> books are returned if
        and only if there aren't enough books that meet the above criteria.
        """
        if film in {'movie', 'series'}:
            verts = list(self.get_all_vertices(film))
            v = self._vertices[verts[0]]
            options = self.get_all_vertices(film)
            options.remove(v.idnum)

            non_zero_options = [(self.get_similarity_score(v.idnum, u, score_type), u) for u in
                                options if self.get_similarity_score(v.idnum, u, score_type) != 0]

            non_zero_options.sort(reverse=True)

            recommend = [self._vertices[non_zero_options[op][1]].title for op in
                         range(len(non_zero_options))]

            return recommend[:limit]
        else:
            v = None
            for key in self._vertices:
                if self._vertices[key].title == film:
                    v = self._vertices[key]
                    break
            if v is None:
                return "Please choose a valid movie/series"

            options = self.get_all_vertices('movie').union(self.get_all_vertices('series'))
            options.remove(v.idnum)

            if 'comparison_vertex' in options:
                options.remove('comparison_vertex')

            non_zero_options = [(self.get_similarity_score(v.idnum, u, score_type), u) for u in
                                options if self.get_similarity_score(v.idnum, u, 'average') != 0]

            non_zero_options.sort(reverse=True)

            recommend = [self._vertices[non_zero_options[op][1]].title for op in
                         range(len(non_zero_options))]

            return recommend[:limit]

    def recommend_combobox(self, film_type: str, limit: int,
                           score_types: list[str]) -> Union[str, list[str]]:
        """Return a list of up to <limit> recommended movies/series
         based on similarity to the given type, and genres.

        """
        if score_types[len(score_types) - 1][0] == '5':
            a, b = 1, 5
        else:
            rnge = score_types[len(score_types) - 1].split('-')
            a, b = int(rnge[0]), int(rnge[1])
        v = VertexMovie(film_type, 'comparison_vertex', None,
                        None, None, None, set(score_types[:-1]), None)
        self.add_vertex(film_type, 'comparison_vertex', None, None, None, None,
                        set(score_types[:-1]), None)

        options = [x for x in self.get_all_vertices(film_type) for g in score_types[:-1]
                   if g in self._vertices[x].genre
                   and x != v.idnum and self._vertices[x].rating in range(a, b)]
        non_zero_options = [(self.get_similarity_score(v.idnum, u, 'genre'), u) for u in
                            options if self.get_similarity_score(v.idnum, u, 'genre') != 0]
        non_zero_options.sort(reverse=True)

        recommend = [self._vertices[non_zero_options[op][1]].title for op in
                     range(len(non_zero_options))]
        recommend_no_dups = no_dups(recommend)
        return recommend_no_dups[:limit]

    def release_year(self, vertex: str) -> int:
        """
        A method to publicly access a given vertex's release year

        >>> test_graph = Graph()
        >>> test_graph.add_vertex('movie', '01', 'Movie1', 10, 2021, 'pg-13', {'comedy'}, '120')
        >>> test_graph.release_year('01')
        2021
        """
        if vertex in self._vertices:
            v = self._vertices[vertex]
            return v.release_year
        else:
            raise ValueError('Movie entered not in graph')

    def get_attribute_tuple_set_for_clusters(self, attribute_type: str) -> list[tuple]:
        """
        Returns a list of tuples of every element in the graph.
        The first element in the tuple is the vertex
        The second element in the tuple is it's attribute
        attributes can be release year, genre, rating or duration
        """
        curr_list = []

        if attribute_type not in ['release year', 'genre', 'rating', 'duration']:
            raise ValueError('Invalid attribute type entered')
        elif attribute_type == 'release year':
            for element in self._vertices:
                curr_tuple = (self._vertices[element], self._vertices[element].release_year)
                if curr_tuple[1] is not None:
                    curr_list.append(tuple(curr_tuple))
        elif attribute_type == 'genre':
            for element in self._vertices:
                curr_tuple = (self._vertices[element], self._vertices[element].genre)
                if curr_tuple[1] is not None:
                    curr_list.append(tuple(curr_tuple))
        elif attribute_type == 'rating':
            for element in self._vertices:
                curr_tuple = (self._vertices[element], self._vertices[element].rating)
                if curr_tuple[1] is not None:
                    curr_list.append(tuple(curr_tuple))
        else:  # attribute_type == 'duration'
            for element in self._vertices:
                curr_tuple = (self._vertices[element], self._vertices[element].duration)
                if curr_tuple[1] is not None:
                    curr_list.append(tuple(curr_tuple))

        return curr_list

    def get_list_review_scores_all(self) -> list[list]:
        """
        Generates a list containing two lists, where the first list contains movie names and the
        second contains review scores for the whole graph to be used for the bar chart generator.
        The first element of the first list corresponds to the first element of the second and so
        on.
        Since we are capping the amount of elements at 15, raise an Error if more than 15
        elements are going to be added to each sublist
        """
        if len(self.get_all_vertices()) > 15:
            raise ValueError('possesses a number of vertices which exceeds the limit')
        else:
            list_a = []
            list_b = []
            for vertex in self.get_all_vertices_as_vertices():
                list_a.append(vertex.title)
                list_b.append(vertex.rating)
            return [list_a, list_b]

    def get_movie_id_given_title(self, title: str) -> Any:
        """
        Lets the user input a movie title to get the movie's id num.
        If the movie title is unique, it will return just the id .
        Since there may be more than one movie with the same name, all options for that movie
        are returned in the output list as a tuple with their id and year of release for the user
        to decide which one they want, with a message telling the user this.

        >>> test_graph = load_review_graph("disney_plus_shows.csv", 'users.csv')
        >>> test_graph.get_movie_id_given_title('Alice in Wonderland')
        ['multiple movies found, choose id of correct year of release', ('tt0043274', 1951), ('tt1014759', 2010)]
        >>> test_graph.get_movie_id_given_title('A Goofy Movie')
        'tt0113198'
        """
        list_so_far = ['multiple movies found, choose id of correct year of release']
        for vertex in self.get_all_vertices_as_vertices():
            if vertex.title == title and vertex.kind == 'movie':
                id_year_tuple = (vertex.idnum, vertex.release_year)
                list_so_far.append(id_year_tuple)

        if not list_so_far:  # movie not found in the graph
            raise ValueError('Movie entered not in graph')
        elif len(list_so_far) == 2:  # one movie with given title
            return list_so_far[1][0]
        else:  # multiple titles found
            return list_so_far

    def add_item_for_bar_chart(self, movie_id: str) -> None:
        """Update _list_for_bar_chart_titles and _list_for_bar_chart_score by entering the movie's
        unique id_num
        preconditions:
            - self._vertices[movie_id].kind == 'movie'

        >>> test_graph = load_review_graph("disney_plus_shows.csv", 'users.csv')
        >>> test_graph.add_item_for_bar_chart('tt0113198')
        >>> test_graph._list_for_bar_chart_titles
        ['A Goofy Movie']
        >>> test_graph._list_for_bar_chart_score
        [6.8]
        >>> test_graph.add_item_for_bar_chart('tt0043274')
        >>> test_graph._list_for_bar_chart_titles
        ['A Goofy Movie', 'Alice in Wonderland']
        >>> test_graph._list_for_bar_chart_score
        [6.8, 7.4]
        """
        if movie_id in self.get_all_vertices():
            self._list_for_bar_chart_titles.append(self._vertices[movie_id].title)
            self._list_for_bar_chart_score.append(self._vertices[movie_id].rating)
        else:
            raise ValueError('Movie entered not in graph')

    def generate_list_for_bar_chart(self) -> list[list]:
        """Generates a list of lists needed to generate the bar chart with the given bar chart
        lists
        >>> test_graph = load_review_graph("disney_plus_shows.csv", 'users.csv')
        >>> test_graph.add_item_for_bar_chart('tt0113198')
        >>> test_graph.add_item_for_bar_chart('tt0043274')
        >>> test_graph.generate_list_for_bar_chart()
        [['A Goofy Movie', 'Alice in Wonderland'], [6.8, 7.4]]
        """
        return [self._list_for_bar_chart_titles, self._list_for_bar_chart_score]

    def reset_bar_chart_lists(self) -> None:
        """
        Reset _list_for_bar_chart_titles and _list_for_bar_chart_score back to empty lists

        >>> test_graph = load_review_graph("disney_plus_shows.csv", 'users.csv')
        >>> test_graph.add_item_for_bar_chart('tt0113198')
        >>> test_graph.add_item_for_bar_chart('tt0043274')
        >>> test_graph._list_for_bar_chart_titles
        ['A Goofy Movie', 'Alice in Wonderland']
        >>> test_graph._list_for_bar_chart_score
        [6.8, 7.4]
        >>> test_graph.reset_bar_chart_lists()
        >>> test_graph._list_for_bar_chart_titles
        []
        >>> test_graph._list_for_bar_chart_score
        []
        """
        self._list_for_bar_chart_titles = []
        self._list_for_bar_chart_score = []

    def to_networkx(self, max_vertices: int = 5000) -> nx.Graph:
        """Convert this graph into a networkx Graph.

        max_vertices specifies the maximum number of vertices that can appear in the graph.
        (This is necessary to limit the visualization output for large graphs.)
        """
        graph_nx = nx.Graph()
        lst = list(self.get_all_vertices('movie'))

        accumulator = set()
        for i in range(len(lst)):
            accumulator.add(self._vertices[lst[i]])
        final = list(accumulator)
        for v in final:
            graph_nx.add_node(v.idnum, kind=v.kind)

            for u in v.neighbours:
                if graph_nx.number_of_nodes() < max_vertices:
                    graph_nx.add_node(u.idnum, kind=u.kind)

                if u.idnum in graph_nx.nodes:
                    graph_nx.add_edge(v.idnum, u.idnum)

            if graph_nx.number_of_nodes() >= max_vertices:
                break

        return graph_nx

    def trending_films(self) -> list:
        """ Returns a list of the top 15 trending films(movies or series). Films are declared to be
        trending when they most frequently appear as users' neighbours
        (i.e. they have been watched by users)."""
        users = self.get_all_vertices('user')
        all_watched = []
        for user in users:
            user_vertex = self.get_vertex(user)
            all_watched.extend(list(user_vertex.neighbours))

        filtered = list(all_watched.copy())

        trending_vertices = []
        for _ in range(15):
            data = Counter(filtered)
            rank1 = max(filtered, key=data.get)  # finds the most commonly occurring element
            trending_vertices.append(rank1)
            filtered = list(filter(lambda a: a != rank1,
                                   filtered))  # removes element from list for subsequent reps

        trending_titles = []
        for film_vertex in trending_vertices:
            name = film_vertex.title
            trending_titles.append(name)

        return trending_titles


def load_review_graph(disney_file: str, user_file: str) -> Graph:
    """Return a book review graph corresponding to the given datasets.

    The movie and series graph stores one vertex for each show in the datasets.
    Each vertex stores as its item either a item, kind, id, title, rating, release_year,
    genre. Use the "kind" _Vertex attribute to differentiate between the two vertex types.

    Edges represent a review between a user and a book. In this graph, each edge
    only represents the existence of a review---IGNORE THE REVIEW SCORE in the
    datasets, as we don't have a way to represent these scores (yet).

    """
    graph = Graph()
    disney_dict = read_disney_plus(disney_file)
    user_lst = read_user(user_file)
    for key in disney_dict:
        vertex = disney_dict[key]

        graph.add_vertex(vertex.kind, vertex.idnum, vertex.title, vertex.rating,
                         vertex.release_year,
                         vertex.rated, vertex.genre, vertex.duration)
    vert_lst = graph.get_all_vertices('movie').union(graph.get_all_vertices('series'))

    # Adds edges between movies if these two movies' avg similarity score
    # surpass the similarity threshold
    for mos in vert_lst:  # mos means movie or series
        for mos2 in vert_lst:
            v1, v2 = graph.get_vertex(mos), graph.get_vertex(mos2)
            # v1, v2 = graph._vertices[mos], graph._vertices[mos2]
            if mos != mos2 and not graph.adjacent(v1, v2) and \
                    v1.similarity_score_avg(v2) >= SIMILARITY_THRESHOLD:
                graph.add_edge(mos, mos2)

    for user in user_lst:
        graph.add_vertex('user', user, None, None, None, None, set(), None)
        lst = list(vert_lst.copy())
        for _ in range(random.randint(30, 70)):
            random_film = random.choice(lst)
            lst.remove(random_film)
            graph.add_edge(user, random_film)
    # CREATE EDGES BASED ON AVERAGE SCORE(between two movies)(KAI)
    # create edges between user and movie (AMIR)
    return graph


def load_review_graph_for_clusters(disney_file: str, user_file: str) -> Graph:
    """Return a book review graph corresponding to the given datasets.

    The movie and series graph stores one vertex for each show in the datasets.
    Each vertex stores as its item either a item, kind, id, title, rating, release_year,
    genre. Use the "kind" _Vertex attribute to differentiate between the two vertex types.

    Edges represent a review between a user and a book. In this graph, each edge
    only represents the existence of a review---IGNORE THE REVIEW SCORE in the
    datasets, as we don't have a way to represent these scores (yet).

    """
    graph = Graph()
    disney_dict = read_disney_plus(disney_file)
    user_lst = read_user(user_file)
    for key in disney_dict:
        vertex = disney_dict[key]

        graph.add_vertex(vertex.kind, vertex.idnum, vertex.title, vertex.rating,
                         vertex.release_year,
                         vertex.rated, vertex.genre, vertex.duration)

    for user in user_lst:
        graph.add_vertex('user', user, None, None, None, None, set(), None)
        lst = list(graph.get_all_vertices('movie').union(graph.get_all_vertices('series')).copy())
        for _ in range(random.randint(30, 70)):
            random_film = random.choice(lst)
            lst.remove(random_film)
            graph.add_edge(user, random_film)
    return graph


def read_disney_plus(disney_file: str) -> dict[str, VertexMovie]:
    """
    Read the disney plus file and make an appropriate dictionary mapping the id to the vertex
    """
    disney_dict = {}
    with open(disney_file) as csv_file:
        reader1 = csv.reader(csv_file)
        next(reader1)
        for row in reader1:
            if row[0] not in {',', '', 'N/A'} and row[5] not in {',', '', 'N/A'} \
                    and row[17] not in {',', '', 'N/A'} \
                    and row[4] not in {'APPROVED', 'Approved', 'UNRATED', 'Unrated', 'Passed',
                                       'NOT RATED', 'N/A', 'TV-Y7-FV', 'TV-Y7', "Not Rated",
                                       'PASSED'} \
                    and row[3] in {'series', 'movie', 'user'}:
                idnum = row[0]
                title = row[1]
                kind = row[3]
                rated = row[4]
                year_so_far = ''
                for x in row[5]:
                    # breakpoint()
                    if len(year_so_far) != 4:
                        year_so_far += x

                release_year = int(float(year_so_far))
                genre = set(stri.strip() for stri in row[9].split(','))
                rating = float(row[17])
                duration = row[8]
                disney_dict[idnum] = VertexMovie(kind, idnum,
                                                 title, rating, release_year, rated, genre,
                                                 duration)
        return disney_dict


def read_user(user_file: str) -> list:
    """
    Read the disney plus file and make an appropriate dictionary mapping the id to the vertex
    """
    user_lst = []
    with open(user_file) as csv_file:
        reader1 = csv.reader(csv_file)
        next(reader1)
        for row in reader1:
            user_lst.append(row[0])
            if len(user_lst) > 5000:
                break
    return user_lst


def no_dups(recommend: list) -> list:
    """Remove the duplicates"""
    new = []
    for x in recommend:
        if x not in new:
            new.append(x)
    return new


def generate_cluster_movie_release_year(vertices_by_age: list[tuple]) -> Graph:
    """
    This function takes in a list of tuples of vertex id's and their year of release and creates a
    weighted graph of clusters depending on that date
    """
    curr_graph = Graph()

    # first update graph with all vertices inputted
    for item in vertices_by_age:
        curr_graph.add_vertex_given_vertex_format(item[0])

    # then add edges between all with identical release years
    for item in vertices_by_age:
        for vertex in curr_graph.get_all_vertices_as_vertices():
            if item[0] != vertex and vertex.release_year == item[1]:
                curr_graph.add_edge(vertex.idnum, item[0].idnum)

    return curr_graph


def generate_cluster_movie_rating(vertex_list_by_rating: list[tuple]) -> Graph:
    """
    This function takes in a list of tuples of vertex id's and their year of release and creates a
    weighted graph of clusters depending on that date
    """
    curr_graph = Graph()

    # first update graph with all vertices inputted
    for item in vertex_list_by_rating:
        curr_graph.add_vertex_given_vertex_format(item[0])

    # then add edges between all with identical release years
    for item in vertex_list_by_rating:
        for vertex in curr_graph.get_all_vertices_as_vertices():
            if item[0] != vertex and vertex.rating == item[1]:
                curr_graph.add_edge(vertex.idnum, item[0].idnum)

    return curr_graph


def generate_cluster_movie_duration(vertex_list_by_duration: list[tuple]) -> Graph:
    """
    This function takes in a list of tuples of vertex id's and their year of release and creates a
    weighted graph of clusters depending on that date
    """
    curr_graph = Graph()

    # first update graph with all vertices inputted
    for item in vertex_list_by_duration:
        curr_graph.add_vertex_given_vertex_format(item[0])

    # then add edges between all with identical release years
    for item in vertex_list_by_duration:
        for vertex in curr_graph.get_all_vertices_as_vertices():
            if item[0] != vertex and vertex.duration == item[1]:
                curr_graph.add_edge(vertex.idnum, item[0].idnum)

    return curr_graph


def generate_cluster_movie_genre(vertex_list_by_genre: list[tuple]) -> Graph:
    """
    This function takes in a list of tuples of vertex id's and their year of release and creates a
    weighted graph of clusters depending on that date
    """
    curr_graph = Graph()

    # first update graph with all vertices inputted
    for item in vertex_list_by_genre:
        curr_graph.add_vertex_given_vertex_format(item[0])

    # then add edges between all with identical release years
    for item in vertex_list_by_genre:
        for vertex in curr_graph.get_all_vertices_as_vertices():
            if item[0] != vertex and vertex.genre == item[1]:
                curr_graph.add_edge(vertex.idnum, item[0].idnum)

    return curr_graph


def visualize_graph_clusters(graph: Graph, clusters: list[set],
                             layout: str = 'spring_layout',
                             max_vertices: int = 5000,
                             output_file: str = '') -> None:
    """Visualize the given graph, using different colours to illustrate the different clusters.

    Hides all edges that go from one cluster to another. (This helps the graph layout algorithm
    positions vertices in the same cluster close together.)

    Same optional arguments as visualize_graph (see that function for details).
    """
    graph_nx = graph.to_networkx(max_vertices)
    all_edges = list(graph_nx.edges)
    for edge in all_edges:
        # Check if edge is within the same cluster
        if any((edge[0] in cluster) != (edge[1] in cluster) for cluster in clusters):
            graph_nx.remove_edge(edge[0], edge[1])

    pos = getattr(nx, layout)(graph_nx)

    x_values = [pos[p][0] for p in graph_nx.nodes]
    y_values = [pos[p][1] for p in graph_nx.nodes]
    labels = list(graph_nx.nodes)

    colors = []
    for k in graph_nx.nodes:
        for i, c in enumerate(clusters):
            if k in c:
                colors.append(COLOUR_SCHEME[i % len(COLOUR_SCHEME)])
                break
        else:
            colors.append(MOVIE_COLOUR)

    x_edges = []
    y_edges = []
    for edge in graph_nx.edges:
        x_edges += [pos[edge[0]][0], pos[edge[1]][0], None]
        y_edges += [pos[edge[0]][1], pos[edge[1]][1], None]

    trace3 = Scatter(x=x_edges,
                     y=y_edges,
                     mode='lines',
                     name='edges',
                     line=dict(color=LINE_COLOUR, width=1),
                     hoverinfo='none'
                     )
    trace4 = Scatter(x=x_values,
                     y=y_values,
                     mode='markers',
                     name='nodes',
                     marker=dict(symbol='circle-dot',
                                 size=5,
                                 color=colors,
                                 line=dict(color=VERTEX_BORDER_COLOUR, width=0.5)
                                 ),
                     text=labels,
                     hovertemplate='%{text}',
                     hoverlabel={'namelength': 0}
                     )

    data1 = [trace3, trace4]
    fig = Figure(data=data1)
    fig.update_layout({'showlegend': False})
    fig.update_xaxes(showgrid=False, zeroline=False, visible=False)
    fig.update_yaxes(showgrid=False, zeroline=False, visible=False)
    fig.show()

    if output_file == '':
        fig.show()
    else:
        fig.write_image(output_file)


def visualize_graph(graph_input: Graph,
                    layout: str = 'spring_layout',
                    max_vertices: int = 5000,
                    output_file: str = '') -> None:
    """Use plotly and networkx to visualize the given graph.

    Optional arguments:
        - layout: which graph layout algorithm to use
        - max_vertices: the maximum number of vertices that can appear in the graph
        - output_file: a filename to save the plotly image to (rather than displaying
            in your web browser)
    """

    graph_input.delete_allvertex('user')
    graph_input.delete_all_user_edges()
    graph_nx = graph_input.to_networkx(max_vertices)

    # graph_nx.remove_nodes_from(graph.get_all_vertices('user'))

    pos = getattr(nx, layout)(graph_nx)

    x_values = [pos[k][0] for k in graph_nx.nodes]
    y_values = [pos[k][1] for k in graph_nx.nodes]
    labels = list(graph_nx.nodes)
    kinds = [graph_nx.nodes[k]['kind'] for k in graph_nx.nodes]

    colours = [MOVIE_COLOUR if kind == 'movie' else USER_COLOUR for kind in kinds]

    x_edges = []
    y_edges = []

    for edge in graph_nx.edges:
        x_edges += [pos[edge[0]][0], pos[edge[1]][0], None]
        y_edges += [pos[edge[0]][1], pos[edge[1]][1], None]

    trace3 = Scatter(x=x_edges,
                     y=y_edges,
                     mode='lines',
                     name='edges',
                     line=dict(color=LINE_COLOUR, width=1),
                     hoverinfo='none',
                     )
    trace4 = Scatter(x=x_values,
                     y=y_values,
                     mode='markers',
                     name='nodes',
                     marker=dict(symbol='circle-dot',
                                 size=5,
                                 color=colours,
                                 line=dict(color=VERTEX_BORDER_COLOUR, width=0.5)
                                 ),
                     text=labels,
                     hovertemplate='%{text}',
                     hoverlabel={'namelength': 0}
                     )

    data1 = [trace3, trace4]
    fig = Figure(data=data1)
    fig.update_layout({'showlegend': False})
    fig.update_xaxes(showgrid=False, zeroline=False, visible=False)
    fig.update_yaxes(showgrid=False, zeroline=False, visible=False)

    if output_file == '':
        fig.show()
    else:
        fig.write_image(output_file)


def display_bar_chart(elements: list[list]) -> None:
    """
    Function to display a bar chart of up to 15 movies comparing their IMDB rating.
    Elements is a list of movie names and their ratings such that element[0[0]]
    corresponds to elements[1[0]] and so on
    I chose 15 so the bar charts would not get messy with too many things being displayed

    Preconditions:
        - len(elements) == 2
        - len(elements[0]) == len(elements[1])
        - len(elements[0]) <= 15
        - elements != []
    """
    import plotly.graph_objects as go

    names = elements[0]
    scores = elements[1]

    fig = go.Figure(
        data=[go.Bar(x=names, y=scores)],
        layout=go.Layout(
            title=go.layout.Title(text="Bar Chart Comparing Your Movies in Terms of IMDB rating")
        )
    )

    fig.show()


if __name__ == '__main__':
    import python_ta.contracts

    python_ta.check_errors()
    import doctest

    doctest.testmod()

    # import python_ta
    #
    # python_ta.check_all(config={
    #     'extra-imports': ['csv', 'random', 'collections', 'plotly.graph_objs', 'networkx'],
    #     'allowed-io': ['read_user', 'read_disney_plus'],
    #     'max-line-length': 100,
    #     'disable': ['E1136']
    # })
