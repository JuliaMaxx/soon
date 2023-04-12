# import requests
# import json
# url = "https://online-movie-database.p.rapidapi.com/auto-complete"

# title = inpu("Title: ")
# querystring = {"q": f"{title}"}

# headers = {
#     "X-RapidAPI-Key": "5d259f45femsh1450561663d4dcdp11efacjsna9ffa5e1980d",
#     "X-RapidAPI-Host": "online-movie-database.p.rapidapi.com"
# }

# response = requests.request("GET", url, headers=headers, params=querystring)
# # check the response status code
# if response.status_code == 200:
#     data = response.json()
#     # extract the relevant data from the response
#     info = []
#     d = data['d']
#     for num in range(3):
#         if 'y' in d[num].keys():
#             ds = {}
#             ds['id'] = d[num]['id']
#             ds['year'] = d[num]['y']
#             ds['image'] = d[num]["i"]["imageUrl"]
#             ds['title'] = d[num]['l']
#             info.append(ds)

# print(info)


# url1 = "https://online-movie-database.p.rapidapi.com/title/get-releases"

# for movie in info:
#     querystring1 = {"tconst": f"{movie['id']}"}
#     response1 = requests.request(
#         "GET", url1, headers=headers, params=querystring1)
#     data1 = response1.json()

#     print(data1[0]['date'])
