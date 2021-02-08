// sync below drive to database below
function ajax_sync() {
    document.getElementById("sync_button").disabled = true;
    document.getElementById("sync_button").setAttribute("class", "form-control btn-submit-disabled");

    document.getElementById("sync_message").setAttribute("class", "alert alert-secondary");
    document.getElementById("sync_message").style.visibility = "visible";
    document.getElementById("sync_message").style.display = "block";
    document.getElementById("sync_col").className = "col-lg-2 order-lg-2 mt-4 mt-lg-0";
    
    dots = '<span class="dot dot1">.</span><span class="dot dot2">.</span><span class="dot dot3">.</span>';
    document.getElementById("sync_message").innerHTML = "Syncing" + dots;

    $.ajax({url: "/sync", success: function(result){
        $("#sync_button").prop("disabled", false);
        $("#sync_button").attr("class", "form-control btn-submit");
        if (result == "0") {
            $("#sync_message").html("Sync success.");
            $("#sync_message").attr("class", "alert alert-success fade-message");
        } else if (result == "1") {
            $("#sync_message").html("Sync failed.");
            $("#sync_message").attr("class", "alert alert-danger fade-message");
        }
        setTimeout(function() {
            $('[id=sync_message]').fadeOut(500,function(){
                $("#sync_col").removeClass("mt-4")
                $("#sync_col").removeClass("mt-lg-0")
                $('[id=sync_message]').css({"visibility":"hidden",display:'block'}).slideUp();
            });
        }, 5000);
    }});
}

// delete account below
background = document.getElementById('confirm-background');
box = document.getElementById('confirm-box');
row = document.getElementById('confirm-row');
confirm_text = document.getElementById('confirm-text');
confirm_user = document.getElementById('confirm-user');

function confirm_delete(user) {
    background.style.display = 'block';
    box.style.display = 'block';
    confirm_text.innerHTML = "Delete user '" + user + "'?";
    confirm_user.value = user
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