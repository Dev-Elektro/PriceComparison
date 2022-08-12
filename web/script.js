toastr.options = {
  "closeButton": false,
  "debug": false,
  "newestOnTop": false,
  "progressBar": true,
  "positionClass": "toast-top-center",
  "preventDuplicates": false,
  "onclick": null,
  "showDuration": "500",
  "hideDuration": "1000",
  "timeOut": "5000",
  "extendedTimeOut": "1000",
  "showEasing": "swing",
  "hideEasing": "linear",
  "showMethod": "fadeIn",
  "hideMethod": "fadeOut"
}

document.querySelector(".u-btn.u-btn-round.u-button-style.u-gradient.u-none.u-radius-4.u-text-body-alt-color.u-btn-2").style=("display:none")
document.querySelector(".u-btn.u-btn-round.u-button-style.u-gradient.u-none.u-radius-4.u-text-body-alt-color.u-btn-3").style=("display:none");
document.querySelector(".u-text.u-text-palette-1-light-1.u-text-3").style=("display:none");
document.querySelector(".u-image.u-image-circle.u-preserve-proportions.u-image-1").style=("display:none")
document.querySelector(".u-image.u-image-circle.u-preserve-proportions.u-image-2").style=("display:none")
document.querySelector(".u-align-center.u-custom-font.u-font-lobster.u-text.u-text-default.u-text-5").style=("display:none")


// Onclick of the button выбор файла
document.querySelector("#choosefile").onclick = function () {  
  document.querySelector(".u-btn.u-btn-round.u-button-style.u-gradient.u-none.u-radius-4.u-text-body-alt-color.u-btn-2").style=("display:none")
  document.querySelector(".u-btn.u-btn-round.u-button-style.u-gradient.u-none.u-radius-4.u-text-body-alt-color.u-btn-3").style=("display:none");
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
    toastr.success("Выбран файл для обработки");
    }
    else
    {//alert( "Необходимо выбрать файл реестра для обработки" );
    toastr.error("Необходимо выбрать файл реестра для обработки");
  }
  
  })
  
}


//открыть файл
document.querySelector("#openresultfile").onclick = function () {  
   // Call python's random_python function
    // Update the div with a random number returned by python
    
    if (document.querySelector("#outfilename").innerHTML)
    {
      toastr.success("Запускаем обработанный файл");
      eel.resultfileopen();
    }
    else
    {//alert( "Нет файла реестра... ошибка, откройте вручную" );
    toastr.error("Нет файла реестра... ошибка, откройте вручную");}  
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
  toastr.info("Текущий этап отработан");
}


eel.expose(my_javascript_function);
function my_javascript_function(out) {
  document.querySelector("#outputpython").innerHTML = document.querySelector("#outputpython").innerHTML + "<br>" + out ;
}

//проверка checkbox4
eel.expose(my_checkbox_function);
function my_checkbox_function() {
  if((document.querySelector("#checkbox-e85e").checked==true) || (document.querySelector("#checkbox-a03c").checked==true) || (document.querySelector("#checkbox-0521").checked==true))
  {
    ok="OK"
    console.log("srabotalo")
    return ok
  }
  else
  {
    ok="null"
    return ok
  }

}

eel.expose(check_citilink);
function check_citilink()
{
  //citilink
  if( document.querySelector("#checkbox-e85e").checked==true)
  {
    ch="citilink"
    return ch;
  }
  
}

eel.expose(check_regard);
function check_regard()
{
  //regard
  if( document.querySelector("#checkbox-a03c").checked==true)
  {
    ch="regard"
    return ch;
  }
}

eel.expose(check_dns);
function check_dns()
{
  //dns
  if( document.querySelector("#checkbox-0521").checked==true)
  {
    ch="dns"
    return ch;
  }
  
}


document.querySelector("#startsearch").onclick = async function () {

  if((document.querySelector("#checkbox-e85e").checked==true) || (document.querySelector("#checkbox-a03c").checked==true) || (document.querySelector("#checkbox-0521").checked==true))
  {
    if( document.querySelector("#checkbox-e85e").checked==true)
    {document.querySelector("#outputpython").innerHTML = document.querySelector("#outputpython").innerHTML + "<br>" + "•Выбран поставщик Citilink" ;}
    if( document.querySelector("#checkbox-a03c").checked==true)
    {document.querySelector("#outputpython").innerHTML = document.querySelector("#outputpython").innerHTML + "<br>" + "•Выбран поставщик Regard" ;}
    if( document.querySelector("#checkbox-0521").checked==true)
    {document.querySelector("#outputpython").innerHTML = document.querySelector("#outputpython").innerHTML + "<br>" + "•Выбран поставщик DNS" ;}
  document.querySelector(".u-btn.u-btn-round.u-button-style.u-gradient.u-none.u-radius-4.u-text-body-alt-color.u-btn-2").style=("display:none");
  toastr.success("Запущен поиск!!!");
  eel.start_search_js();
  }
  else
  {
    //alert( "Необходимо выбрать поставщика для поиска!!!" );
    toastr.error("Необходимо выбрать поставщика для поиска!!!");
  }
  
}

