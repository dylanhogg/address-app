const version = "v1.0.0";
const predictionUrl = "https://address-api.infocruncher.com/predict/";
const randomAddresses = [
        "48a Pirrama Rd Pyrmont NSW 2009",
        "6/341 George Str, Sydney NSW 2000",
        "108-110 Kippax Lane, Surry Hills NSW 2010",
        "L41, Tower Two, 200 Barangaroo Ave, Sydney NSW 2000",
        "Unit 18/14-18 Flood St, Bondi, NSW 2026",
        "Aptt 16, 400 Bondi Rd, Bondi NSW 2026",
        "Lvl 15/333 George St Sydney NSW 2000",
        "Shop 4/11-31 York St, Sydney NSW 2000",
        "Floor 3, 152-156 Clarence St, Sydney NSW 2000",
    ]

var predict_count = 0;

$(document).ready(function () {
    var randomElement = randomAddresses[Math.floor(Math.random() * randomAddresses.length)];
    $("#input-text").val(randomElement)

    $("#clear-button").click(function(){
        $("#input-text").val("")
        $("#input-text").focus();
    });

    $("#random-button").click(function(){
        var randomElement = randomAddresses[Math.floor(Math.random() * randomAddresses.length)];
        $("#input-text").val(randomElement)
    });

    $("#view-debug-info").click(function(){
        $("#debug-response").toggle();
        return false;
    });

    $("#view-about-info").click(function(){
        var about = "Address Segmenter App by Dylan Hogg\n" +
        "<a href='https://address-app.infocruncher.com/'>address-app.infocruncher.com</a>\n\n" +
        "I'm an app that segments an address\ninto structured fields using the\n<a href='https://github.com/jasonrig/address-net'>address-net</a> library\n\n" +
        "Source code available:\n<a href='https://github.com/dylanhogg/address-app'>github.com/dylanhogg/address-app</a>";
        $("#response").html(about)
        return false;
    });

    $("#input-text").keypress(function (e) {
      if (e.which == 13) {
        $("#address-button").click();
        return false;
      }
    });

    $("#address-button").click(function(){
        $("#debug-response").html("");
        $("#loader").addClass("loader");

        var address = $("#input-text").val();
        if (address.length == 0) {
            $("#response").html("Address is empty<br /><br />Experiment by clicking the Random button");
            $("#loader").removeClass("loader");
            return;
        }

        if (predict_count == 0) {
           $("#response").html("Segmenting address...<br />...and waking up the server");
        } else {
           $("#response").html("Segmenting address...");
        }

        var start = new Date().getTime();
        $.ajax({
           type: "POST",
           url: predictionUrl,
           data: '{"address": "'+address.replace(/(\r\n|\n|\r)/gm, " ")+'"}',
           tryCount : 0,
           retryLimit : 1,
           success: function(data)
           {
               $("#loader").removeClass("loader");
               predict_count++;
               var end = new Date().getTime();
               var time = end - start;

               var response = "<table class='response'>";
               response += "<tr><th>Key</th><th>Value</th></tr>";
               var segments = data["result"];
               for (var key in segments){
                 var key_display = key.replace(/_/g, " ");
                 key_display = key_display.charAt(0).toUpperCase() + key_display.slice(1);
                 response += "<tr><td>" + key_display + "</td><td>" + segments[key] + "</td></tr>";
               }
               response += "</table>";
               $("#response").html(response)

               var debugInfo = "\nDEBUG INFO:\nClient timing: " + time + "\n"
                                                    + "Retries: "+this.tryCount+"\n"
                                                    + "Success Reponse:\n"
                                                    + JSON.stringify(data, null, "  ");
               console.log(debugInfo);
               $("#debug-response").html(debugInfo)
           },
           error: function(data)
           {
               this.tryCount++;
               if (this.tryCount <= this.retryLimit) {
                   $("#response").html("Error, retry " + this.tryCount + " of " + this.retryLimit + "...");
                   $.ajax(this);
                   return;
               }
               var end = new Date().getTime();
               var time = end - start;

               $("#loader").removeClass("loader");
               $("#response").html("Oops, something went wrong<br /><br />Please try again")

               var debugInfo = "\nDEBUG INFO:\nClient timing: " + time + "\n"
                                            + "Retries: "+this.tryCount+"\n"
                                            + "Error Reponse:\n"
                                            + JSON.stringify(data, null, "  ");
               console.log(debugInfo);
               $("#debug-response").html(debugInfo)
           },
         });
    });


    var start = new Date().getTime();
    $.ajax({
       type: "POST",
       url: predictionUrl,
       data: '{"address": "Page load priming"}',
       tryCount : 0,
       retryLimit : 1,
       success: function(data)
       {
            predict_count++;
            var end = new Date().getTime();
            var time = end - start;
            var debugInfo = "\nPRIME SUCCESS:\nClient timing: " + time + "\n"
                             + "Retries: "+this.tryCount+"\n"
                             + "Success Reponse:\n"
                             + JSON.stringify(data, null, "  ");
            console.log(debugInfo);
            $("#debug-response").html(debugInfo)
       },
       error: function(data)
       {
           this.tryCount++;
           if (this.tryCount <= this.retryLimit) {
               $("#response").html("Retry " + this.tryCount + "...");
               $.ajax(this);
               return;
           }
           var end = new Date().getTime();
           var time = end - start;

           var debugInfo = "\nPRIME ERROR:\nClient timing: " + time + "\n"
                            + "Retries: "+this.tryCount+"\n"
                            + "Error Reponse:\n"
                            + JSON.stringify(data, null, "  ");
           console.log(debugInfo);
           $("#debug-response").html(debugInfo)
       },
     });
});
