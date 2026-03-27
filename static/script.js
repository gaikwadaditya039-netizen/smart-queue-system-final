setInterval(function(){

document.getElementById("clock").innerHTML =
new Date().toLocaleTimeString();

},1000);

setTimeout(function(){

location.reload();

},5000);