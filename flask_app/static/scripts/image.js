var tag_message_timer = null;
var update_description_timer = null;

// add confirmation below
background = document.getElementById('confirm-background');
box = document.getElementById('confirm-box');
row = document.getElementById('confirm-row');
confirm_text = document.getElementById('confirm-text');
add_tag_display = document.getElementById('add-tag-display');
add_annotation_display = document.getElementById('add-annotation-display');

function confirm_add(tag) {
    add_tag_display.style.display = '';
    background.style.display = 'block';
    box.style.display = 'block';
    confirm_text.innerHTML = "Add new tag '" + tag + "'?";
}

function cancel() {
    background.style.display = 'none';
    box.style.display = 'none';
    add_tag_display.style.display = 'none';
    add_annotation_display.style.display = 'none';

    document.getElementById("image-link").style.pointerEvents = "auto";
    click_enabled = false;
    document.getElementById("temp-note-circle").remove();
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



var click_enabled = false;

function get_note_circle_size() {
    widths = [[992, 16], [776, 12], [540, 8], [270, 6], [0, 4]];
    w = screen.width;
    return widths.find((e) => w >= e[0])[1]
    // widths.forEach(function(tuple) {
    //     if (w >= tuple[0]) {
    //         console.log(0);
    //         return tuple[1];
    //     }
    // })
}

function open_click_layer() {
    document.getElementById("image-link").style.pointerEvents = "none";
    document.getElementById("click-layer").style.filter = "brightness(50%)";
    click_enabled = true;
}

document.getElementById("click-layer").onclick = function(e) {
    if (!click_enabled) {
        return;
    }

    // var sheet = document.styleSheets.item.find((e) => e.href.includes("custom.css"))
    // var rule = sheet.cssRules.find((e) => e.selectorText == "note-circle")
    // var font_size = parseInt($('.note-circle').css( "font-size").slice(0, -2));
    // var font_size = parseInt($('.note-circle').css( "font-size").slice(0, -2));
    var font_size = get_note_circle_size();
    var rect = e.target.getBoundingClientRect();
    var x = Math.round((e.clientX - rect.left - font_size / 2) / rect.width * 100);
    var y = Math.round((e.clientY - rect.top - font_size / 2) / rect.height * 100);

    document.getElementById("click-layer").style.filter = "brightness(100%)";
    document.getElementById("image-link").innerHTML += `
        <div class="note-circle" id="temp-note-circle" style="position:absolute; left:` + x + `%; top:` + y + `%; z-index: 1">
            <i class="bi bi-circle-fill" style="opacity:50%; color:red"></i>
            <div class="note-text"></div>
        </div>
    `
    document.getElementById("click-layer").style.filter = "brightness(100%)";

    add_annotation_display.style.display = '';
    background.style.display = 'block';
    box.style.display = 'block';
    confirm_text.innerHTML = "Text";

    document.getElementById('annotation_form_file_id').value = image_id;
    document.getElementById('annotation_form_left').value = x;
    document.getElementById('annotation_form_top').value = y;
}

function submit_add_annotation_form() {
    $.ajax({
        type: "POST",
        url: "/add_annotation",
        data: $('#addannotationform').serialize(),
        success: function(result) {
            if (result.success == "0") {
                var note_circle = document.getElementById("temp-note-circle");
                note_circle.getElementsByTagName('i')[0].style.color = "gold";
                note_circle.getElementsByTagName('div')[0].innerHTML = document.getElementById('annotation_form_text').value;
                note_circle.id = result.annotation_id
            } else if (result.success == "1") {
                document.getElementById("temp-note-circle").remove();
            }

            document.getElementById('annotation_form_text').value = "";
            cancel()
        }
    });
}

// disable saving if text is empty
// multi-add mode?
// switch to show/hide annotations

// move notes above a tag
// add delete function
// add edit function
