var version = "v0.0.1";

$(document).ready( function () {
    $("#clear-button").click(function(){
        $("#address-text").val("")
    });

    $("#address-button").click(function(){
        var address = $("#address-text").val();

        $("#response").html("Parsing address...");

        var start = new Date().getTime();

        $.ajax({
           type: "POST",
           url: "https://address-api.infocruncher.com/predict/",
           data: '{"address": "'+address+'"}',
           success: function(data)
           {
               var end = new Date().getTime();
               var time = end - start;
               $("#response").html("Clent timing: " + time + "<br />"
                                                  + "Success Reponse:<br />"
                                                  + JSON.stringify(data, null, "  "))
           },
           error: function(data)
           {
               var end = new Date().getTime();
               var time = end - start;
               $("#response").html("Clent timing: " + time + "<br />"
                                                  + "Error Reponse:<br />"
                                                  + JSON.stringify(data, null, "  "))
           },
         });
    });

    $("#response").html("Initialising service...");
    var start = new Date().getTime();
    $.ajax({
       type: "POST",
       url: "https://address-api.infocruncher.com/predict/",
       data: '{"address": "1 Prime Lane"}',
       success: function(data)
       {
            var end = new Date().getTime();
            var time = end - start;
            $("#response").html("Clent timing: " + time + " (Priming)<br />"
                                             + "Success Reponse:<br />"
                                             + JSON.stringify(data, null, "  "))
       },
       error: function(data)
       {
           var end = new Date().getTime();
           var time = end - start;
           $("#response").html("Clent timing: " + time + " (Priming)<br />"
                                            + "Error Reponse:<br />"
                                            + JSON.stringify(data, null, "  "))
       },
     });
});
