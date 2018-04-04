$.ajaxSetup({
   async: false
 });
$(document).ready(function(e) {
      //alert(jsonObject.start.count);
      var arrData;
      $.getJSON("static/data.json", function(json) {
          var jsonStr = JSON.stringify(json);
          var result = JSON.parse(jsonStr);
          arrData = result;
          //console.log(json); // this will show the info it in firebug console
      });
      console.log(arrData);
});
