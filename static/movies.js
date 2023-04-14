$(function () {
    // Fetch all titles
    const apiKey = "8e5c4304a2b0fc02884f12935ccffac9";
    const url = `https://api.themoviedb.org/3/search/multi?api_key=${apiKey}&language=en-US&query=`;

    function fetchTitles(request, response) {
        const searchTerm = encodeURIComponent(request.term);
        $.ajax({
            url: url + searchTerm,
            success: function (data) {
                const titles = [];
                data.results.forEach(function (result) {
                    titles.push(result.title || result.name);
                });
                response(titles);
            }
        });
    }

    // Initialize autocomplete
    $("#title-input").autocomplete({
        source: fetchTitles,
        minLength: 1,
        appendTo: "#my-navbar"
    });
});