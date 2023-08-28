var scroller = document.querySelector("#scroller");
var template_row = document.querySelector('#new_row');
var loaded = document.querySelector("#loaded");
var sentinel = document.querySelector('#sentinel');

// disable sentinel if unnecessary
if (remaining_results.length <= 10) {
    sentinel.innerHTML = "";
}

// loads more images
function loadItems() {
    if (remaining_results.length > 0) {
        new_section = [];
        if (remaining_results.length < 10) {
            new_section = remaining_results.slice(0,remaining_results.length);
            remaining_results = [];
        } else {
            new_section = remaining_results.slice(0, 10);
            remaining_results = remaining_results.slice(10,remaining_results.length);
        }
        
        new_section.forEach(function(new_row) {
            let template_clone = template_row.content.cloneNode(true);
            var innerhtml = "";
            new_row.forEach(function(file_info) {
                file_id = file_info[0]
                file_name = file_info[1]

                var href = "/file/" + file_id;
                var src = 'https://drive.google.com/thumbnail?id=' + file_id;
                
                innerhtml += `  <div class="col-lg-3 col-md-6 col-sm-12 d-flex justify-content-center" style="height:235px; display:flex; align-items: center;">
                                    <a href="` + href + `" id="link" target="_blank">
                                        <img src="` + src + `" style="max-width:100%; max-height:100%" id="image">
                                    </a>`;
                
                if (file_name.includes(".mp4")) {
                    innerhtml += `<i class="bi bi-film" style="color:gray; position:absolute; bottom:5%; right:5%; font-size:20px;"></i>`;
                }

                if (user_authenticated) {
                    innerhtml += `<form style="color:gold; position:absolute; top:5%; left:5%; margin-bottom:0px; font-size:20px;" id="starForm_` + file_id + `" onclick="star('` + file_id + `')">`;
                    innerhtml += starform_csrf_token_field;
                    innerhtml += favorites.indexOf(file_id) == -1 ? `<i class="bi bi-star"` : `<i class="bi bi-star-fill"`;
                    innerhtml += ` id="star_` + file_id + `"></i>`;
                }
                
                innerhtml += `</div></form>`;
            })
            template_clone.querySelector("#row").innerHTML = innerhtml;
            scroller.appendChild(template_clone);
        })
    } else {
        sentinel.innerHTML = "";
    }
}

// time used to prevent function being called more than once at the same time
var time = Date.now()

// detects if end of page is reached
var intersectionObserver = new IntersectionObserver(entries => {
    if (entries[0].intersectionRatio <= 0 || Date.now() - time < 10) {
        return;
    }
    loadItems();
    time = Date.now()
});

intersectionObserver.observe(sentinel);

// star function
function star(id) {
    $.ajax({
        type: "POST",
        url: "/star/" + id,
        data: $('#starForm_' +  id).serialize(),
        success: function(result){
            if (result == "0") {
                $("#star_" + id).addClass("bi-star-fill");
                $("#star_" + id).removeClass("bi-star");
            } else if (result == "1") {
                $("#star_" + id).addClass("bi-star");
                $("#star_" + id).removeClass("bi-star-fill");
            }
        }
    });
}