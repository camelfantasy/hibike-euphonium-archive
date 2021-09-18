var tag_message_timer = null;
var update_description_timer = null;

// add confirmation below
background = document.getElementById('confirm-background');
box = document.getElementById('confirm-box');
row = document.getElementById('confirm-row');
confirm_text = document.getElementById('confirm-text');

function confirm_add(tag) {
    background.style.display = 'block';
    box.style.display = 'block';
    confirm_text.innerHTML = "Add new tag '" + tag + "'?";
}

function cancel() {
    background.style.display = 'none';
    box.style.display = 'none';
}

// also allow closing popup by clicking outside of it
window.onclick = function(event) {
    if (event.target == background || event.target == row) {
        cancel();
    }
}

// submits add tag form
function submit_add_tag_form(isConfirmation) {
    newtag = document.getElementById("myInput").value.trim();

    // ignores blank tag
    if (!newtag) return;

    // confirmation if user is adding new tag
    if (!isConfirmation && user_level < 2 && search_tags.map((x) => { return x.toLowerCase(); }).indexOf(newtag.toLowerCase()) == -1) {
        confirm_add(newtag);
        return;
    }
    cancel();
    
    // resets timer if handling more than one request before timeout
    if (tag_message_timer) {
        clearTimeout(tag_message_timer)
        tag_message_timer = null;
    }

    formdata = $('#addTagForm').serialize();
    $("#myInput").val("");

    $.ajax({
        type: "POST",
        url: "/add_folder_tag",
        data: formdata,
        success: function (data) {
            $("#tag_message").html(data.message);
            if (data.success == 0 || data.success == 2) {
                $("#tag_message").attr("class", "alert alert-success");
                
                // removes added tag from add_tags and adds to delete_tags
                index = add_tags.indexOf(data.tag);
                if (index != -1) {
                    add_tags.splice(index, 1);
                }
                if (delete_tags.indexOf(data.tag) == -1) {
                    delete_tags.push(data.tag);
                    delete_tags.sort();
                }

                // insert tag into search suggestions if newly created
                if (data.success == 2) {
                    if (search_tags.indexOf(data.tag) == -1) {
                        search_tags.push(data.tag);
                        search_tags.sort(function (a, b) {
                            return a.toLowerCase().localeCompare(b.toLowerCase());
                        })
                    }
                }
            } else {
                $("#tag_message").attr("class", "alert alert-warning");
            }

            if ($('#tag_box').css("visibility") != "visible") {
                $('#tag_box').slideDown(250,function(){
                    $('#tag_box').css({"visibility":"visible",display:'none'}).fadeIn(250);
                });
            }

            // sets fadeout timer
            tag_message_timer = setTimeout(function() {
                if ($('#tag_box').css("visibility") != "hidden") {
                    $('#tag_box').fadeOut(500,function(){
                        $('#tag_box').css({"visibility":"hidden",display:'block'}).slideUp(500);
                    });
                }
            }, 5000);
        }
    });
}

// sends tag deletion request
function submit_delete_tag_form() {
    // resets timer if handling more than one request before timeout
    if (tag_message_timer) {
        clearTimeout(tag_message_timer)
        tag_message_timer = null;
    }

    formdata = $('#deleteTagForm').serialize();
    $("#deleteInput").val("");
    $.ajax({
        type: "POST",
        url: "/delete_folder_tag",
        data: formdata,
        success: function (data) {
            $("#tag_message").html(data.message);
            if (data.success == 0) {
                $("#tag_message").attr("class", "alert alert-success");
                
                // adds tag to add_tags and removes from delete_tags
                if (add_tags.indexOf(data.tag) == -1) {
                    add_tags.push(data.tag)
                    add_tags.sort()
                }
                index = delete_tags.indexOf(data.tag);
                if (index != -1) {
                    delete_tags.splice(index, 1);
                }
            } else {
                $("#tag_message").attr("class", "alert alert-warning");
            }
            $("#deleteInput").val("");

            if ($('#tag_box').css("visibility") != "visible") {
                $('#tag_box').slideDown(250,function(){
                    $('#tag_box').css({"visibility":"visible",display:'none'}).fadeIn(250);
                });
            }

            // sets fadeout timer
            tag_message_timer = setTimeout(function() {
                if ($('#tag_box').css("visibility") != "hidden") {
                    $('#tag_box').fadeOut(500,function(){
                        $('#tag_box').css({"visibility":"hidden",display:'block'}).slideUp(500);
                    });
                }
            }, 5000);
        }
    });
}

// sends update description request
function submit_update_description_form() {
    // resets timer if handling more than one request before timeout
    if (update_description_timer) {
        clearTimeout(update_description_timer)
        update_description_timer = null;
    }

    $.ajax({
        type: "POST",
        url: "/update_folder_description",
        data: $('#updateDescriptionForm').serialize(),
        success: function (data) {
            $("#description_message").html(data.message);
            if (data.success == 0) {
                $("#description_message").attr("class", "alert alert-success");
            } else {
                $("#description_message").attr("class", "alert alert-warning");
            }

            if ($('#description_box').css("visibility") != "visible") {
                $('#description_box').slideDown(250,function(){
                    $('#description_box').css({"visibility":"visible",display:'none'}).fadeIn(250);
                });
            }

            // sets fadeout timer
            update_description_timer = setTimeout(function() {
                if ($('#description_box').css("visibility") != "hidden") {
                    $('#description_box').fadeOut(500,function(){
                        $('#description_box').css({"visibility":"hidden",display:'block'}).slideUp(500);
                    });
                }
            }, 5000);
        }
    });
}