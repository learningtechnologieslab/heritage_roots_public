function populate_list(url, link_target, link_text, target_div_id, label){
    $.getJSON(url, function(data){
        // console.log(data);
        if(data && data.length > 0){
            for(var i = 0; i<data.length; i++){
                $tr = $('<tr></tr>');
                $td = $('<td></td>');
                
                var visible_text = "";

                if(label == "Animal" || label == "Plant"){
                    if(Object.hasOwnProperty(data[i], link_text)){
                        visible_text = data[i][link_text];
                    }
                    else{
                        visible_text = data[i]['common_name'];
                    }
                    if(String(visible_text).length < 1){
                        visible_text = data[i]['scientific_name'];
                    }
                    if(String(visible_text).length > 25){
                        visible_text = visible_text.substring(0, 25) + "...";
                    }
                }
                else{
                    visible_text = data[i][link_text];
                }
                
                
                var tooltip = data[i][link_text]

                var href = data[i][link_target];
                
                // href = "{{story_worlds_files}}"
                
                
                switch(label){
                    case "Plant":
                        href="view_entity?entity_id=" + data[i]['id'] + "&entity_label=Plant&browse_target=plants";
                        break;
                    case "Animal":
                        href="view_entity?entity_id=" + data[i]['id'] + "&entity_label=Animal&browse_target=animals";
                        break;
                    case "File":
                        href = "download?file_id="+data[i]['id']+"&filename=" + data[i][link_target];
                        break;
                    case "Media":
                        href = data[i][link_target];
                        break;
                    case "Country":
                        href = "https://www.google.com/maps/place/" + data[i][link_text];
                        break;
                    case "Narrative":
                        href="view_entity?entity_id=" + data[i]['id'] + "&entity_label=Narrative&browse_target=narratives";
                        break;
                    case "Object":
                        href="view_entity?entity_id=" + data[i]['id'] + "&entity_label=Object&browse_target=objects";
                        break;
                    case "Language":
                        href="view_entity?entity_id=" + data[i]['id'] + "&entity_label=Language&browse_target=languages";
                        break;
                    default:
                        href = data[i][link_target];
                        break;
                }
                $a = $('<a></a>').attr({
                    "href" : href,
                    "title" : tooltip
                });
                
                $a.text(visible_text);
                $td.append($a);
                $tr.append($td);

                /*
                $td = $('<td></td>');
                $a = $('<a></a>').attr({
                    "href" : "javascript: return false;",
                    "title" : tooltip,
                });
                $a.text("[x]");
                var item_id = data[i]['id']
                $a.click(function(){
                    source_id = entity_id;
                    source_label = entity_label;
                    target_id = item_id;
                    target_label = label;
                    url = "delete_link?source_id=" + source_id + "&source_label=" + source_label;
                    url += "&target_id=" + target_id + "&target_label=" + target_label;
                    alert("DELETE: " + url);
                    
                    $.get(url, function(data){
                        window.location.reload();
                    })
                    
                });
                $td.append($a);
                $tr.append($td);
                */
                $('#'+target_div_id).append($tr);
            }
        }
        else{
            $tr = $('<tr></tr>');
            $td = $('<td></td>');
            $td.text("There are no " + label.toLowerCase() + "s connected to this entity.");
            $tr.append($td);

            $('#'+target_div_id).append($tr);
        }
    });
}



function getrequest(name){
    if(name=(new RegExp('[?&]'+encodeURIComponent(name)+'=([^&]*)')).exec(location.search))
    var param = decodeURIComponent(name[1]);
    
    if(!param){
        param = "";
    }
    return param;
}


function link_file(){
    const window_features = "left=100,top=100,width=500,height=600";
    if(entity_id != ""){
        window.open("file_uploader?entity_id="+entity_id+"&entity_label="+entity_label, "File Uploader", window_features);
    }
    
}

function link_media(){
    const window_features = "left=100,top=100,width=500,height=600";
    if(entity_id != ""){
        window.open("media_linker?entity_id="+entity_id+"&entity_label="+entity_label, "Media Linker", window_features);
    }
    
}

function link_country(link_name){
    const window_features = "left=100,top=100,width=500,height=600";
    
    if(entity_id != ""){
        window.open("country_linker?entity_id="+entity_id+"&entity_label=" + entity_label + "&link_name=" + link_name, "Country Linker", window_features);
    }
}

function link_animal(){
    if(entity_id != ""){
        document.location.href = "animal_linker?entity_id="+entity_id+"&entity_label="+entity_label;
    }
    
}

function link_plant(){
    if(entity_id != ""){
        document.location.href = "plant_linker?entity_id="+entity_id+"&entity_label="+entity_label;
    }
}

function link_object(){
    if(entity_id != ""){
        document.location.href = "object_linker?entity_id="+entity_id+"&entity_label="+entity_label;
    }
}


function get_languages(target_controls){
    $.getJSON('get_languages', function(data){
        // console.log($target_control);
        if(data){
            for(var k = 0; k<target_controls.length; k++){
                for(var i = 0; i<data.length; i++){
                    // console.log(data[i]['language_name']);
                    target_controls[k].append($("<option />").val(data[i]['language_name']).text(data[i]['language_name']));
                }
            }
        }
    });
}

function get_countries(target_controls){
    $.getJSON('get_countries', function(data){
        if(data){
            for(var k = 0; k<target_controls.length; k++){
                for(var i = 0; i<data.length; i++){
                    // console.log(data[i]['language_name']);
                    target_controls[k].append($("<option />").val(data[i]['country_name']).text(data[i]['country_name']));
                }
            }
        }
    });
}



function capitalize(phrase){
    temp = phrase.split("_");
    result = "";
    for(i = 0; i<temp.length; i++){
      temp[i] = temp[i][0].toUpperCase() + temp[i].substring(1);
      result += temp[i] + " ";
    }
    return result.trim();
  }

  function generate_api_link(target_control){
    alert(window.location.hostname);
    var link = "apinarrative?key=" + uuid4();
    $target = $('#' + target_control);
    if($target){
        $target.text(link);
    }
  }


  function uuid4() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'
    .replace(/[xy]/g, function (c) {
        const r = Math.random() * 16 | 0, 
            v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

function check_loggedin_user(){
    console.log("Called");
    $.getJSON('get_loggedin_user_info', function(data){
        if(data){
            if(object_type(data) == "String"){
                data = JSON.parse(data);
            }
            
            // console.log(data['user_info']);
            console.log(data);
            if(data.hasOwnProperty('user_info')){
                user_data = data['user_info'];
                if(user_data){
                    $('.menu-loggedin').css({
                        "visibility" : "visible"
                    });
                    $('.menu-loggedout').css({
                        "visibility" : "hidden"
                    });   
                }
            }
            else{
                $('.menu-loggedin').css({
                    "visibility" : "hidden"
                });
                $('.menu-loggedout').css({
                    "visibility" : "visible"
                });
            }
            
        }
    });
}


function object_type(object) {
    var stringConstructor = "test".constructor;
    var arrayConstructor = [].constructor;
    var objectConstructor = ({}).constructor;

    if (object === null) {
        return "null";
    }
    else if (object === undefined) {
        return "undefined";
    }
    else if (object.constructor === stringConstructor) {
        return "String";
    }
    else if (object.constructor === arrayConstructor) {
        return "Array";
    }
    else if (object.constructor === objectConstructor) {
        return "Object";
    }
    {
        return "don't know";
    }
}