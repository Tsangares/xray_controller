
function save(){
  folderName=prompt("What is the name of this dataset?\n(Leave blank for unixtime)")
  $.post('/save',{folder: folderName})
}
function motorResponse(axis,data){
  console.log(axis,data)
  if (data!='Error'){
    $('#'+axis).text(Math.round(Number(data))).css('color','black')
	alert("Motor movement completed.")
    Push.create('Motor finished moving!',{timeout: 3000,onClick: function () {
        window.focus();
        this.close();
    }})
  }else{
    $('#'+axis).css('color','red')
	alert("Motor Error")
    Push.create('Failed to move moter!',{timeout: 3000,onClick: function () {
        window.focus();
        this.close();
    }})
  }
}
function move_vert(){
  distance=prompt("Enter microns\nNegative means Ascend above beam\nPositive means Decend below beam\nDash (-) to return home.")
  $.get('/move/vertical',{distance: distance},(d)=>motorResponse('y',d))
}
function move_horiz(){
  distance=prompt("Enter microns\nNegative means from beam direction move Port\nPositive means from the beam direction move Starboard\nDash (-) to return home.")
  $.get('/move/horizonal',{distance: distance},(d)=>motorResponse('x',d))
}
var socket=io('/');
socket.on('update', function(data){
  $("#plot").css("display","inline-flex")
});
