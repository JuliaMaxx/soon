// select input tag in movies.html file
let input = document.querySelector('#title-input');
input.addEventListener('input', function (event) {
    let html = '';
    if (input.value) {
        // convert input value to lowercase
        const val = input.value.toLowerCase();
        let count = 0;
        for (movie of titles) {
            // make sure that autocomplete does not suggest more than 15 options
            if (count === 15) {
                break
            }
            if (movie.substr(0, val.length).toLowerCase() === val) {
                count = count + 1;
                //if the input matches any movie title - create a new list item
                html += `<li><a href="/movies?movie=${movie}" role="button">${movie}</a></li>`;
            }
        }
        // add list items to the unordered list
        document.querySelector('.options').innerHTML = html;
    }
});