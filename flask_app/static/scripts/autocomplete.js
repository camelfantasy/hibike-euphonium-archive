// tag autocomplete below
function autocomplete(inp, arr) {
    var currentFocus;

    // checks for new input
    inp.addEventListener("input", function(e) {
        var a, b, i, val = this.value;
        closeAllLists();
        if (!val) { return false;}
        currentFocus = -1;
        
        // div element containing tags
        a = document.createElement("DIV");
        a.setAttribute("id", this.id + autocomplete_list_name);
        a.setAttribute("class", autocomplete_items_name);
        this.parentNode.appendChild(a);
        
        var numItems = 0;
        for (i = 0; i < arr.length; i++) {
            // check for same initial letters ignoring case and limits results to 5
            if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase() && numItems++ < 5) {
                b = document.createElement("DIV");
                b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
                b.innerHTML += arr[i].substr(val.length);
                b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
                b.setAttribute("style", "padding:3px")

                // called when tag is clicked
                b.addEventListener("click", function(e) {
                    inp.value = this.getElementsByTagName("input")[0].value;
                    closeAllLists();
                });
            a.appendChild(b);
            }
        }

        // selects first item
        if (numItems > 0) {
            var x = document.getElementById(this.id + autocomplete_list_name);
            if (x) x = x.getElementsByTagName("div");
            currentFocus++;
            addActive(x);
        }
    });

    // checks when key is pressed
    inp.addEventListener("keydown", function(e) {
        var x = document.getElementById(this.id + autocomplete_list_name);
        if (x) x = x.getElementsByTagName("div");
        if (e.keyCode == 40) { // down
            currentFocus++;
            addActive(x);
        } else if (e.keyCode == 38) { // up
            currentFocus--;
            addActive(x);
        } else if (e.keyCode == 13 && document.getElementsByClassName(autocomplete_active_name).length != 0) { // enter
            e.preventDefault();
            if (currentFocus > -1) {
                if (x) x[currentFocus].click();
            }
        }
    });

    // select tag
    function addActive(x) {
        if (!x) return false;
        removeActive(x);
        if (currentFocus >= x.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (x.length - 1);
        x[currentFocus].classList.add(autocomplete_active_name);
    }

    // deselect tag
    function removeActive(x) {
        for (var i = 0; i < x.length; i++) {
            x[i].classList.remove(autocomplete_active_name);
        }
    }

    // close tag list
    function closeAllLists(elmnt) {
        var x = document.getElementsByClassName(autocomplete_items_name);
        for (var i = 0; i < x.length; i++) {
            if (elmnt != x[i] && elmnt != inp) {
                x[i].parentNode.removeChild(x[i]);
            }
        }
    }

    document.addEventListener("click", function (e) {
        closeAllLists(e.target);
    });
}