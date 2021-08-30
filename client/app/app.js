var version = "v0.0.1";

$(document).ready( function () {
    $("#clear-button").click(function(){
        $("#address-text").val("")
    });

    $("#address-button").click(function(){
        var address = $("#address-text").val();

        $("#response").html("Parsing address...");

        $.ajax({
           type: "POST",
           url: "https://address-api.infocruncher.com/predict/",
           data: '{"address": "'+address+'"}',
           success: function(data)
           {
               // alert("success");
               // alert(JSON.stringify(data));

               $("#response").html("Success Reponse:<br />" + JSON.stringify(data, null, "  "))
           },
           error: function(data)
           {
               // alert("error: " + JSON.stringify(data));
               $("#response").html("Error Reponse:<br />" + JSON.stringify(data, null, "  "))
           },
         });
    });

    $("#response").html("Initialising service...");
    $.ajax({
       type: "POST",
       url: "https://address-api.infocruncher.com/predict/",
       data: '{"address": "1 Prime Lane"}',
       success: function(data)
       {
           $("#response").html("Success Reponse (Priming):<br />" + JSON.stringify(data, null, "  "))
       },
       error: function(data)
       {
           // alert("error: " + JSON.stringify(data));
           $("#response").html("Error Reponse (Priming):<br />" + JSON.stringify(data, null, "  "))
       },
     });
});
