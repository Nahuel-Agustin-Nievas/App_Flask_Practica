document.getElementById("add-file-button").addEventListener("click", function () {
    var file_input = document.createElement("input");
    file_input.setAttribute("type", "file");
    file_input.setAttribute("name", "ourfile[]");
    file_input.setAttribute("multiple", false);
    file_input.setAttribute("accept", ".pdf, .txt, .doc, .jpg, .jpeg, .png");
    var file_input_container = document.createElement("div");
    var remove_button = document.createElement("button");
    remove_button.innerHTML = "Eliminar";
    remove_button.addEventListener("click", function(){
        file_input_container.remove();
    });
    file_input_container.appendChild(file_input);
    file_input_container.appendChild(remove_button);
    document.getElementById("file-inputs").appendChild(file_input_container);
});






// document.getElementById("add-file-button").addEventListener("click", function () {
//     var file_input = document.createElement("input");
//     file_input.setAttribute("type", "file");
//     file_input.setAttribute("name", "ourfile[]");
//     file_input.setAttribute("multiple", false);
//     file_input.setAttribute("accept", ".pdf, .txt, .doc, .jpg, .jpeg, .png");
//     document.getElementById("file-inputs").appendChild(file_input);
// });



document.getElementById("form_id").addEventListener("submit", function(event) {
    var fileInputs = document.querySelectorAll("input[type=file]");
    for (var i = 0; i < fileInputs.length; i++) {
        if (fileInputs[i].files.length === 0) {
            fileInputs[i].parentNode.removeChild(fileInputs[i]);
        }
    }
});





