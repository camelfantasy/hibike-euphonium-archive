var message_timer = null;
background = document.getElementById('confirm-background');
box = document.getElementById('confirm-box');
row = document.getElementById('confirm-row');
confirm_text = document.getElementById('confirm-text');
confirm_tag = document.getElementById('confirm-tag');

function confirm_delete() {
    background.style.display = 'block';
    box.style.display = 'block';
    tag = document.getElementById('deleteTagField').value;
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

function fix_category() {
    tag = $('#modifyCategoryField').val();
    category = tags_dict[tag];
    
    selectfield = document.getElementById('modifyCategoryField');
    for (i = 0; i < selectfield.options.length; i++) {
        if (selectfield[i].value == category) {
            selectfield.options[i].selected = true;
            return;
        }
    }
}

function fix_tags(result) {
    // re-sort tags
    all_tags = Object.keys(tags_dict);
    all_tags.sort(function (a, b) {
        return a.toLowerCase().localeCompare(b.toLowerCase());
    })

    // fix modify and delete drop-down lists
    newHtml = "";
    all_tags.forEach(x => {
        newHtml += `<option value=` + x + `>` + x + `</option>`
    });
    document.getElementById('modifyTagField').innerHTML = newHtml;
    document.getElementById('deleteTagField').innerHTML = newHtml;

    // change selected tag on modify tab
    if (result != null) {
        selectfield = document.getElementById('modifyTagField');
        for (i = 0; i < selectfield.options.length; i++) {
            if (selectfield[i].value == result) {
                selectfield.options[i].selected = true;
                break;
            }
        }
    }

    // split tags into categories
    tag_lists = {'Characters':[], 'Media':[], 'Other':[], 'Unsorted':[]};
    all_tags.forEach(x => {
        tag_lists[tags_dict[x]].push(x);
    });

    // split characters into columns
    characters = tag_lists['Characters'];
    mod = characters.length % 3
	div = Math.floor(characters.length / 3)
	split1 = mod == 0 ? div : div + 1
	split2 = mod != 1 ? 2*split1 : 2*div+1

	Characters1 = characters.slice(0, split1)
	Characters2 = characters.slice(split1,split2)
	Characters3 = characters.slice(split2,characters.length)

    // fix displayed tags
    columns = {'characters1Col':Characters1, 'characters2Col':Characters2, 'characters3Col':Characters3,
            'mediaCol':tag_lists['Media'], 'otherCol':tag_lists['Other'], 'unsortedCol':tag_lists['Unsorted']}
    for (col in columns) {
        newHtml = "";
        columns[col].forEach(x => {
            newHtml += `<a href="/search-results/` + x + `" class="tag-link" style="word-wrap: break-word;">` + x + `</a><br>`;
        });
        document.getElementById(col).innerHTML = newHtml;
    }
}

function ajax_call(url, form, success_function) {
    if (message_timer) {
        clearTimeout(message_timer)
        message_timer = null;
    }
    $.ajax({
        type: "POST",
        url: url,
        data: $('#' + form).serialize(),
        success: function (data) {
            if (data.success == 0) {
                $("#message_box").attr("class", "alert alert-success");
                $("#message").html(data.message);

                result = success_function();
                search_tags.sort(function (a, b) {
                    return a.toLowerCase().localeCompare(b.toLowerCase());
                })
                fix_tags(result);
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
            message_timer = setTimeout(function() {
                if ($('#message_box').css("visibility") != "hidden") {
                    $('#message_box').fadeOut(500,function(){
                        $('#message_box').css({"visibility":"hidden",display:'block'}).slideUp(500);
                    });
                }
            }, 5000);
        }
    });
}

function add_tag() {
    tag = document.getElementById('addTagField').value
    if (tag == "" || tag.match(/^ *$/)) {
        return;
    }

    var success_function = function () {
        tag = document.getElementById('addTagField').value;
        category = document.getElementById('addCategoryField').value;

        tags_dict[tag] = category;
        search_tags.push(tag);

        document.getElementById('addTagField').value = "";
        return null;
    };

    ajax_call("/add_tag", "addTagForm", success_function);
}

function modify_tag() {
    var success_function = function () {
        tag = document.getElementById('modifyTagField').value;
        new_tag = document.getElementById('modifyNewTagField').value;
        category = document.getElementById('modifyCategoryField').value;
        
        tags_dict[new_tag] = category;
        delete tags_dict[tag];

        search_tags.push(new_tag);
        search_tags.splice(search_tags.indexOf(tag), 1);

        document.getElementById('modifyNewTagField').value = "";
        return new_tag;
    };

    ajax_call("/modify_tag", "modifyTagForm", success_function);
}

function delete_tag() {
    cancel()
    var success_function = function () {
        tag = document.getElementById('deleteTagField').value;

        delete tags_dict[tag];
        search_tags.splice(search_tags.indexOf(tag), 1);
        return null;
    };

    ajax_call("/delete_tag", "deleteTagForm", success_function);
}

// call function on page load to fix category of selected tag on modify tab
fix_category()