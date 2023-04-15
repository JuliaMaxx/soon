import requests
import json


def search_album(title):

    url = "https://api.deezer.com/search/album"
    params = {"q": f"{title}"}

    # Make the API request to search for the album
    response = requests.get(url, params=params)
    ids = []
    # Check if the search request was successful
    if response.status_code == 200:
        # Get the album ID from the search response
        response = response.json()
        if "data" in response and len(response["data"]) > 0:
            for d in response['data']:
                album_id = d["id"]
                ids.append(album_id)
        else:
            print("Error: Album not found.")
            exit()
    else:
        print("Error:", response.status_code)
        exit()

    info = []
    # Set up the API endpoint to get detailed information about the album
    for id in ids:
        url1 = f"https://api.deezer.com/album/{id}"

        # Make the API request to get detailed information about the album
        response1 = requests.get(url1)

        # Check if the album request was successful
        if response1.status_code == 200:
            # Get the album information from the album response
            response1 = response1.json()
            album_info = {
                "title": response1["title"],
                "image": response1["cover"],
                "artist_name": response1["artist"]["name"],
                "release_date": response1["release_date"],
            }
            info.append(album_info)
            # Print out the album information
        else:
            print("Error:", response1.status_code)
    print(info)
