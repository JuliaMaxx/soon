let input = document.querySelector('#title-input2');
input.addEventListener('input', function (event) {
    let html = '';
    if (input.value) {
        const val = input.value.toLowerCase();
        let count = 0;
        for (album of albums) {
            if (count === 15) {
                break
            }
            if (album.substr(0, val.length).toLowerCase() === val) {
                count = count + 1;
                html += `<li><a href="/music?album=${album}" role="button">${album}</a></li>`;
            }
        }
        document.querySelector('.options').innerHTML = html;
    }
});