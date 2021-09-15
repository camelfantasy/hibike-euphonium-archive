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

    // resets fadeout timer if handling more than one request before timeout
    if (tag_message_timer) {
        clearTimeout(tag_message_timer)
        tag_message_timer = null;
    }
    
    formdata = $('#addTagForm').serialize();
    $("#myInput").val("");
    $.ajax({
        type: "POST",
        url: "/add_file_tag",
        data: formdata,
        success: function (data) {
            $("#tag_message").html(data.message);
            if (data.success == 0 || data.success == 2) {
                $("#tag_message").attr("class", "alert alert-success");

                // add new tag to correct position
                current_tags = Array.from(document.getElementById("taglist").children).slice(1);
                newNode = document.createElement('div');
                newNode.className = "form-group row";
                newNode.style.margin = "0px";
                newNode.id = "tag_" + data.tag.replace(' ', '_')
                newNode.innerHTML = `
                    <label class="col-11 col-form-label" style="padding:0px">
                        <a href="` + data.url_for + `" class="tag-link">` + data.tag + `</a>
                    </label>
                    <label class="col-1" style="margin:0px; padding:0px; display:flex; align-items:center; direction:rtl;">
                        <form method="POST" action="" style="margin:0px" id="deleteTagForm_` + data.tag.replace(' ', '_') + `">
                            ` + deletetagform_csrf_token_field + `
                            ` + deletetagform_file_id_field + `
                            <input hidden="" id="tag" name="tag" required="" type="text" value="` + data.tag + `">
                            <i class="bi bi-trash" style="color:red; cursor:pointer" onclick="submit_delete_tag_form('` + data.tag.replace(' ', '_') + `')"></i>
                        </form>
                    </label>
                `
                
                // try catch necessary to break forEach
                try {
                    current_tags.forEach(x => {
                        if (("tag_" + data.tag.replace(' ', '_')).toLowerCase() < x.id.toLowerCase()) {
                            x.before(newNode);
                            throw BreakException;
                        }
                    });
                    document.getElementById("taglist").appendChild(newNode);
                } catch {}
                
                // removes added tag from tag suggestions
                index = tags.indexOf(data.tag);
                if (index != -1) {
                    tags.splice(index, 1);
                }

                // updates tag label
                $("#tag-label").html('<b>Tags (' + ($("#taglist div").length - 1) + '):</b>');

                // insert tag into search suggestions if newly created
                if (data.success == 2) {
                    if (search_tags.indexOf(data.tag) == -1) {
                        search_tags.push(data.tag)
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
function submit_delete_tag_form(tag) {
    // resets fadeout timer if handling more than one request before timeout
    if (tag_message_timer) {
        clearTimeout(tag_message_timer)
        tag_message_timer = null;
    }

    $.ajax({
        type: "POST",
        url: "/delete_file_tag",
        data: $('#deleteTagForm_' + tag).serialize(),
        success: function (data) {
            $("#tag_message").html(data.message);
            if (data.success == 0) {
                $("#tag_message").attr("class", "alert alert-success");
                $("#tag_" + tag).remove();
                
                // adds tag to tag suggestions
                tag = tag.replace("_", " ");
                if (tags.indexOf(tag) == -1) {
                    tags.push(tag)
                    tags.sort()
                }

                // updates tag label
                if ($("#taglist div").length == 1) {
                    $("#tag-label").html('No tags.');
                } else {
                    $("#tag-label").html('<b>Tags (' + ($("#taglist div").length - 1) + '):</b>');
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

// sends update description request
function submit_update_description_form() {
    // resets fadeout timer if handling more than one request before timeout
    if (update_description_timer) {
        clearTimeout(update_description_timer)
        update_description_timer = null;
    }

    $.ajax({
        type: "POST",
        url: "/update_file_description",
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

function star(id) {
    $.ajax({
        type: "POST",
        url: "/star/" + id,
        data: $('#starForm').serialize(),
        success: function(result){
            if (result == "0") {
                $("#star").addClass("bi-star-fill");
                $("#star").removeClass("bi-star");
            } else if (result == "1") {
                $("#star").addClass("bi-star");
                $("#star").removeClass("bi-star-fill");
            }
        }
    });
}