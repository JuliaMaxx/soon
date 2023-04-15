function createAutocompleteSearchBar() {
    // Initialize jQuery UI Autocomplete widget
    $('#title-input2').autocomplete({
        source: function (request, response) {
            // Make a request to the Deezer API search endpoint
            $.ajax({
                url: 'https://api.deezer.com/search',
                dataType: 'jsonp',
                data: {
                    q: request.term,
                    limit: 10, // set the number of results to display
                    type: 'album' // set the type of search to albums
                },
                success: function (data) {
                    // Extract the album titles from the response data
                    var albumTitles = $.map(data.data, function (album) {
                        return { label: album.title, value: album.title };
                    });
                    // Pass the album titles to the autocomplete widget
                    response(albumTitles);
                }
            });
        },
        minLength: 2 // set the minimum number of characters required to trigger a search
    });
}
