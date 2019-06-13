
//'id'0, 'answer'1, 'answer_date'2, 'praisenum'3, 'replier_id'4, 'user.id_num'5, 'user.username'6
// 答案的字段匹配数组
var answer_match_array = ['id','answer','answer_date','praisenum','replier_id','replier_id_num','replier_name'];
var answerTemplate = '<div class="answer" data-ansid="{id}" data-reprid="{replier_id}">\
<div class="replier">\
<div class="name">\
<a href="#">{replier_id_num}&nbsp{replier_name}</a>\
<span class="slogen">{answer_date}</span>\
</div>\
</div>\
<div class="answerboard">{answer}</div>\
<div class="footer">\
<a href="javascript:void(0)" class="praise" onclick="PraiseAnswer(this)" status="0"><span>{praisenum}</span>&nbsp<span class="glyphicon glyphicon-thumbs-up"></span></a>\
<a href="javascript:void(0)" class="replynum" onclick="Collect(this)">收藏</a>\
</div>\
<div class="commentboard hideoff">\
<div class="commentheader">\
<span style="color:black;margin:0px;font-size:1.1px">\
<strong>{7}&nbsp条评论</strong>\
</span>\
</div>\
<div class="commentinput">\
<div ansid={id}>\
<input type="text" name="comment" required="required" placeholder="快写下你的评论吧...">\
<button onclick="CommitComment(this)">发送</button>\
</div>\
</div>\
</div>\
</div>';

// c.id 0, c.comment 1, c.comment_date 2, c.praisenum 3, c.commenter.username 4, c.commenter.id 5
var commentTemplate = '\
<div class="commentitem">\
<div class="commenter" objid="{0}" type="0">\
<a href="#">{4}</a>\
&nbsp<span>{2}</span>\
{delete}\
</div>\
<div class="commentcontent">{1}</div>\
<div class="commentfooter">\
<a href="javascript:void(0)" class="praise" onclick="PraiseComment(this)" status="0"><span>{3}</span>&nbsp\
<span class="glyphicon glyphicon-thumbs-up"></span>\
</a>\
<a href="javascript:void(0)" onclick="ShowReplyComment(this)">\
<span class="glyphicon glyphicon-send"></span>&nbsp回复</a>\
</div>\
<div class="replycomment hideoff">\
<div comid="{0}" usrid={5}>\
<input type="text" required="required" placeholder=" 回复{4}">\
<button onclick="ReplyComment(this)">回复</button>\
<a href="javascript:void(0)" onclick="HideReplyComment(this)">取消</a>\
</div>\
</div>\
</div>';

// 'sender 0', 'sname 1', 'receiver 2', 'rname 3', 'comment 4', 'comment_date 5', 'praisenum 6' commentid 7 conversion.id 8
var conversationTemplate = '<div class="commentitem">\
<div class="commenter" objid="{8}" type="1">\
<a href="#">{1}&nbsp</a>回复&nbsp\
<a href="#">{3}&nbsp</a>\
&nbsp<span>{5}</span>\
{delete}\
</div>\
<div class="commentcontent">{4}</div>\
<div class="commentfooter">\
<a href="javascript:void(0)" class="praise" onclick="PraiseConver(this)" status="0" cid="{8}"><span>{6}</span>&nbsp\
<span class="glyphicon glyphicon-thumbs-up"></span>\
</a>\
<a href="javascript:void(0)" onclick="ShowReplyComment(this)">\
<span class="glyphicon glyphicon-send"></span>&nbsp回复</a>\
</div>\
<div class="replycomment hideoff">\
<div comid="{7}" usrid="{0}">\
<input type="text" required="required" placeholder=" 回复{1}">\
<button onclick="ReplyComment(this)">回复</button>\
<a href="javascript:void(0)" onclick="HideReplyComment(this)">取消</a>\
</div>\
</div>\
</div>';


// 'qus.id' 0, 'ques' 1, 'update_date' 2, 'tag' 3, 'asker_id' 4, 'praisenum' 5, 'imgurl' 6, user.username 7, user.id 8, answernum 9
var question_match_array = ['id', 'ques', 'update_date', 'tag', 'asker_id', 'praisenum','description','username','answernum'];
var questionTemplate = '<div class="Card">\
<div class="topic">\
<span>来自语言:\
<a href="#">{tag}</a>\
</span>\
<span style="float:right;">\
<!--<a href="javascript:void(0)" onclick="DeleteCard(this)">×&nbsp;</a>-->\
</span>\
</div>\
<div class="userinfo">\
<div class="name">\
<a href="#">{username}</a>\
<span>{update_date}</span>\
</div>\
</div>\
<div class="clearfix"></div>\
<div class="question" data-qusid="{id}">\
<div class="board">\
<div class="item">\
<div class="problem">\
<p>{ques}</p>\
<div class="attach">\
{description}</div>\
</div>\
<div class="footer">\
<a href="javascript:void(0)" class="praise" onclick="PraiseQuestion(this)" status="0"><span>{praisenum}</span>&nbsp\
<span class="glyphicon glyphicon-thumbs-up"></span>\
</a>\
<a href="javascript:void(0)" class="replynum" onclick="ShowOrHideAnswer(this)" status="0" data-origintext="" loaded="0">&nbsp\
<span class="glyphicon glyphicon-ok"></span>&nbsp共{answernum}条回答&nbsp\
</a>\
<a href="/wenda/question/answer/{id}" class="replynum">我要回答</a>\
</div>\
</div>\
<div class="answeritem hideoff">\
<hr>\
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
                var answer;
                if ($.isEmptyObject(collectId)) {
                    for (var i = 0; i < data.length; i++) {
                        answer = StringFormat(answerTemplate,answer_match_array, data[i]);
                        answeritem.append($(answer));
                    }
                } else {
                    for (var i = 0; i < data.length; i++) {
                        answer = StringFormat(answerTemplate, answer_match_array ,data[i]);
                        if (collectId[data[i]['id']] != undefined) {
                            answer = answer.replace("收藏", "取消收藏");
                            //console.log(collectId[data[i][0]]);
                        }
                        answeritem.append($(answer));
                    }
                }
                $(node).attr("loaded", "1");
            } else if (response == "0") {
                alert("参数为空！");
            } else if (response == "1") {
                alert("加载答案出错，请稍后重试!");
            }
        },
    });
}


// 删除问题的版块
function DeleteCard(node) {
    var card = $(node).parents().filter(".Card")[0];
    card.remove();
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


function LoadComment(ansid, node, commentheader) {
    $.ajax({
        type: "GET",
        url: '/onlineFaq/loadComment/',
        data: { ansid: ansid, },
        dataType: "json",
        success: function (data) {
            if (data.length > 0) {
                // c.id, c.comment, c.comment_date, c.praisenum, c.commenter.username, c.commenter.id, convser
                var comment, conver;
                var uid = getCookie("uid")
                var re = new RegExp('\\{' + 'delete' + '\\}', 'gm');
                var deletestr = '<a class="deletecomment" href="javascript:void(0)" onclick="DeleteComment(this)">×&nbsp;</a>';
                for (var i = data.length - 1; i >= 0; i--) {
                    comment = data[i].slice(0, 6);
                    conver = data[i][6];

                    var commentcell = $('<div class="commentcell"></div>')
                    var commentitem = StringFormat(commentTemplate, comment);

                    if (uid == comment[5]) {
                        commentitem = commentitem.replace(re, deletestr);
                    } else {
                        commentitem = commentitem.replace(re, "");
                    }

                    commentitem = $(commentitem);
                    commentcell.append(commentitem);
                    var conversation = $('<div class="conversation"></div>');
                    commentcell.append(conversation);
                    for (var j = 0; j < conver.length; j++) {
                        var converstr = StringFormat(conversationTemplate, conver[j]);
                        if (uid == conver[j][0]) {
                            converstr = converstr.replace(re, deletestr);
                        } else {
                            converstr = converstr.replace(re, "");
                        }
                        conversation.append($(converstr));
                    }
                    commentheader.after(commentcell);
                }
                $(node).attr("loaded", "1");
            } else if (data == "0") {
                alert("参数为空！");
            } else if (data == "1") {
                alert("查询出错，请稍后重试!");
            }
        }
    })
}


function ShowOrHideComment(node) {
    var answer = $(node).parents().filter(".answer")[0];
    var commentboard = $(answer).find(".commentboard");
    var status = $(node).attr("status");
    if (status == "0") {
        var loaded = $(node).attr("loaded");
        if (loaded == "0") {
            var ansid = $(answer).attr("data-ansid");
            var commentheader = commentboard.find(".commentheader");
            LoadComment(ansid, node, commentheader);
        }
        commentboard.fadeIn();
        $(node).attr("status", "1");
    } else if (status == "1") {
        commentboard.fadeOut();
        $(node).attr("status", "0");
    }
}

function ShowReplyComment(node) {
    var replycomment = $(node).parent().next();
    replycomment.fadeIn();
}

function HideReplyComment(node) {
    var replycomment = $(node).parents().filter(".replycomment")[0];
    $(replycomment).find("input").val("");
    $(replycomment).fadeOut();
}

// 对评论的回复
function ReplyComment(node) {
    var comid = $(node).parent().attr("comid");
    var receiver = $(node).parent().attr("usrid");;
    var comment = $(node).prev().val();
    var receiverName = $(node).prev().attr("placeholder").slice(3);
    $.ajax({
        type: "GET",
        url: '/onlineFaq/replyComment/',
        data: { comid: comid, comment: comment, receiver: receiver },
        success: function (response) {
            if (typeof response == 'object') {
                // response [conversation.id, commentid ,request.user.id]
                // 'sender 0', 'sname 1', 'receiver 2', 'rname 3', 'comment 4', 'comment_date 5', 'praisenum 6' commentid 7 conversion.id 8
                var data = Array(9);
                data[0] = response[2];
                data[1] = "我";
                data[2] = receiver;
                data[3] = receiverName;
                data[4] = comment;
                data[5] = formateDate(new Date());
                data[6] = 0;
                data[7] = response[1];
                data[8] = response[0];
                var conver = StringFormat(conversationTemplate, data);

                var re = new RegExp('\\{' + 'delete' + '\\}', 'gm');
                var deletestr = '<a class="deletecomment" href="javascript:void(0)" onclick="DeleteComment(this)">×&nbsp;</a>';
                conver = conver.replace(re, deletestr);

                var commentcell = $(node).parents().filter(".commentcell")[0];
                var conversation = $(commentcell).find(".conversation")[0];
                $(conversation).append($(conver));
                HideReplyComment(node);
            } else if (response == "0") {
                alert("参数为空");
            } else if (response == "2") {
                alert("回复失败，稍后重试");
            }
        }
    })
}

// 对问题的评论
function CommitComment(node) {
    var ansid = $(node).parent().attr("ansid");
    var input = $(node).prev();
    var comment = input.val();
    $.ajax({
        type: "GET",
        data: { ansid: ansid, comment: comment },
        url: '/onlineFaq/commitComment/',
        success: function (response) {
            if (typeof response == 'object') {
                // response [comment.id, request.user.id]
                // c.id 0, c.comment 1, c.comment_date 2, c.praisenum 3, c.commenter.username 4, c.commenter.id 5
                var data = Array(6);
                data[0] = response[0];
                data[1] = comment;
                data[2] = formateDate(new Date());
                data[3] = 0;
                data[4] = "我";
                data[5] = response[1];
                var comm = StringFormat(commentTemplate, data);

                var re = new RegExp('\\{' + 'delete' + '\\}', 'gm');
                var deletestr = '<a class="deletecomment" href="javascript:void(0)" onclick="DeleteComment(this)">×&nbsp;</a>';
                comm = comm.replace(re, deletestr);

                var commentboard = $(node).parent().parent().prev();
                commentboard.append($(comm));
                input.val("");
            } else if (response == "0") {
                alert("参数为空");
            } else if (response == "2") {
                alert("评论失败，稍后重试");
            }
        }
    })
}

// {'id', 'ques', 'update_date', 'tag', 'asker_id', 'praisenum','description','username','answernum'}
// 'qus.id' 0, 'ques' 1, 'update_date' 2, 'tag' 3, 'asker_id' 4, 'praisenum' 5, 'imgurl' 6, user.username 7, user.id 8, answernum 9
function LoadQuestion() {
    $.ajax({
        type:"GET",
        url:"/wenda/load_question/",
        success:function(data) {
            var list = $("#list");
            var card;
            for (var i = 0; i < data.length ;i++){
                if(data[i]['description'] == null){
                    data[i]['description'] = "";
                }else{
                    data[i]['description'] = "<span style='font-size:1em;margin-left: -15px'><b>问题补充：</b></span>" + data[i]['description'];
                }
                card = $(StringFormat(questionTemplate, data[i]));
                list.append(card);
            }
            // console.log(data);
        }
    })
}



var flag = 1;
window.onscroll = function () {
    var hh = document.body.scrollTop || document.documentElement.scrollTop;
    var clientHeight = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
    var H = document.documentElement.scrollHeight - clientHeight;
    if (H * 0.9 <= hh && flag) {
        flag = 0;
        LoadQuestion();
    }
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

function PraiseComment(node) {
    var comment = $(node).parent().next().children();
    var comid = comment.attr('comid');
    var status = $(node).attr("status");
    Praise(node, comid, status, 2);
}

// 对评论中对话的点赞
function PraiseConver(node) {
    var cid = $(node).attr("cid");
    var status = $(node).attr("status");
    Praise(node, cid, status, 3);
}
// ******************************

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


function DeleteComment(node) {
    // type 0:comment 1:conversation
    var type = $(node).parent().attr("type");
    var objid = $(node).parent().attr("objid");
    console.log(type);
    var url, deletenode;
    if (type == "0") {
        url = "/onlineFaq/delcomment/";
        deletenode = $(node).parent().parent().parent();
    } else if (type == "1") {
        url = "/onlineFaq/delconversation/";
        deletenode = $(node).parent().parent();
    }
    DeleteObj(deletenode, objid, url);
}

function Collect(node) {
    var answer = $(node).closest(".answer");
    var qus = $(node).closest(".question");
    var qid = qus.attr("data-qusid");
    var aid = answer.attr("data-ansid");
    var status = ($(node).text() == "收藏") ? "0" : "1";
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