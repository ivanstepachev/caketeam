$(document).ready(function(){

    $(".add-to-input").on("click", function(e) {
        e.preventDefault();
        var value = $(this).text()
        $("#first-input").val(value);
    });

    $("#first-button").click(function(e) {
        if ($("#first-input").val().length === 0) {
            $("#first-input").addClass("is-invalid");
        } else {
            $("#first-form").css("display", "none");
            $("#second-form").css("display", "block");
        }
    });
    $("#second-back").click(function(e) {
        $("#second-form").css("display", "none");
        $("#first-form").css("display", "block");
    });
    $("#second-button").click(function(e) {
        if ($("#second-input").val().length === 0) {
            $("#second-input").addClass("is-invalid");
        } else {
            $("#second-form").css("display", "none");
            $("#third-form").css("display", "block");
        }
    });
    $("#third-back").click(function(e) {
        $("#third-form").css("display", "none");
        $("#second-form").css("display", "block");
    });
    $("#third-button").click(function(e) {
        if ($("#third-input").val().length === 0) {
            $("#third-input").addClass("is-invalid");
        } else {
            $("#third-form").css("display", "none");
            $("#fourth-form").css("display", "block");
        }
    });
    $("#fourth-back").click(function(e) {
        $("#fourth-form").css("display", "none");
        $("#third-form").css("display", "block");
    });
    $("#fourth-button").click(function(e) {
        $("#fourth-form").css("display", "none");
        $("#fifth-form").css("display", "block");
    });
    $("#fifth-back").click(function(e) {
        $("#fifth-form").css("display", "none");
        $("#fourth-form").css("display", "block");
    });
    $("#fifth-button").click(function(e) {
        $("#fifth-form").css("display", "none");
        $("#sixth-form").css("display", "block");
    });
    $("#sixth-back").click(function(e) {
        $("#sixth-form").css("display", "none");
        $("#fifth-form").css("display", "block");
    });

    $("#sixth-button").click(function(e) {
        if ($("#sixth-input1").val().length === 0) {
            e.preventDefault();
            $("#sixth-input1").addClass("is-invalid");
        } else {
            $("#sixth-input1").removeClass("is-invalid");
        }
        if ($("#sixth-input2").val().length === 0) {
            e.preventDefault();
            $("#sixth-input2").addClass("is-invalid");
        } else {
            $("#sixth-input2").removeClass("is-invalid");
        }

    });

    $("#second-input").suggestions({
        token: "1fb228bbc969c88de6a9998d1b20bff93cd8ba94",
        type: "ADDRESS",
        /* Вызывается, когда пользователь выбирает одну из подсказок */
        onSelect: function(suggestion) {
            $('#city-input').val(suggestion.data.city_with_type);
            $('#second-input').val(suggestion.value);
        }
    });

    $("#check").change(function() {
    if(this.checked) {
        $("#delivery-need").css("display", "block");
    } else {
        $("#delivery-need").css("display", "none");
    }
    });

    $("#sixth-input2").mask("7(999)999-99-99");

    $("form").submit(function() {
        $(this).submit(function() {
            return false;
        });
        return true;
    });

});