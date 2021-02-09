var tag_message_timer = null;
var update_description_timer = null;

// submits add tag form
function submit_add_tag_form(e) {
    $.ajax({
        type: "POST",
        url: add_file_tag_url,
        data: $('#addTagForm').serialize(),
        success: function (data) {
            $("#tag_message").css("visibility", "visible");
            $("#tag_message").css("display", "block");
            $("#tag_box").attr("class", "mt-4");
            $("#tag_message").html(data.message);
            if (data.success == 0) {
                $("#tag_message").attr("class", "alert alert-success fade-message");
                $("#taglist").append(`
                    <div class="form-group row" style="margin:0px" id="tag_` + data.tag.replace(' ', '_') + `">
                        <label class="col-11 col-form-label" style="padding:0px">
                            <a href="` + data.url_for + `" class="tag-link">` + data.tag + `</a>
                        </label>
                        <label class="col-1" style="margin:0px; padding:0px; display:flex; align-items:center; direction:rtl;">
                            <form method="POST" action="" style="margin:0px" id="deleteTagForm_` + data.tag.replace(' ', '_') + `">
                                ` + deletetagform_csrf_token_field + `
                                ` + deletetagform_file_id_field + `
                                <input hidden="" id="tag" name="tag" required="" type="text" value="` + data.tag + `">
                                <svg width="1em" height="1em" viewBox="0 0 16 16" class="bi bi-trash" fill="red" xmlns="http://www.w3.org/2000/svg" style="cursor: pointer" onclick="submit_delete_tag_form('` + data.tag.replace(' ', '_') + `')">
                                    <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                                    <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4L4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                                </svg>
                            </form>
                        </label>
                    </div>
                `)
                
                // removes added tag from tag suggestions
                index = tags.indexOf(data.tag);
                if (index != -1) {
                    tags.splice(index, 1);
                }

                // ensures tag label is correct
                $("#tag-label").html('<b>Tags:</b>');
            } else {
                $("#tag_message").attr("class", "alert alert-warning fade-message");
            }
            $("#myInput").val("");

            // resets timer if handling more than one request before timeout
            if (tag_message_timer) {
                clearTimeout(tag_message_timer)
                tag_message_timer = null;
            }
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
function submit_delete_tag_form(tag) {
    $.ajax({
        type: "POST",
        url: delete_file_tag_url,
        data: $('#deleteTagForm_' + tag).serialize(),
        success: function (data) {
            $("#tag_message").css("visibility", "visible");
            $("#tag_message").css("display", "block");
            $("#tag_box").attr("class", "mt-4");
            $("#tag_message").html(data.message);
            if (data.success == 0) {
                $("#tag_message").attr("class", "alert alert-success fade-message");
                $("#tag_" + tag).remove();
                
                // adds tag to tag suggestions
                tag = tag.replace("_", " ");
                if (tags.indexOf(tag) == -1) {
                    tags.push(tag)
                    tags.sort()
                }

                // ensures tag label is correct
                if ($("#taglist div").length == 1) {
                    $("#tag-label").html('No tags.');
                }
            } else {
                $("#tag_message").attr("class", "alert alert-warning fade-message");
            }

            // resets timer if handling more than one request before timeout
            if (tag_message_timer) {
                clearTimeout(tag_message_timer)
                tag_message_timer = null;
            }
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
    $.ajax({
        type: "POST",
        url: update_file_description_url,
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

            // resets timer if handling more than one request before timeout
            if (update_description_timer) {
                clearTimeout(update_description_timer)
                update_description_timer = null;
            }
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