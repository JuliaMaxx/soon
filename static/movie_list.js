// create a list with all the movie and tv show titles
const titles = [];

// loop over 500 pages of the data
for (let i = 1; i <= 500; i++) {
  page = i;
  // fetch data using tmdb api
  fetch(`https://api.themoviedb.org/3/discover/movie?api_key=8e5c4304a2b0fc02884f12935ccffac9&language=en-US&sort_by=popularity.desc&include_adult=false&include_video=false&primary_release_date.gte=2010-01-01&primary_release_date.lte=2023-04-15&page=${page}`)
    .then(response => response.json())
    .then(data => {
      // get the titles from the response and add them to the list
      titles.push(...data.results?.map(item => item.title));

    })
    // catch any potential errors
    .catch(error => console.log(error));
}
