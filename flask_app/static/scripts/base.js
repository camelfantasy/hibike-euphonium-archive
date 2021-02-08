// fadeout for flashed messages
setTimeout(function() {
    $('[id=fadeout]').fadeOut(500,function() {
        $('[id=fadeout]').css({"visibility":"hidden",display:'block'}).slideUp();
    });
}, 5000);

// suppresses default error popup for required form fields
document.addEventListener('invalid', (function () {
    return function (e) {
        e.preventDefault();
    };
})(), true);