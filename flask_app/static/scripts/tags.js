background = document.getElementById('confirm-background');
box = document.getElementById('confirm-box');
row = document.getElementById('confirm-row');
confirm_text = document.getElementById('confirm-text');
confirm_tag = document.getElementById('confirm-tag');

function confirm_delete(tag) {
    background.style.display = 'block';
    box.style.display = 'block';
    confirm_text.innerHTML = "Delete tag '" + tag + "'?";
    confirm_tag.value = tag
}

function cancel() {
    background.style.display = "none";
    box.style.display = "none";
}

// also allow closing popup by clicking outside of it
window.onclick = function(event) {
    if (event.target == background || event.target == row) {
        background.style.display = "none";
        box.style.display = "none";
    }
}