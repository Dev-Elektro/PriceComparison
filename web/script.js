document.querySelector(".u-btn.u-btn-round.u-button-style.u-gradient.u-none.u-radius-4.u-text-body-alt-color.u-btn-2").style=("display:none")
document.querySelector(".u-btn.u-btn-round.u-button-style.u-gradient.u-none.u-radius-4.u-text-body-alt-color.u-btn-3").style=("display:none");
document.querySelector(".u-text.u-text-palette-1-light-1.u-text-3").style=("display:none");
document.querySelector(".u-image.u-image-circle.u-preserve-proportions.u-image-1").style=("display:none")
document.querySelector(".u-image.u-image-circle.u-preserve-proportions.u-image-2").style=("display:none")
document.querySelector(".u-align-center.u-custom-font.u-font-lobster.u-text.u-text-default.u-text-5").style=("display:none")









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


//открыть файл
document.querySelector("#openresultfile").onclick = function () {  
   // Call python's random_python function
  
  
    // Update the div with a random number returned by python
    
    if (document.querySelector("#outfilename").innerHTML)
    {
      eel.resultfileopen();
    }
    else
    {alert( "Нет файла реестра... ошибка, откройте вручную" );}
  
}






eel.expose(js_wait);
function js_wait() {
  document.querySelector(".u-image.u-image-circle.u-preserve-proportions.u-image-2").style=("display:none");
  document.querySelector(".u-btn.u-btn-round.u-button-style.u-gradient.u-none.u-radius-4.u-text-body-alt-color.u-btn-3").style=("display:none");
  document.querySelector(".u-text.u-text-palette-1-light-1.u-text-3").style=("display");
  document.querySelector(".u-image.u-image-circle.u-preserve-proportions.u-image-1").style=("display");
  document.querySelector(".u-align-center.u-custom-font.u-font-lobster.u-text.u-text-default.u-text-5").style=("display");
  document.querySelector(".u-align-center.u-custom-font.u-font-lobster.u-text.u-text-default.u-text-5").innerHTML="Выполняем работы, пожалуйста, подождите...";
}


eel.expose(js_gotovo);
function js_gotovo() {
  document.querySelector(".u-image.u-image-circle.u-preserve-proportions.u-image-1").style=("display:none");
  document.querySelector(".u-text.u-text-palette-1-light-1.u-text-3").style=("display:none");
  document.querySelector(".u-image.u-image-circle.u-preserve-proportions.u-image-2").style=("display");
  document.querySelector(".u-align-center.u-custom-font.u-font-lobster.u-text.u-text-default.u-text-5").innerHTML="Работы завершены!";
  document.querySelector(".u-btn.u-btn-round.u-button-style.u-gradient.u-none.u-radius-4.u-text-body-alt-color.u-btn-3").style=("display");
}


eel.expose(my_javascript_function);
function my_javascript_function(out) {
  document.querySelector("#outputpython").innerHTML = document.querySelector("#outputpython").innerHTML + "<br>" + out ;
}





document.querySelector("#startsearch").onclick = async function () {

  document.querySelector(".u-btn.u-btn-round.u-button-style.u-gradient.u-none.u-radius-4.u-text-body-alt-color.u-btn-2").style=("display:none");
  eel.start_search_js();
  
 
  
  
}

