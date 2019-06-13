
//'id'0, 'answer'1, 'answer_date'2, 'praisenum'3, 'replier_id'4, 'user.id_num'5, 'user.username'6
// 答案的字段匹配数组
var answer_match_array = ['id','answer','answer_date','praisenum','replier_id','replier_id_num','replier_name'];
var answerTemplate1 = '<div class="answer" data-ansid="{id}" data-reprid="{replier_id}">\
<div class="replier">\
<div class="name">\
<a href="#">{replier_id_num}&nbsp;{replier_name}</a>\
<span class="slogen">{answer_date}</span>\
</div>\
</div>\
<div class="answerboard">{answer}</div>\
<div class="qfooter">\
<a href="javascript:void(0)" class="praise" onclick="PraiseAnswer(this)" status="0"><span>{praisenum}</span>&nbsp<span class="glyphicon glyphicon-thumbs-up"></span></a>\
<a href="javascript:void(0)" class="replynum" onclick="Collect(this)">收藏</a>\
<a href="javascript:void(0)" class="replynum" onclick="DeleteAnswer(this)">删除</a>\
</div>\
</div>';

var answerTemplate2 = '<div class="answer" data-ansid="{id}" data-reprid="{replier_id}">\
<div class="replier">\
<div class="name">\
<a href="#">{replier_id_num}&nbsp;{replier_name}</a>\
<span class="slogen">{answer_date}</span>\
</div>\
</div>\
<div class="answerboard">{answer}</div>\
<div class="qfooter">\
<a href="javascript:void(0)" class="praise" onclick="PraiseAnswer(this)" status="0"><span>{praisenum}</span>&nbsp;<span class="glyphicon glyphicon-thumbs-up"></span></a>\
<a href="javascript:void(0)" class="replynum" onclick="Collect(this)">收藏</a>\
</div>\
</div>';

// 'qus.id' 0, 'ques' 1, 'update_date' 2, 'tag' 3, 'asker_id' 4, 'praisenum' 5, 'imgurl' 6, user.username 7, user.id 8, answernum 9
var question_match_array = ['id', 'ques', 'update_date', 'tag', 'asker_id', 'praisenum','description','username','answernum'];
var questionTemplate1 = '<div class="Card">\
<div class="topic">\
<span>来自语言:<a href="#">{tag}</a></span>\
</div>\
<div class="userinfo">\
<div class="name">\
<a href="#">由&nbsp;{username}&nbsp;</a>\
<span>提问于&nbsp;{update_date}</span>\
</div>\
</div>\
<div class="clearfix"></div>\
<div class="question" data-qusid="{id}">\
<div class="board">\
<div class="item">\
<div class="problem" style="margin-bottom:10px">\
<p>{ques}</p>\
</div>\
<div class="attach">\
{description}\
</div>\
<div class="qfooter">\
<a href="javascript:void(0)" class="praise" onclick="PraiseQuestion(this)" status="0"><span>{praisenum}</span>&nbsp<span class="glyphicon glyphicon-thumbs-up"></span></a>\
<a href="javascript:void(0)" class="replynum" onclick="ShowOrHideAnswer(this)" status="0" data-origintext="" loaded="0">&nbsp共{answernum}条回答&nbsp</a>\
<a href="/wenda/question/answer/{id}" class="replynum">我要回答</a>\
<a href="javascript:void(0)" class="replynum" onclick="DeleteCard(this)">删除</a>\
</div>\
</div>\
<div class="answeritem hideoff" >\
</div>\
</div>\
</div>\
</div>';

var questionTemplate2 = '<div class="Card">\
<div class="topic">\
<span>来自语言:<a href="#">{tag}</a></span>\
</div>\
<div class="userinfo">\
<div class="name">\
<a href="#">由&nbsp;{username}&nbsp;</a>\
<span>提问于&nbsp;{update_date}</span>\
</div>\
</div>\
<div class="clearfix"></div>\
<div class="question" data-qusid="{id}">\
<div class="board">\
<div class="item">\
<div class="problem" style="margin-bottom:10px">\
<p>{ques}</p>\
</div>\
<div class="attach">\
{description}\
</div>\
<div class="qfooter">\
<a href="javascript:void(0)" class="praise" onclick="PraiseQuestion(this)" status="0"><span>{praisenum}</span>&nbsp<span class="glyphicon glyphicon-thumbs-up"></span></a>\
<a href="javascript:void(0)" class="replynum" onclick="ShowOrHideAnswer(this)" status="0" data-origintext="" loaded="0">&nbsp共{answernum}条回答&nbsp</a>\
</div>\
</div>\
<div class="answeritem hideoff" >\
</div>\
</div>\
</div>\
</div>';

// 接受两个参数 1、格式化的字符串，2、匹配字段数组，3、需要填入的数据数组
function StringFormat(str, match_array, data) {
    if (arguments.length < 2)
        return null;
    for (var i = 0; i < match_array.length; i++) {
        var key = match_array[i];
        var re = new RegExp('\\{' + key + '\\}', 'gm');
        str = str.replace(re, data[key]);
    }
    return str;
}

function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i].trim();
        if (c.indexOf(name) == 0) return c.substring(name.length, c.length);
    }
    return "";
}

function formateDate(date) {
    var y = date.getFullYear();
    var m = date.getMonth() + 1;
    var d = date.getDate();
    m = m > 9 ? m : '0' + m;
    d = d > 9 ? d : '0' + d;
    return y + '-' + m + '-' + d;
}

// answerTemplate:答案模板 data：需要填入的答案数据 answeritem：加入答案的父级元素 collectId：用户已经收藏的答案
function appendAnswer(answerTemplate,data,answeritem,collectId){
    for(var i=0;i<data.length;i++){
        answer = StringFormat(answerTemplate,answer_match_array, data[i]);
        if(!$.isEmptyObject(collectId) && collectId.indexOf(data[i]['id'])!=-1){
            answer = answer.replace("收藏", "取消收藏");
        }
        answer = $(answer);
        var img = answer.find("div.answerboard img");
        if(img.length>0){
            $(img[0]).click(function(){
                ZoomBig(this);
            })
        }-
        answeritem.append(answer);
    }
}



// 返回的response是一个字典 {'answer':answer, 'collectId':collectId}，
// 每个答案数组包含以下字段：'id', 'answer', 'answer_date', 'praisenum', 'replier_id', 'user.id_num', 'user.username'

// 0:请求参数为空 1:查询出错
function LoadAnswer(qusid, node, answeritem) {
    $.ajax({
        url: '/wenda/load_answer/',
        data: { qusid: qusid },
        type: "GET",
        dataType: "json",
        success: function (response) {
            // response = {answer:{'id':,'answer':....},collectId:{question_id:question_id}}
            if (typeof response == "object") {
                // console.log(response);
                var data = response['answer'];
                var collectId = response['collectId'];
                var recommend = response['recommend'];
                var answer;
                var answerTemplate;
                var role = getCookie("role");
                if(role == 'a'){
                    answerTemplate  = answerTemplate1;
                }else{
                    answerTemplate = answerTemplate2;
                }

                appendAnswer(answerTemplate,recommend,answeritem,collectId);
                appendAnswer(answerTemplate,data,answeritem,collectId);

                $(node).attr("loaded", "1");
            } else if (response == "0") {
                alert("参数为空！");
            } else if (response == "1") {
                alert("加载答案出错，请稍后重试!");
            }
        },
    });
}

function ShowOrHideAnswer(node) {
    var status = $(node).attr("status");
    var board = $(node).parents().filter(".board")[0];
    var answeritem = $(board).find(".answeritem");
    if (status == "0") {
        var origintext = $(node).attr("data-origintext");
        if (origintext == "") {
            $(node).attr("data-origintext", $(node).html());
        }
        var loaded = $(node).attr("loaded");
        if (loaded == "0") {
            var question = $(node).parents().filter(".question")[0];
            var qusid = $(question).attr("data-qusid");
            // console.log("qusid:"+qusid);
            LoadAnswer(qusid, node, answeritem);
        }
        answeritem.fadeIn();
        $(node).html("收起答案");
        $(node).attr("status", "1");
    } else if (status == "1") {
        answeritem.fadeOut();
        $(node).html($(node).attr("data-origintext"));
        $(node).attr("status", "0");
    }
}



// {'id', 'ques', 'update_date', 'tag', 'asker_id', 'praisenum','description','username','answernum'}
// 'qus.id' 0, 'ques' 1, 'update_date' 2, 'tag' 3, 'asker_id' 4, 'praisenum' 5, 'imgurl' 6, user.username 7, user.id 8, answernum 9
function LoadQuestion(_url) {
    $.ajax({
        type:"GET",
        url:_url,
        beforeSend:function(xhr){
            $("#loadBar").removeClass("hideoff");
            $("#loadquesStatus").attr("value","0");
        },
        success:function(data) {
            var list = $("#list");
            var card;
            var role = getCookie("role");
            var questionTemplate;
            if(role == 'a'){
                questionTemplate = questionTemplate1;
            }else{
                questionTemplate = questionTemplate2;
            }
            for (var i = 0; i < data.length ;i++){
                if(data[i]['description'] == null){
                    data[i]['description'] = "";
                }
                card = $(StringFormat(questionTemplate, question_match_array,data[i]));
                var img = card.find("div.attach img");
                if(img.length > 0){
                   $(img[0]).click(function(){
                       ZoomBig(this);
                   })
                }

    
                
                list.append(card);
            }

        },
        complete:function(xhr){
            $("#loadBar").addClass("hideoff");
            $("#loadquesStatus").attr("value","1");
        },



    })
}




// ******************************
function Praise(node, id, status, praiseObj) {
    $.ajax({
        type: "GET",
        url: "/wenda/praise_or_not/",
        data: { id: id, status: status, praiseObj: praiseObj },
        success: function (response) {
            if (response == "1") {
                if (status == "0") {
                    var praisenum = parseInt($(node).children("span:first").text()) + 1;
                    $(node).children("span:first").text(praisenum);
                    $(node).children("span:last").attr("class", "glyphicon glyphicon-thumbs-down");
                    $(node).attr("status", "1");
                } else {
                    var praisenum = parseInt($(node).children("span:first").text()) - 1;
                    $(node).children("span:first").text(praisenum);
                    $(node).children("span:last").attr("class", "glyphicon glyphicon-thumbs-up");
                    $(node).attr("status", "0");
                }
            } else {
                if (status == "0") {
                    alert("点赞失败,请稍后再试");
                } else {
                    alert("取消点赞失败,请稍后再试");
                }
            }
        }
    });
}

//  praiseObj 0代表问题 1代表答案点赞 2代表评论点赞 3代表对评论中对话的点赞
// 目前关闭评论和评论中的对话所以只有 点赞问题和点赞答案
function PraiseQuestion(node) {
    var question = $(node).parents().filter(".question")[0];
    var qusid = $(question).attr('data-qusid');
    var status = $(node).attr("status");
    Praise(node, qusid, status, 0);
}

function PraiseAnswer(node) {
    var answer = $(node).parents().filter(".answer")[0];
    var ansid = $(answer).attr('data-ansid');
    var status = $(node).attr("status");
    Praise(node, ansid, status, 1);
}


function DeleteObj(deletenode, objid, url) {
    $.ajax({
        type: "GET",
        url: url,
        data: { id: objid },
        success: function (response) {
            if (response == "1") {
                deletenode.remove();
            } else if (response == "2") {
                alert("删除失败请稍后再试！");
            } else if (response == "2") {
                alert("参数为空");
            }
        }
    })
}


function sendCollectReq(qid,aid,status){
    $.ajax({
        type: "GET",
        url: "/wenda/collect_or_not/",
        data: { qid: qid, aid: aid, status: status },
        success: function (response) {
            if (response == "1") {
                if (status == "0") {
                    $(node).text("取消收藏");
                } else {
                    $(node).text("收藏");
                }
            } else {
                alert("操作失败，请稍后再试！");
            }
        }
    })
}

function Collect(node) {
    var answer = $(node).closest(".answer");
    var qus = $(node).closest(".question");
    var qid = qus.attr("data-qusid");
    var aid = answer.attr("data-ansid");
    var status = ($(node).text() == "收藏") ? "0" : "1";
    sendCollectReq(qid,aid,status)
}


// 遮罩显示大图
function ZoomBig(self){
    var bigimg = $("#bigimg");
    bigimg.css({
            height: $(self).height() * 1.5,
            width: $(self).width() * 1.5
        });
    RotateCurrent = 0;
    bigimg[0].style.transform = 'rotate('+RotateCurrent+'deg)';
    $("#mask").fadeIn();
    bigimg.attr('src',$(self).attr("src")).fadeIn();

    $("#bigimg").on('mousewheel DOMMouseScroll', scrollFn);
}

// 鼠标滚动监听函数
function scrollFn(e) {
    e.preventDefault();
    var wheel = e.originalEvent.wheelDelta || -e.originalEvent.detail;
    var delta = Math.max(-1, Math.min(1, wheel) );
    if(delta<0){//向下滚动
        // console.log('down');
        downfun();
    }else{//向上滚动
        upfun();
        // console.log('up');
    }
} 

// 缩小图片
function downfun() {
    if ($("#bigimg").innerWidth() < 100) {
        alert("不能再缩小了哦");
        return
    }
    if ($("#bigimg").innerHeight() < 100) {
        alert("不能再缩小了哦！");
        return
    }
    var ratio = $("#bigimg")[0].naturalWidth / $("#bigimg")[0].naturalHeight;
    var zoomHeight = $("#bigimg").height() / 1.03;
    var zoomWidth = zoomHeight * ratio;
    // console.log("small:"+zoomHeight+" "+zoomWidth)
    $("#bigimg").css({
        height: zoomHeight + "px",
        width: zoomWidth + "px"
    })
}

// 放大图片
function upfun() {
    if ($("#bigimg").innerWidth() > $("body").width() - 20) {
        alert("不能再放大了");
        return
    }
    if ($("#bigimg").innerHeight() > $("body").height() - 50) {
        alert("不能再放大");
        return
    }
    var ratio = $("#bigimg")[0].naturalWidth / $("#bigimg")[0].naturalHeight;
    var zoomHeight = $("#bigimg").height() * 1.1;
    var zoomWidth = zoomHeight * ratio;
    // console.log("big:"+zoomHeight+" "+zoomWidth)
    $("#bigimg").css({
        height: zoomHeight + "px",
        width: zoomWidth + "px"
    })
}

// 大图隐去
function ZoomOut(){
    $("#bigimg").fadeOut();
    $("#mask").fadeOut(); 
}

// 图片旋转
function ImgRotate(self){
    RotateCurrent = (RotateCurrent + 90) % 360;
    self.style.transform = 'rotate('+RotateCurrent+'deg)';
}