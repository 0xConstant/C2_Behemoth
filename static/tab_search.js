
    $(document).ready(function(){

    // For the first table (users table)
    $("#search-input").on("keyup", function() {
        var value = $(this).val().toLowerCase();

        $("#users-table tr").filter(function() {
            $(this).toggle($(this).find('.uid-cell').text().toLowerCase().indexOf(value) > -1)
        });
    });

    // For the second table (paid users table)
    $("#search-paid-input").on("keyup", function() {
        var value = $(this).val().toLowerCase();

        $("#users-paid-table tr").filter(function() {
            $(this).toggle($(this).find('.uid-cell').text().toLowerCase().indexOf(value) > -1)
        });
    });
});

