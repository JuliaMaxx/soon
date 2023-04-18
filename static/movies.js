let input = document.querySelector('#title-input');
input.addEventListener('input', function (event) {
    let html = '';
    if (input.value) {
        const val = input.value.toLowerCase();
        let count = 0;
        for (movie of titles) {
            if (count === 15) {
                break
            }
            if (movie.substr(0, val.length).toLowerCase() === val) {
                count = count + 1;
                html += `<li><a href="/movies?movie=${movie}" role="button">${movie}</a></li>`;
            }
        }
        document.querySelector('.options').innerHTML = html;
    }
});