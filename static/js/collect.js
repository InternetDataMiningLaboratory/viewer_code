function collect(cSpan, collected, data_id){
    $.post(
        "/collection",
        {
            "_xsrf": getCookie("_xsrf"),
            "collected": collected,
            "data_id": data_id,
        },
        function(data){
            if(data=="success"){
                if(collected){
                    collectedcSpan(cSpan);
                }
                else{
                    uncollectedcSpan(cSpan);
                }
            }
            else{
                alerting(data, "danger");
            }
        }
    );
}
function collectedcSpan(cSpan){
    cSpan.removeClass("collected glyphicon-heart");
    cSpan.addClass("uncollected glyphicon-heart-empty");
}
function uncollectedcSpan(cSpan){
    cSpan.removeClass("uncollected glyphicon-heart-empty");
    cSpan.addClass("collected glyphicon-heart");
}
