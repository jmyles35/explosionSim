$.ajaxSetup({
   async: false
 });
<<<<<<< HEAD
 var arrData;
=======
var arrData;
>>>>>>> 24a920808b50362753b583539e4371a43e2335dc
$(document).ready(function(e) {
      //alert(jsonObject.start.count);

      $.getJSON("static/data.json", function(json) {
          var jsonStr = JSON.stringify(json);
          var result = JSON.parse(jsonStr);
          arrData = result;
          //console.log(json); // this will show the info it in firebug console
      });
      console.log(arrData);
});
