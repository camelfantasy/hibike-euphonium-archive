var tag_message_timer = null;
var update_description_timer = null;

// submits add tag form
function submit_add_tag_form(e) {
    // resets timer if handling more than one request before timeout
    if (tag_message_timer) {
        clearTimeout(tag_message_timer)
        tag_message_timer = null;
    }

    // set loading message
    document.getElementById("tag_message").setAttribute("class", "alert alert-secondary");
    document.getElementById("tag_message").style.visibility = "visible";
    document.getElementById("tag_message").style.display = "block";
    document.getElementById("tag_box").className = "mt-4";
    dots = '<span class="dot dot1">.</span><span class="dot dot2">.</span><span class="dot dot3">.</span>';
    document.getElementById("tag_message").innerHTML = "Adding" + dots;

    $.ajax({
        type: "POST",
        url: add_folder_tag_url,
        data: $('#addTagForm').serialize(),
        success: function (data) {
            $("#tag_message").html(data.message);
            if (data.success == 0 || data.success == 2) {
                $("#tag_message").attr("class", "alert alert-success fade-message");
                
                // removes added tag from tag suggestions
                index = tags.indexOf(data.tag);
                if (index != -1) {
                    tags.splice(index, 1);
                }

                // insert tag into search suggestions if newly created
                if (data.success == 2) {
                    if (search_tags.indexOf(data.tag) == -1) {
                        search_tags.push(data.tag)
                        search_tags.sort()
                    }
                }
            } else {
                $("#tag_message").attr("class", "alert alert-warning fade-message");
            }
            $("#myInput").val("");

            // sets fadeout timer
            tag_message_timer = setTimeout(function() {
                if ($('#tag_message').css("visibility") != "hidden") {
                    $('#tag_message').fadeOut(500,function(){
                        $("#tag_box").removeClass("mt-4")
                        $('#tag_message').css({"visibility":"hidden",display:'block'}).slideUp();
                    });
                }
            }, 5000);
        }
    });
    e.preventDefault();

    // adds CSRF token to form
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", addtagform_csrf_token)
            }
        }
    })
}

// sends tag deletion request
function submit_delete_tag_form(e) {
    // resets timer if handling more than one request before timeout
    if (tag_message_timer) {
        clearTimeout(tag_message_timer)
        tag_message_timer = null;
    }

    // set loading message
    document.getElementById("tag_message").setAttribute("class", "alert alert-secondary");
    document.getElementById("tag_message").style.visibility = "visible";
    document.getElementById("tag_message").style.display = "block";
    document.getElementById("tag_box").className = "mt-4";
    dots = '<span class="dot dot1">.</span><span class="dot dot2">.</span><span class="dot dot3">.</span>';
    document.getElementById("tag_message").innerHTML = "Deleting" + dots;

    $.ajax({
        type: "POST",
        url: delete_folder_tag_url,
        data: $('#deleteTagForm').serialize(),
        success: function (data) {
            $("#tag_message").html(data.message);
            if (data.success == 0) {
                $("#tag_message").attr("class", "alert alert-success fade-message");
                
                // adds tag to tag suggestions
                if (tags.indexOf(data.tag) == -1) {
                    tags.push(data.tag)
                    tags.sort()
                }
            } else {
                $("#tag_message").attr("class", "alert alert-warning fade-message");
            }
            $("#deleteInput").val("");

            // sets fadeout timer
            tag_message_timer = setTimeout(function() {
                if ($('#tag_message').css("visibility") != "hidden") {
                    $('#tag_message').fadeOut(500,function(){
                        $("#tag_box").removeClass("mt-4")
                        $('#tag_message').css({"visibility":"hidden",display:'block'}).slideUp();
                    });
                }
            }, 5000);
        }
    });

    // adds CSRF token to form
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", deletetagform_csrf_token)
            }
        }
    })
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
        url: update_folder_description_url,
        data: $('#updateDescriptionForm').serialize(),
        success: function (data) {
            $("#description_message").css("visibility", "visible");
            $("#description_message").css("display", "block");
            $("#description_box").attr("class", "mt-4");
            $("#description_message").html(data.message);
            if (data.success == 0) {
                $("#description_message").attr("class", "alert alert-success fade-message");
            } else {
                $("#description_message").attr("class", "alert alert-warning fade-message");
            }

            // sets fadeout timer
            update_description_timer = setTimeout(function() {
                if ($('#description_message').css("visibility") != "hidden") {
                    $('#description_message').fadeOut(500,function(){
                        $("#description_box").removeClass("mt-4")
                        $('#description_message').css({"visibility":"hidden",display:'block'}).slideUp();
                    });
                }
            }, 5000);
        }
    });

    // adds CSRF token to form
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", updateddescriptionform_csrf_token)
            }
        }
    })
}

// calls tag deletion when enter is pressed
var inp = deleteInput
inp.addEventListener("keydown", function(e) {
    if (e.keyCode == 13) {
        e.preventDefault();
        submit_delete_tag_form();
    }
});