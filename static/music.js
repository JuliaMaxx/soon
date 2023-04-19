// select input tag in music.html file
let input = document.querySelector('#title-input2');
input.addEventListener('input', function (event) {
    let html = '';
    if (input.value) {
        // convert input value to lowercase
        const val = input.value.toLowerCase();
        let count = 0;
        for (album of albums) {
            // make sure that autocomplete does not suggest more than 15 options
            if (count === 15) {
                break
            }
            if (album.substr(0, val.length).toLowerCase() === val) {
                count = count + 1;
                //if the input matches any movie title - create a new list item
                html += `<li><a href="/music?album=${album}" role="button">${album}</a></li>`;
            }
        }
        // add list items to the unordered list
        document.querySelector('.options').innerHTML = html;
    }
});