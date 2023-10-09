function getList() {
    $.ajax({
        url: "/socialnetwork/get_list_json",
        dataType : "json",
        success: function(items) {
            update_post_list(items);
            update_comment_list(items);
        }
    });
}

function update_comment_list(items) {
    var comments = JSON.parse(items['comments']);
    // console.log(pk_comment);
    var updated_pk_comment = comments.length-1;
    // console.log(updated_pk_comment);
    // console.log("#########################");
    var post_number = items['post_id'];
    var num_comments = items['num_comments'];
    for (var i = pk_comment; i <= updated_pk_comment; ++i)
    {
        this_comment = comments[i];
        $("#comments_for_post_"+this_comment.fields.post).append(
            "<li class='comment_bullet'>" + 
            "<a href=\'/socialnetwork/someone_profile?created_by=" + 
            sanitize(this_comment.fields.created_by_username) + "\'>" + 
            sanitize(this_comment.fields.created_by_username) + "</a>" + "\xa0\xa0\xa0\xa0\xa0" +
            sanitize(this_comment.fields.content) +
            "</li>"
        );
    }
    $("#"+post_number+"_metadata" + " span[data-id='num_comments']").text(num_comments);
    pk_comment = updated_pk_comment + 1;
}

function sanitize(s) {
    // Be sure to replace ampersand first
    return s.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
}

function displayError(message) {
    $("#error").html(message);
}

function getCSRFToken() {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
        if (cookies[i].startsWith("csrftoken=")) {
            return cookies[i].substring("csrftoken=".length, cookies[i].length);
        }
    }
    return "unknown";
}

function addItem(postID) {
    var itemTextElement = $("#item."+postID);
    var itemTextValue   = itemTextElement.val();
    var last_update_time = new Date().getTime()/1000;

    // Clear input box and old error message (if any)
    itemTextElement.val('');
    displayError('');

    // data-->url-->success
    $.ajax({
        url: "/socialnetwork/add_comment",
        type: "POST",
        data: { this_post:           itemTextValue, 
                current_post_id:     postID,
                last_update_time:    last_update_time,
                csrfmiddlewaretoken: getCSRFToken() },
        dataType : "json",
        success: function(response) {
            if ('error' in response){
                displayError(response.error);
            } else {
                update_comment_list(response);
            }
        }
    });
}

function update_post_list(items) {
    var posts = JSON.parse(items['posts']);
    var comments = JSON.parse(items['comments']);
    var updated_pk_post = posts.length-1;
    var relates_icon = document.getElementById("relates_img").getAttribute("data-image-path");
    var hugs_icon = document.getElementById("hugs_img").getAttribute("data-image-path");
    var comments_icon = document.getElementById("comments_img").getAttribute("data-image-path");
    for (var i = pk_post; i <= updated_pk_post; ++i)
    {
        this_post = posts[i];
        // console.log(this_post);
        var d = new Date(this_post.fields.creation_time);
        

        $(".post_items").prepend(
            "<div class='post_item'>" + 
            "<div class='title'>" + sanitize(this_post.fields.title) + "</div>" +
            "<div class='post_head'>" +
            "<a href=\'/socialnetwork/someone_profile?created_by=" + 
            sanitize(this_post.fields.created_by_username) + 
            "\'>" + sanitize(this_post.fields.created_by_username) + "<br/></a>" +  
            "</div>" +
            
            "<div class='content'>" + sanitize(this_post.fields.content) + "</div>" +
            
            "<div id=\"" + sanitize(this_post.fields.created_by_identity) + "_metadata\">" +
                "<span class='relates' onclick=\"relate(\'" + sanitize(this_post.fields.created_by_identity) + "\')\">" + "<img src="+relates_icon+ " alt='relates'>" + "<span data-id='relates'>" + this_post.fields.num_relates + "</span>" + " relates" + "</span>" + "\xa0\xa0\xa0\xa0\xa0" +
                "<span class='hugs' onclick=\"hug(\'" + sanitize(this_post.fields.created_by_identity) + "\')\">" + "<img src="+hugs_icon+ " alt='hugs'>" + "<span data-id='hugs'>" + this_post.fields.num_hugs + "</span>" + " hugs" + "</span>" + "\xa0\xa0\xa0\xa0\xa0" +
                "<span class='comments' onclick=\"toggleComment(\'" + sanitize(this_post.fields.created_by_identity) + "\')\">" + "<img src="+comments_icon + " alt='comments'>" + "<span data-id='num_comments'>" + this_post.fields.num_comments + "</span>" + "</span>" + "  " +
                "<span class='date'>" + d.toLocaleDateString() + " " + d.toLocaleTimeString() + "</span>" +
            "</div>" +
            
            "<div class='comment_list' id='" + sanitize(this_post.fields.created_by_identity) + "'>" + 
            "<label>Leave a comment: </label>" + 
            "<input id='item' type='text' name='item' class='" + 
            sanitize(this_post.fields.created_by_identity) + "'>" + 
            "<button onclick=\"addItem(\'" + 
            sanitize(this_post.fields.created_by_identity) + "\')\">Add item</button>" + 
            "<span id=\"error\" class=\"error\"></span>"  + 
            "<ul id=\"comments_for_post_" + 
            sanitize(this_post.fields.created_by_identity) + "\"></ul>" + 
            "</div>" + 
            "</div>" 
        );
    }
    pk_post = updated_pk_post + 1;
}

function toggleComment(postID) {
    $(".comment_list#"+postID).toggle();
}

function toggleWait() {
    $(".waiting_box").toggle()
}

function relate(postID) {
    $.ajax({
        url: "/socialnetwork/relate",
        type: "POST",
        data: { current_post_id:     postID,
                csrfmiddlewaretoken: getCSRFToken() },
        dataType : "json",
        success: function(response) {
            if ('error' in response){
                displayError(response.error);
            } else {
                update_relates(response);
            }
        }
    });
}

function update_relates(items) {
    var post_number = items['post_id'];
    var num_relates = items['num_relates'];
    $("#"+post_number+"_metadata" + " span[data-id='relates']").text(num_relates);
}

function hug(postID) {
    $.ajax({
        url: "/socialnetwork/hug",
        type: "POST",
        data: { current_post_id:     postID,
                csrfmiddlewaretoken: getCSRFToken() },
        dataType : "json",
        success: function(response) {
            if ('error' in response){
                displayError(response.error);
            } else {
                update_hugs(response);
            }
        }
    });
}

function update_hugs(items) {
    var post_number = items['post_id'];
    var num_hugs = items['num_relates'];
    $("#"+post_number+"_metadata" + " span[data-id='hugs']").text(num_hugs);
}

function chat() {
    var itemTextElement = $("#answer");
    var itemTextValue   = itemTextElement.val();

    // Clear input box and old error message (if any)
    itemTextElement.val('');
    displayError('');

    $(".chat-container").append(
        "<li class='message sent'>" + 
        sanitize(itemTextValue) + 
        "</li>"
    );

    toggleWait();

    // // data-->url-->success
    $.ajax({
        url: "/socialnetwork/chat",
        type: "POST",
        data: { message:           itemTextValue, 
                csrfmiddlewaretoken: getCSRFToken() },
        dataType : "json",
        success: function(response) {
            if ('error' in response){
                displayError(response.error);
            } else {
                update_chat(response);
            }
        }
    });
}

function update_chat(items) {
    var answer = items['answer'];
    $(".chat-container").append(
        "<li class='message received'>" + 
        sanitize(answer) + 
        "</li>"
    );
    toggleWait();
}

window.onload = function(){
    getList();
    pk_post = 0;
    pk_comment = 0;
}

// need pk here too!
window.setInterval(getList, 2000);