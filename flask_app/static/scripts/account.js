var message_1_timer = null;
var message_3_timer = null;

// sync below drive to database below
function ajax_sync() {
    document.getElementById("sync_button").disabled = true;
    document.getElementById("sync_button").setAttribute("class", "form-control btn-submit-disabled");

    document.getElementById("sync_message").setAttribute("class", "alert alert-secondary");
    document.getElementById("sync_message").style.visibility = "visible";
    document.getElementById("sync_message").style.display = "block";
    document.getElementById("sync_col").className = "col-11 col-lg-2 order-lg-2 mt-4 mt-lg-0";

    var waiting_to_sync;
    $.ajax({
        type: "POST",
        url: "/sync",
        data: $('#syncForm').serialize(),
        success: function(result){
            $("#sync_message").attr("class", "alert alert-secondary");
            dots = '<span class="dot dot1">.</span><span class="dot dot2">.</span><span class="dot dot3">.</span>';
            if (result == "2") {
                $("#sync_message").html("Syncing" + dots);
                waiting_to_sync = false;
            } else if (result == "3") {
                $("#sync_message").html("Wait" + dots);
                waiting_to_sync = true;
            }
        }
    });

    // check result of sync every 5 seconds
    timer = setInterval(function() {
        $.ajax({url: "/sync_progress", success: function(result){
            if (!result['syncing']) {
                if (waiting_to_sync) {
                    $("#sync_message").html("Sync available.");
                } else if (result['last_sync'] == "0") {
                    $("#sync_message").html("Sync success.");
                    $("#sync_message").attr("class", "alert alert-success");
                } else if (result['last_sync'] == "1") {
                    $("#sync_message").html("Sync failed.");
                    $("#sync_message").attr("class", "alert alert-danger");
                }
                $("#sync_button").prop("disabled", false);
                $("#sync_button").attr("class", "form-control btn-submit");
                clearInterval(timer);
            }
        }});
    }, 5000);
}

// delete account below
background = document.getElementById('confirm-background');
box = document.getElementById('confirm-box');
row = document.getElementById('confirm-row');
confirm_text = document.getElementById('confirm-text');
confirm_user = document.getElementById('confirm-user');
user_form = document.getElementById('user-form');
account_form = document.getElementById('account-form');

function confirm_delete(user) {
    background.style.display = 'block';
    box.style.display = 'block';
    user_form.style.display = 'block';
    confirm_text.innerHTML = "Delete user '" + user + "'?";
    confirm_user.value = user
}

function confirm_delete_account() {
    background.style.display = 'block';
    box.style.display = 'block';
    account_form.style.display = 'block';
    confirm_text.innerHTML = "Delete account?";
}

function cancel() {
    background.style.display = 'none';
    box.style.display = 'none';
    user_form.style.display = 'none';
    account_form.style.display = 'none';
}

// also allow closing popup by clicking outside of it
window.onclick = function(event) {
    if (event.target == background || event.target == row) {
        cancel();
    }
}

function replace_api_key() {
    $.ajax({
        type: "POST",
        url: "/replace_api_key",
        data: $('#replaceApiKeyForm').serialize(),
        success: function(result){
            $("#api_key").html(result);
            $('#message_box_2').slideDown(250,function(){
                $('#message_box_2').css({"visibility":"visible",display:'none'}).fadeIn(250);
            });
        }
    });
}

function delete_api_key() {
    $.ajax({
        type: "POST",
        url: "/delete_api_key",
        data: $('#deleteApiKeyForm').serialize(),
        success: function(){
            $("#api_key").html("Key not set");
            if ($('#message_box_2').css("visibility") != "hidden") {
                $('#message_box_2').fadeOut(500,function(){
                    $('#message_box_2').css({"visibility":"hidden",display:'block'}).slideUp(500);
                });
            }
        }
    });
}

function change_password() {
    if (message_1_timer) {
        clearTimeout(message_1_timer)
        message_1_timer = null;
    }

    $.ajax({
        type: "POST",
        url: "/change_password",
        data: $('#changePasswordForm').serialize(),
        success: function (data) {
            $("#password").val('');
            $("#confirm_password").val('');
            if (data.success == 0) {
                $("#message_box").attr("class", "alert alert-success");
                $("#message").html(data.message);
            } else {
                $("#message_box").attr("class", "alert alert-warning");
                $("#message").html(data.message);
            }

            if ($('#message_box').css("visibility") != "visible") {
                $('#message_box').slideDown(250,function(){
                    $('#message_box').css({"visibility":"visible",display:'none'}).fadeIn(250);
                });
            }

            // sets fadeout timer
            message_1_timer = setTimeout(function() {
                if ($('#message_box').css("visibility") != "hidden") {
                    $('#message_box').fadeOut(500,function(){
                        $('#message_box').css({"visibility":"hidden",display:'block'}).slideUp(500);
                    });
                }
            }, 5000);
        }
    });
}

document.getElementById("confirm_password").addEventListener("keydown", function(e) {
    if (e.keyCode == 13) { // enter
        change_password();
    }
});

function change_level(user) {
    if (message_3_timer) {
        clearTimeout(message_3_timer)
        message_3_timer = null;
    }

    $.ajax({
        type: "POST",
        url: "/change_level",
        data: $('#' + user + '_level').serialize(),
        success: function (data) {
            if (data.success == 0) {
                $("#message_box_3").attr("class", "alert alert-success");
                $("#message_3").html(data.message);
            } else {
                $("#message_box_3").attr("class", "alert alert-warning");
                $("#message_3").html(data.message);
            }

            if ($('#message_box_3').css("visibility") != "visible") {
                $('#message_box_3').slideDown(250,function(){
                    $('#message_box_3').css({"visibility":"visible",display:'none'}).fadeIn(250);
                });
            }

            // sets fadeout timer
            message_3_timer = setTimeout(function() {
                if ($('#message_box_3').css("visibility") != "hidden") {
                    $('#message_box_3').fadeOut(500,function(){
                        $('#message_box_3').css({"visibility":"hidden",display:'block'}).slideUp(500);
                    });
                }
            }, 5000);
        }
    });
}

function delete_user() {
    cancel();

    if (message_3_timer) {
        clearTimeout(message_3_timer)
        message_3_timer = null;
    }

    $.ajax({
        type: "POST",
        url: "/delete_user",
        data: $('#user-form').serialize(),
        success: function (data) {
            if (data.success == 0) {
                $("#message_box_3").attr("class", "alert alert-success");
                $("#message_3").html(data.message);
            } else {
                $("#message_box_3").attr("class", "alert alert-warning");
                $("#message_3").html(data.message);
            }

            if ($('#message_box_3').css("visibility") != "visible") {
                $('#message_box_3').slideDown(250,function(){
                    $('#message_box_3').css({"visibility":"visible",display:'none'}).fadeIn(250);
                });
            }

            // sets fadeout timer
            message_3_timer = setTimeout(function() {
                if ($('#message_box_3').css("visibility") != "hidden") {
                    $('#message_box_3').fadeOut(500,function(){
                        $('#message_box_3').css({"visibility":"hidden",display:'block'}).slideUp(500);
                    });
                }
            }, 5000);
            
            user_row = '#' + $('#confirm-user').val() + '_row';
            $(user_row).fadeOut(500,function(){
                $(user_row).css({"visibility":"hidden",display:'block'}).slideUp(500,function(){
                    $(user_row).remove();
                });
            });
        }
    });
}