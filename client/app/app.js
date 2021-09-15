var version = "v0.0.1";

$(document).ready( function () {
    $("#clear-button").click(function(){
        $("#address-text").val("")
    });

    $("#address-button").click(function(){
        var address = $("#address-text").val();

        $("#response").html("Reading address...");

        var start = new Date().getTime();
        $.ajax({
           type: "POST",
           url: "https://address-api.infocruncher.com/predict/",
           data: '{"address": "'+address+'"}',
           tryCount : 0,
           retryLimit : 1,
           success: function(data)
           {
               var end = new Date().getTime();
               var time = end - start;
               $("#response").html("Client timing: " + time + "<br />"
                                                  + "Retries: "+this.tryCount+"<br />"
                                                  + "Success Reponse:<br />"
                                                  + JSON.stringify(data, null, "  "))
           },
           error: function(data)
           {
               this.tryCount++;
               if (this.tryCount <= this.retryLimit) {
                   // Retry
                   $("#response").html("Retry " + this.tryCount + "...");
                   $.ajax(this);
                   return;
               }
               var end = new Date().getTime();
               var time = end - start;
               $("#response").html("Client timing: " + time + "<br />"
                                                  + "Retries: "+this.tryCount+"<br />"
                                                  + "Error Reponse:<br />"
                                                  + JSON.stringify(data, null, "  "))
           },
         });
    });

//    $("#response").html("Initialising service...");
//    var start = new Date().getTime();
//    $.ajax({
//       type: "POST",
//       url: "https://address-api.infocruncher.com/predict/",
//       data: '{"address": "1 Prime Lane"}',
//       success: function(data)
//       {
//            var end = new Date().getTime();
//            var time = end - start;
//            $("#response").html("Clent timing: " + time + " (Priming)<br />"
//                                             + "Success Reponse:<br />"
//                                             + JSON.stringify(data, null, "  "))
//       },
//       error: function(data)
//       {
//           var end = new Date().getTime();
//           var time = end - start;
//           $("#response").html("Clent timing: " + time + " (Priming)<br />"
//                                            + "Error Reponse:<br />"
//                                            + JSON.stringify(data, null, "  "))
//       },
//     });
});
