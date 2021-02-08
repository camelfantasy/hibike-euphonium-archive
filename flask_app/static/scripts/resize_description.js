var descriptionbox = document.getElementById("descriptionbox");
function resizeDescriptionBox() {
    descriptionbox.style.height = "";
    descriptionbox.style.height = Math.max(descriptionbox.scrollHeight, 55) + 2 + "px";
}
resizeDescriptionBox(); // onload call
descriptionbox.oninput = resizeDescriptionBox;