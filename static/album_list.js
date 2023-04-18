const albums = [];
for (let i = 1; i < 40; i++) {
    page = i;
    fetch(`https://api.discogs.com/database/search?year_from=2012&year_to=2023&per_page=100&page=${page}&type=master&key=EUjoZGBSWBFZcbLFaqYK&secret=tNlfLISrlOltyWURcPRgJvmXofvXUTbz`)
        .then(response => response.json())
        .then(data => {
            // Extract the titles from the response and store them in an array
            albums.push(...data.results?.map(item => item.title));
        })
        .catch(error => console.log(error));
}
console.log(albums); // Print the titles to the console





