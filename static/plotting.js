var socket=io('/plot');
socket.on('plot_update', function(data){
  console.log("America",data)
});
