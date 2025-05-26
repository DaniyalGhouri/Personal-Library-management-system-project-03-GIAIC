import streamlit as st
import pandas as pd 
import json
import os
from datetime import datetime   
import time
import random
import plotly.express as px 
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests

# set page config
st.set_page_config(
    page_title="Personal Library Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)
# custom css
st.markdown(
    """
    <style>
    .main-header{
        font-size: 2.5rem;
        font-weight: bold;
        color: #4B0082;
        text-align: center;
        margin-top: 20px;
        margin-bottom: 20px;
        background-color: #f0f2f5;
    }
    .sub-header{
        font-size: 1.5rem;
        font-weight: bold;
        color: #4B0082;
        text-align: center;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .success-message{
        padding: 10px;
        background-color: #d4edda;
        border left: 5px solid #c3e6cb;
        border-radius: 5px;
        }
    .warning-message{
        padding: 10px;
        background-color: #fff3cd;
        border left: 5px solid #ffeeba;
        border-radius: 5px;
        }
        .book-card {
        background-color: #f8f9fa;  
        border-radius: 10px;
        padding: 20px;  
        margin: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
        }
        book-card:hover {
        transform: translate(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
        }
        .red-badge {
        background-color: #dc3545;
        color: white;   
        padding: 5px 10px;
        border-radius: 5px; 
        font-size: 0.8rem;
        font-weight: bold;
        }
        .unread-badge {
        background-color: #007bff;
        color: white;   
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 0.8rem;
        font-weight: bold;
        }
        .action-button{
        margin-right : 0.5rem;
        }
        .stButton>button {
        border-radius: 5px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

if 'library' not in st.session_state:
    st.session_state.library = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'book_added' not in st.session_state:
    st.session_state.book_added = False
if 'book_remove' not in st.session_state:
    st.session_state.book_remove = False
if 'current_view' not in st.session_state:
    st.session_state.current_view = "library"

# load library
def load_library():
    try:
        if os.path.exists("library.json"):
            with open("library.json", "r") as file:
                st.session_state.library = json.load(file)
                return True
            return False
    except Exception as e:
        st.error(f"Error loading library: {e}")
        return False
    
# save library
def save_library():
    try:
        with open("library.json", "w") as file:
            json.dump(st.session_state.library, file)
            return True
    except Exception as e:
        st.error(f"Error saving library: {e}")
        return False
    
# add book to library
def add_book(title,Author,Genre,read_status,publication_year):
    book = {
        "title": title,
        "Author": Author,
        "Genre": Genre,
        "Read-Status": read_status,
        "Publication_year":publication_year,
       " added_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    st.session_state.library.append(book)
    save_library()
    st.session_state.book_added = True
    time.sleep(0.5) #animation delay

# remove book from library
def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library()
        st.session_state.book_remove = True
    return False

# search book
def search_book(search_term, search_by):
    search_term = search_term.lower()
    results = []

    for book in st.session_state.library:
        if search_by == "Title" and search_term in book["title"].lower():
            results.append(book)
        elif search_by == "Author" and search_term in book["author"].lower():
            results.append(book)
        elif search_by == "Genre" and search_term in book["genre"].lower():
            results.append(book)
    st.session_state.search_results = results
        
# calculate library statistics
def get_lib_stats():
    total_books = len(st.session_state.library)
    read_books = len(1 for book in st.session_state.library if book["Read-Status"] == "Read")
    read_percent = (read_books / total_books) *100 if total_books > 0 else 0

    genres = {}
    decades = {}
    authors = {}
    for book in st.session_state.library:
        if book["Genre"] in genres:
            genres[book["Genre"]] += 1
        else:
            genres[book["Genre"]] = 1
        if book["Author"] in authors:
            authors[book["Author"]] += 1
        else:
            authors[book["Author"]] = 1
        decades = (book["Publication_Year"]//10) * 10
        if decades in decades:
            decades[decades] += 1
        else:
            decades[decades] = 1

    # sort by count

    genres = dict(genres.items() , key=lambda x: x[1], reverse=True)
    authors = dict(authors.items() , key=lambda x: x[1], reverse=True)
    decades = dict(decades.items(), key=lambda x: x[0])

    return{
        "total_books": total_books,
        "read_books": read_books,
        "read_percent": read_percent,
        "genres": genres,
        "authors": authors,
        "decades": decades,        
    }

def create_visualizations(stats):
    if stats["total_books"] > 0:
        fig_read_status = go.Figure(data = [go.pie(
            labels = ["Read", "unread"],
            values = [stats["read_books"], stats["Total_books"] - stats["read_books"]],
            hole = 0.4,
            marker_colors = ["#0015F9", "#FF000D"],
        )])
        fig_read_status.update_layout(
            title_text = "Read VS Unread Books",
            showlegend = True,
            hieght = 400,
        )
        st.plotly_chart(fig_read_status, use_container_width = True)
    # bar chart for genres
    if stats["genres"]:
        genres_df = pd.DataFrame({
            "Genre": list(stats["genres"].keys()),
            "Count": list(stats["genres"].values()),
        })
        fig_genres = px.bar(
            genres_df,
            x = "Genre",
            y = "Count",
            color = "Count",
            color_continuous_scale =px.colors.sequential.Blues,
        )
        fig_genres.update_layout(
            title_text = "Books by Genre",
            xaxis_title = "Genre",
            yaxis_title = "Number of Books",
            height = 400,
        )
        st.plotly_chart(fig_genres, use_container_width = True)
    
    if stats["decades"]:
        decades_df = pd.DataFrame({
            "Decade": list(stats["decades"].keys()),
            "Count": list(stats["decades"].values()),
        })
        fig_decades = px.bar(
            decades_df,
            x = "Decade",
            y = "Count",
            markers = True,
            line_shape = "spline",
        )
        fig_decades.update_layout(
            title_text = "Books by Decade",
            xaxis_title = "Decade",
            yaxis_title = "Number of Books",
            height = 400,
        )
        st.plotly_chart(fig_decades, use_container_width = True)
# load library
load_library()
st.sidebar.markdown("<h1 style='text-align:center;'>Navigation </h1>", unsafe_allow_html=True)
lottie_book = load_lottieurl("https://assests9.lottiefiles.com/temp1F20_aKAfIn.json")
if lottie_book:
    with st.sidebar:
        st_lottie(lottie_book , height = 200, key = "book_animation")

nav_options = st.sidebar.radio(
    "Choose an Option :",
    ["View Library", "Add Book", "Search Books", "Library Statistics"])
if nav_options == "View Library":
    st.session_state.current_view = "library"
elif nav_options == "Add Book":
    st.session_state.current_view = "add"
elif nav_options == "Search Books":
    st.session_state.current_view = "search"
elif nav_options == "Library Statistics":
    st.session_state.current_view = "stats"

st.markdown("<h1 class='main-header'>Personal Library Management System</h1>", unsafe_allow_html=True) 
if st.session_state.current_view == "add":
    st.markdown("<h2 class='sub-header'>Add a New Book</h2>", unsafe_allow_html=True)
    

    # adding books input form
    with st.form("add_book_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Book Title", placeholder="Enter book title", max_chars=100)
            author = st.text_input("Author", placeholder="Enter author's name", max_chars=100)
            publication_year = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, step=1, value=2023)

        with col2:
            genre = st.selectbox(
                "Genre",
                ["Fiction", "Non-Fiction", "Science", "History", "Biography", "Fantasy", "Mystery", "Romance", "Thriller","other"
                 ])
            read_status = st.selectbox(
                "Read Status",
                ["Read", "Unread"],
                horizontal=True
            )
            read_bool = read_status == "Read"
        submit_button = st.form_submit_button(label="Add Book")

        if submit_button and title and author:
            add_book(title, author, genre, read_bool, publication_year)
            
    if st.session_state.book_added:
        st.markdown("<div class='success-messge'> Book Added Successfully </div>", unsafe_allow_html=True)
        st.balloons()
        st.session_state.book_added = False
    elif st.session_state.current_view == "library":
        st.markdown("<h2 class='sub-header'>Your Library</h2>", unsafe_allow_html=True)

    if st.session_state.library:
        st.markdown("<div class='warning-message'>your library is empty. Add some books to get started.</div>", unsafe_allow_html=True)
    else:
        cols = st.columns(2)
        for i , book in enumerate(st.session_state.library):
            with cols[i % 2]:
                st.markdown(
                    f"""
                    <div class="book-card">
                        <h3>{book['title']}</h3>
                        <p><strong>Author:</strong> {book['Author']}</p>
                        <p><strong>publication year:</strong> {book['Publication_year']}</p>
                        <p><strong>Genre:</strong> {book['Genre']}</p>
                        <p><span class='{"read-badge" if book["read_status"] else "unread-badge"}'>{
                            "Read" if book["read_status"] else "Unread"}</span></p>
                    </div>
                    """,unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"remove", key=f"remove{i}", use_container_width=True):
            if remove_book(i):
                st.rerun()
    with col2:
            new_status = not book['read_status']
            status_label = "Mark as Unread" if not book["read_status"] else "Mark as unread"
            if st.button(status_label, key=f"status{i}", use_container_width=True):
                st.session_state.library[i]["read_status"] = new_status
                save_library()
                st.rerun()
    if st.session_state.book_remove:
        st.markdown("<div class='success-message'>Book Removed Successfully</div>", unsafe_allow_html=True)
        st.session_state.book_remove = False

elif st.session_state.current_view == "search":
    st.markdown("<h2 class='sub-header'>Search Books </h2>", unsafe_allow_html=True)

    search_by = st.selectbox("search by:", ["Title", "Author", "Genre"])
    search_term = st.text_input ("Enter search term:")

    if st.button("Search",use_container_width=False):
        if search_term:
            with st.spinner("Searching..."):
                time.sleep(0.5)
                search_book(search_term, search_by)
    if hasattr(st.session_state, "search_results"):
        if st.session_state.search_results:
            st.markdown(f"<h3> found {len(st.session_state.search_results)} results for '{search_term}'</h3>", unsafe_allow_html=True)

            for i , book in enumerate(st.session_state.search_results):
                st.markdown(
                    f"""
                    <div class="book-card">
                        <h3>{book['title']}</h3>
                        <p><strong>Author:</strong> {book['Author']}</p>
                        <p><strong>Publication Year:</strong> {book['Publication_year']}</p>
                        <p><strong>Genre:</strong> {book['Genre']}</p>
                        <p><span class='{"read-badge" if book["Read-Status"] else "unread-badge"}'>{
                            "Read" if book["Read-Status"] else "Unread"}</span></p>)
                    </div>
                    """, unsafe_allow_html=True)
        elif search_term:
            st.markdown("<div class='warning-message'>No results found</div>", unsafe_allow_html=True)        

elif st.session_state.current_view == "stats":
    st.markdown("<h2 class='sub-header'>Library Statistics</h2>", unsafe_allow_html=True)
    if not st.session_state.library:
        st.markdown("<div class='warning-message'>Your library is empty. Add some books to get started.</div>", unsafe_allow_html=True)
    else:
        stats = get_lib_stats()
        col1 , col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Books", stats["total_books"])
        with col2:
            st.metric("Read Books", stats["read_books"])
        with col3:
            st.metric("percentage of Read Books", f"{stats['read_percent']:.1f}%")
        create_visualizations()

        if stats['authors']:
            st.markdown("<h3>Top Authors</h3>", unsafe_allow_html=True)
            top_authors = dict(list(stats["authors"].items())[:5])
            for author, count in top_authors.items():
                st.markdown(f"**{author}**: {count} book{'s' if count > 1 else ''}")
st.markdown("---")
st.markdown("copyright @2025 Daniyal Ghouri Library Management System", unsafe_allow_html=True)
