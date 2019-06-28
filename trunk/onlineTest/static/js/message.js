var messageAnswerTemplate = '<div class="answer" data-ansid="{id}" data-reprid="{replier_id}">\
<div class="replier">\
<div class="name">\
<a href="#">{replier_id_num}&nbsp;{replier_name}</a>\
<span class="slogen">{answer_date}</span>\
</div>\
</div>\
<div class="answerboard">{answer}</div>\
<div class="qfooter">\
<a href="javascript:void(0)" class="praise" onclick="PraiseAnswer(this)" status="0"><span>{praisenum}</span>&nbsp;<span class="glyphicon glyphicon-thumbs-up"></span></a>\
</div>\
</div>';

    function readMessage(node){
        var _mid = $(node).attr('data-mid');
        // console.log(mid);
        $.ajax({
            type:'GET',
            data:{mid:_mid},
            url:"/message/read_message",
            success:function(response){
                if(response== '1'){
                    $(node).css('display','none');
                }else{
                    alert("点击已读出错，请稍后再试！");
                }
            },
        })

    }

    function loadMessage(node){
        $.ajax({
            type:'get',
            url:"/message/load_message/",
            success:function(response){
                var loadMore = $("#loadMore");
                var sibling = loadMore.prev();
                var m;
                var temp = '<div class="item"><div class="question">';
                for(var i=0;i<response.length;i++){
                    m = response[i];
                    var template = temp;
                    if(m['messagetype'] == 0){
                        template += '<span>系统提示您:' + m['message'] +'</span>';
                    }else if(m['messagetype'] == 1){
                        template += '<a href="/wenda/question/answer/' + m.objId+ '">' + m.sname + "邀请您回答问题：" + m.message +'</a>';
                    }else if(m['messagetype'] == 2){
                        template += '<span>' + m.message + '</span>';
                    }else{
                        var t;
                        if(m['messagetype'] == 3){
                            t = '回答了您的问题：';
                        }else if(m['messagetype'] == 4){
                            t = '评论了您的问题：';
                        }else if(m['messagetype'] == 5){
                            t = '更新了答案：';
                        }
                        template += '<a href="javascript:void(0)" data-ansid = "' + m.objId+ '" onclick="showAnswer(this)" status="0" load="0">' + m.sname + t + m.message +'</a>';
                    }
                    template +=  '<span style="font-size:1em">&nbsp;发布时间:'+ m.date + '</span>';
        
                    template += '<div class="answeritem hideoff"></div></div></div>';
                    sibling.after($(template));
                }
                loadMore.css('display','none');
            }

        })
    }

    function showAnswer(node){
        var status = $(node).attr("status");
        var board = $(node).parents().filter(".item")[0];
        var answeritem = $(board).find(".answeritem");
        var tip = $(board).find(".tip");
        var isread = $(node).attr("isread");
        if(isread == "0"){
            readMessage(tip);
            $(node).attr("isread","1");
        }
        // console.log(tip.attr("data-mid"));
        // console.log(board);
        if($(node).attr("load") == "0"){
            loadMessageAnswer($(node).attr("data-ansid"),answeritem);
            $(node).attr("load","1");
        }

        if(status == "0"){
            answeritem.fadeIn();
            $(node).attr("status","1");
        }else{
            answeritem.fadeOut();
            $(node).attr("status","0");
        }
    }

    function loadMessageAnswer(ansid,answeritem){
        $.ajax({
            data:{ansid:ansid},
            type:'GET',
            url:"/wenda/load_answer_message/",
            success:function(response){
                if(typeof response == "object"){
                    answer = StringFormat(messageAnswerTemplate,answer_match_array, response);
                    // console.log(answer);
                    answer = $(answer);
                    var img = answer.find("div.answerboard img");
                    if(img.length>0){
                        $(img[0]).click(function(){
                            ZoomBig(this);
                        })
                    }
                    $(answeritem).append(answer);
                }else{
                    alert("加载出错！");
                }
            }
        })
    }