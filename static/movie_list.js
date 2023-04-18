// TMDB API returns a maximum of 5000 results, which is 250 pages with 20 results per page
const titles = [];

// Make a GET request to the TMDB API for each page of results
for (let i = 1; i <= 500; i++) {
  page = i;
  fetch(`https://api.themoviedb.org/3/discover/movie?api_key=8e5c4304a2b0fc02884f12935ccffac9&language=en-US&sort_by=popularity.desc&include_adult=false&include_video=false&primary_release_date.gte=2010-01-01&primary_release_date.lte=2023-04-15&page=${page}`)
    .then(response => response.json())
    .then(data => {
      // Extract the titles from the response and concatenate them to the array
      titles.push(...data.results?.map(item => item.title));

    })
    .catch(error => console.log(error));
}
console.log(titles)
