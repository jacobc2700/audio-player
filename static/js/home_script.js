$(document).ready(function() {
    $(".start").click(function(){
        var thisID = $(this).attr('id');
        var videoURL = $('#frame-' + thisID).prop('src');
        videoURL += "&autoplay=1";
        $('#frame-' + thisID).prop('src', videoURL);
    });

    $(".stop").click(function(){
        var thisID = $(this).attr('id').substring(5);
        var videoURL = $('#frame-' + thisID).prop('src');
        videoURL = videoURL.replace("&autoplay=1", "");
        $('#frame-' + thisID).prop('src', '');
        $('#frame-' + thisID).prop('src', videoURL);
    });
});