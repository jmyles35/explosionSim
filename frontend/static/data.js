$.ajaxSetup({
   async: false
 });

var arrData;
var objData;

$(document).ready(function(e) {

      $.getJSON("static/data/data.json", function(json) {
          var jsonStr = JSON.stringify(json);
          var result = JSON.parse(jsonStr);
          arrData = result;
          //console.log(json); // this will show the info it in firebug console
      });
      $.getJSON("static/data/objectData.json", function(json) {
          var jsonStr = JSON.stringify(json);
          var result = JSON.parse(jsonStr);
          objData = result;
          //console.log(json); // this will show the info it in firebug console
      });
      //console.log(arrData);
});
