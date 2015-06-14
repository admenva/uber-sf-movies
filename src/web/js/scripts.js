var movieInfo = $(".movie-info"),
    markers = [],
    map;

$(".searchbox").on("input", function() {
    var query = encodeURI($(this).val());

    movieInfo.fadeOut();
    for (var i = 0; i < markers.length; i++) {
        markers[i].setMap(null);
    }
    markers = [];

    $.getJSON("http://localhost:8080/api/search/movies?query=" + query, function(data) {
        var items = [];
            $.each(data, function(index, movie) {
            items.push( "<a class='movie-link' data-id='" + movie.id +"'><li class='movie-item'>" +
                movie.title + " (" + movie.release_year + ")</li></a>" );
        });

        $(".results").html(
            $("<ul/>", {
                "class": "movie-items",
                html: items.join("")
            })
        );

        $("ul.movie-items").delegate("a.movie-link", "click", function() {
            $(".results ul.movie-items").slideUp();

            $.getJSON("http://localhost:8080/api/movies/" + $(this).data("id"), function(data) {
                movieInfo.find("h1").text(data.title);
                movieInfo.find(".release-year").text("(" + data.release_year + ")");
                movieInfo.find(".director").text(data.director);
                movieInfo.find(".company").text(data.production_company);
                movieInfo.find(".writer").text(data.writer);
                movieInfo.find(".actors").text(data.actors.join(", "));
                movieInfo.fadeIn();

                $.each(data.locations, function(index, location) {
                    var coords = new google.maps.LatLng(location.lat, location.lng);
                    markers.push(new google.maps.Marker({
                        position: coords,
                        map: map,
                        title: location.address
                    }));
                });
            });
        });
    });
});


function initializeMap() {
    var mapOptions = {
        zoom: 12,
        center: new google.maps.LatLng(37.73, -122.45),
        panControl: true,
            panControlOptions: {
            position: google.maps.ControlPosition.RIGHT_TOP
        },
        zoomControl: true,
        zoomControlOptions: {
            style: google.maps.ZoomControlStyle.LARGE,
            position: google.maps.ControlPosition.RIGHT_TOP
        }
    };
    map = new google.maps.Map(document.getElementById("map-canvas"), mapOptions);
}

initializeMap();
