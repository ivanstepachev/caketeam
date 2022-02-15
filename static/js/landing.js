$(document).ready(function(){

    $(".add-to-input").on("click", function(e) {
        e.preventDefault();
        var value = $(this).text()
        $("#first-input").val(value);
    });


});