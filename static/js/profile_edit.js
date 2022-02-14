$(document).ready(function(){

  $("#add-city-input").suggestions({
        token: "1fb228bbc969c88de6a9998d1b20bff93cd8ba94",
        type: "ADDRESS",
        /* Вызывается, когда пользователь выбирает одну из подсказок */
        onSelect: function(suggestion) {
            $('#add-city').prop("disabled", false);
            console.log(suggestion.data.city_with_type);
            if (suggestion.data.city_with_type) {
            $("#add-city-input").removeClass("is-invalid");
            $("#already-city").css("display", "none");
            $("#not-city").css("display", "none");
            $('[name="add-city"]').val(suggestion.data.city_with_type);
            } else {
            $("#add-city-input").val("");
            $("#add-city-input").addClass("is-invalid");
            $("#not-city").css("display", "block");
            }


        }
  });

  $("#editInfo").on("click", function(e) {
  $("#add-info").css("display", "block");
  $("#info").css("display", "none");
  });

  $("#info-back").on("click", function(e) {
  e.preventDefault();
  $("#add-info").css("display", "none");
  $("#info").css("display", "block");
  });

  $("#editContacts").on("click", function(e) {
  $("#add-contacts").css("display", "block");
  $("#contacts").css("display", "none");
  });

  $("#contacts-back").on("click", function(e) {
  e.preventDefault();
  $("#add-contacts").css("display", "none");
  $("#contacts").css("display", "block");
  });

  $("#editCities").on("click", function(e) {
  $("#add-cities").css("display", "block");
  $("#cities-list").css("display", "none");
  $("#editCities").css("display", "none");
  $("#saveCities").css("display", "inline");
  });

  $("#saveCities").on("click", function(e) {
  $("#add-cities").css("display", "none");
  $("#cities-list").css("display", "block");
  $("#editCities").css("display", "inline");
  $("#saveCities").css("display", "none");
  });

  (function($) {
      $.fn.inputFilter = function(inputFilter) {
        return this.on("input keydown keyup mousedown mouseup select contextmenu drop", function() {
          if (inputFilter(this.value)) {
            this.oldValue = this.value;
            this.oldSelectionStart = this.selectionStart;
            this.oldSelectionEnd = this.selectionEnd;
          } else if (this.hasOwnProperty("oldValue")) {
            this.value = this.oldValue;
            this.setSelectionRange(this.oldSelectionStart, this.oldSelectionEnd);
          } else {
            this.value = "";
          }
        });
      };
    }(jQuery));


  $("#wa").inputFilter(function(value) {
    return /^\d*$/.test(value);    // Allow digits only, using a RegExp
  });


});
