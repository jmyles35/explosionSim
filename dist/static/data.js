$.ajaxSetup({
   async: false
 });

var arrData;

$(document).ready(function(e) {

      $.getJSON("static/data/data.json", function(json) {
          var jsonStr = JSON.stringify(json);
          var result = JSON.parse(jsonStr);
          arrData = result;
          //console.log(json); // this will show the info it in firebug console
      });
      //console.log(arrData);
});
