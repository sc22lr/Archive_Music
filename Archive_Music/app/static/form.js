$(document).ready(function () {
    $('#search-input').on('input', function () {
        const searchQuery = $(this).val().trim();

        if (searchQuery.length > 1) {
            $.ajax({
                url: "/autocomplete",
                method: "POST",
                contentType: "application/json",
                data: JSON.stringify({ search: searchQuery }),
                success: function (response) {
                    console.log("Suggestions received: ", response);
                    const suggestionsDiv = $('#suggestions');
                    suggestionsDiv.empty();

                    if (response.status === 'OK' && response.suggestions.length > 0) {
                        response.suggestions.forEach(item => {
                            suggestionsDiv.append(`<div class="suggestion-item">${item}</div>`);
                        });
                        $('.suggestion-item').on('click', function () {
                            $('#search-input').val($(this).text());
                            suggestionsDiv.empty();
                        });
                    } else {
                        suggestionsDiv.append('<div class="suggestion-item">No results found</div>');
                    }
                },
                error: function (xhr, status, error) {
                    console.error("AJAX error:", error);
                }
            });
        } else {
            $('#suggestions').empty();
        }
    });
    $(document).on('click', function (event) {
        if (!$(event.target).closest('#search-input, #suggestions').length) {
            $('#suggestions').empty();
        }
    });
});
