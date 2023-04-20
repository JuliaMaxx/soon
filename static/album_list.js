// create a list to store all the titles of the albums
const albums = [];

// loop over 25 pages of data
for (let i = 1; i < 25; i++) {
    page = i;
    // use discogs api to fetch data from 2012 till 2023 
    fetch(`https://api.discogs.com/database/search?year_from=2012&year_to=2023&per_page=100&page=${page}&type=master&key=EOkrQXHJtnMKmjQXuAFb&secret=QYVzmXpfStbButiFBSVCaMQcoeYrFXRT`)
        .then(response => response.json())
        .then(data => {
            // get the titles from the response and add them to the list
            albums.push(...data.results?.map(item => item.title));
        })
        // catch potential erorrs
        .catch(err => console.log(err));
}




