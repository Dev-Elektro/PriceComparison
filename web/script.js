document.querySelector(".u-btn.u-btn-round.u-button-style.u-gradient.u-none.u-radius-4.u-text-body-alt-color.u-btn-2").style=("display:none")

document.querySelector(".u-image.u-image-circle.u-preserve-proportions.u-image-1").style=("display:none")
document.querySelector(".u-align-center.u-custom-font.u-font-lobster.u-text.u-text-default.u-text-4").style=("display:none")
document.querySelector(".u-image.u-image-circle.u-preserve-proportions.u-image-2").style=("display:none")


// Onclick of the button
document.querySelector("#choosefile").onclick = function () {  
  document.querySelector(".u-btn.u-btn-round.u-button-style.u-gradient.u-none.u-radius-4.u-text-body-alt-color.u-btn-2").style=("display:none")
  document.querySelector("#outputpython").innerHTML = "Вывод работы программы.";
  document.querySelector("#outfilename").innerHTML = "Выберите файл реестра.";
  // Call python's random_python function
  
  eel.fileopen()(function(number){                      
    // Update the div with a random number returned by python
    document.querySelector("#outfilename").innerHTML = number;
    //document.querySelector("#outputpython").innerHTML = document.querySelector("#outputpython").innerHTML + "\n" + number;
    if (document.querySelector("#outfilename").innerHTML)
    {
    document.querySelector(".u-btn.u-btn-round.u-button-style.u-gradient.u-none.u-radius-4.u-text-body-alt-color.u-btn-2").style=("display")
    }
    else
    {alert( "Необходимо выбрать файл реестра для обработки" );}
  
  })
  
}





eel.expose(js_wait);
function js_wait() {
  document.querySelector(".u-image.u-image-circle.u-preserve-proportions.u-image-2").style=("display:none");
  document.querySelector(".u-image.u-image-circle.u-preserve-proportions.u-image-1").style=("display");
  document.querySelector(".u-align-center.u-custom-font.u-font-lobster.u-text.u-text-default.u-text-4").style=("display");
  document.querySelector(".u-align-center.u-custom-font.u-font-lobster.u-text.u-text-default.u-text-4").innerHTML="Выполняем работы, пожалуйста, подождите...";
}


eel.expose(js_gotovo);
function js_gotovo() {
  document.querySelector(".u-image.u-image-circle.u-preserve-proportions.u-image-1").style=("display:none");
  document.querySelector(".u-image.u-image-circle.u-preserve-proportions.u-image-2").style=("display");
  document.querySelector(".u-align-center.u-custom-font.u-font-lobster.u-text.u-text-default.u-text-4").innerHTML="Работы завершены!";
}


eel.expose(my_javascript_function);
function my_javascript_function(out) {
  document.querySelector("#outputpython").innerHTML = document.querySelector("#outputpython").innerHTML + "<br>" + out ;
}





document.querySelector("#startsearch").onclick = async function () {

 
  eel.start_search_js()
  
  
  
}

