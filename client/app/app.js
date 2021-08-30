var version = "v0.0.1";

$(document).ready( function () {
    $("#address-button").click(function(){
        var address = $("#address-text").val();
        //alert(address);
        $.ajax({
           type: "POST",
           url: "https://address-api.infocruncher.com/predict/",
           data: '{"address": "'+address+'"}',
           success: function(data)
           {
               // alert("success");
               alert(JSON.stringify(data));
           },
           error: function(data)
           {
               alert("error");
               alert(JSON.stringify(data));
           },
         });
    });
});
