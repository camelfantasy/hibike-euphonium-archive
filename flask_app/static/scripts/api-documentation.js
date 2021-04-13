data = {
    "unrestricted":[
        {
            "name":"Tags",
            "method":"GET",
            "route":"/api/v1/tags",
            "description":"Returns all tags.",
            "parameters":null,
            "response":`[
    {
        "category": ,
        "tag":
    }
]`
        },
        {
            "name":"All images",
            "method":"GET",
            "route":"/api/v1/all_images/&lt;page&gt;",
            "description":"Returns data for all images in increments of 100.",
            "parameters":null,
            "response":`[
    {
        "description":,
        "file_id": ,
        "folder_id": ,
        "name": ,
        "tags": [
            {
                "category":, 
                "tag":
            }
        ]
    }
]`
        },
        {
            "name":"Tag images",
            "method":"GET",
            "route":"/api/v1/tag_images",
            "description":"Returns data for all images for an exact tag.",
            "parameters":`"tag": case insensitive string`,
            "response":`[
    {
        "description": , 
        "file_id": , 
        "folder_id": , 
        "name":
    }, 
]`
        },
        {
            "name":"Image",
            "method":"GET",
            "route":"/api/v1/image",
            "description":"Returns data for an image.",
            "parameters":`"file_id": string`,
            "response":`{
    "description": , 
    "file_id": ,
    "folder_id": ,
    "name": ,
    "tags": [
        {
            "category": , 
            "tag":
        },
    ]
}`
        },
        {
            "name":"Random image",
            "method":"GET",
            "route":"/api/v1/random_image",
            "description":"Returns data for a random image.",
            "parameters":`"tag": if an empty string is passed, a purely random image will be returned
"exact": if 'True', the tag will match exactly (case sensitive), else it will find the first tag it is a case-insensitive substring of`,
            "response":`{
    "description": , 
    "file_id": ,
    "folder_id": ,
    "name": ,
    "tag": ,
    "tags": [
        {
            "category": , 
            "tag":
        },
    ]
}`
        },
        {
            "name":"Folder",
            "method":"GET",
            "route":"/api/v1/folder",
            "description":"Returns data for a folder.",
            "parameters":`"folder_id": string`,
            "response":`{
    "children": [
        "folder_id"
    ], 
    "description": , 
    "files": [
        "file_id"
    ], 
    "folder_id": , 
    "name": , 
    "parent_id": 
}`
        }
    ],
    "restricted":[

    ]
}

var unrestricted = document.querySelector("#unrestricted");

data.unrestricted.forEach(function(x) {
    unrestricted.innerHTML += `
        <hr style="margin-top:32px; margin-bottom:32px">
        <h2>` + x.name + `</h2>
        <div class="api-route">
            <label class="col-form-label api-` + x.method.toLowerCase() + `">` + x.method + `</label> ` + x.route + `
        </div>
        <br>
        ` + x.description + `
        <br><br>
    `;

    if (x.parameters) {
        unrestricted.innerHTML += `
            <h5>Parameters</h5>
            <pre class="api-pre"><code class="api-code">` + x.parameters + `</code></pre>
            <br>
        `;
    }

    unrestricted.innerHTML += `
        <h5>Sample response</h5>
        <pre class="api-pre"><code class="api-code">` + x.response + `</code></pre>
    `;
});

var restricted = document.querySelector("#restricted");

data.restricted.forEach(function(x) {
    restricted.innerHTML += `
        <hr style="margin-top:32px; margin-bottom:32px">
        <h2>` + x.name + `</h2>
        <div class="api-route">
            <label class="col-form-label api-` + x.method.toLowerCase() + `">` + x.method + `</label> ` + x.route + `
        </div>
        <br>
        ` + x.description + `
        <br><br>
    `;

    if (x.parameters) {
        restricted.innerHTML += `
            <h5>Parameters</h5>
            <pre class="api-pre"><code class="api-code">` + x.parameters + `</code></pre>
            <br>
        `;
    }

    restricted.innerHTML += `
        <h5>Sample response</h5>
        <pre class="api-pre"><code class="api-code">` + x.response + `</code></pre>
    `;
});