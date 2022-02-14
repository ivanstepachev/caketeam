$(document).ready(function(){
    $(".gallery-foto").on("click", function(e) {
        e.preventDefault();
        var imageUrl = $(this).children().attr("src");
        var imageId = $(this).attr("data-id");
        $("#main-foto" + `${imageId}`).attr("src", imageUrl);
        $(`a[data-id="${imageId}"]`).children().removeClass("active-img");
        $(this).children().addClass("active-img");
    });

        $(".wa-hint").on("click", function(e) {
            var respondId = $(this).attr("data-id");
            $.ajax({
                type: "POST",
                url: "/hint",
                data: {
                    to: "wa",
                    id: respondId,
                    csrfmiddlewaretoken: '{{ csrf_token }}'
                },
                success: function(result) {
                    console.log('Hint send');
                },
                error: function(result) {
                    console.log('error');
                }
                });
        });

        $(".insta-hint").on("click", function(e) {
            var respondId = $(this).attr("data-id");
            $.ajax({
                type: "POST",
                url: "/hint",
                data: {
                    to: "insta",
                    id: respondId,
                    csrfmiddlewaretoken: '{{ csrf_token }}'
                },
                success: function(result) {
                    console.log('Hint send');
                },
                error: function(result) {
                    console.log('error');
                }
                });
        });
});