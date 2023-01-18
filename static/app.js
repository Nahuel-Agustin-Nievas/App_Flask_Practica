document.getElementById("add-file-button").addEventListener("click", function(){
    var file_input = document.createElement("input");
    file_input.setAttribute("type", "file");
    file_input.setAttribute("name", "ourfile");
    file_input.setAttribute("multiple", false);
    document.getElementById("file-inputs").appendChild(file_input);
});
