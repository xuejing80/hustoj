/*
* 这个js文件中是对教师课程主页分组的处理
*/


var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
var chatsock = new WebSocket(ws_scheme + '://' + window.location.host  + window.location.pathname);

var groupsVue = new Map();
var nowid; // 用来记录消息的id，;防止中间消息没有收到

function addGroup(groupid, leader, members, problem) {
    var source = "\
    <div class='container'>\
            <div class='group' id='group-groupid'>\
                <div class='leader'>\
                    <span>{{ leader }}</span>\
                </div>\
                <div class='line'></div>\
                <div class='members'>\
                    <div v-if='members.length == 0'>\
                        <span>暂无成员</span>\
                    </div>\
                    <div v-else>\
                        <ol>\
                            <li v-for='member in members'>\
                                {{ member }} \
                            </li>\
                        </ol>\
                    </div>\
                </div>\
                <div class='select-problem'>\
                    <div v-if='problem != \"\"'>\
                        <span>选择的题目：{{ problem }}</span>\
                    </div>\
                    <div v-else>\
                        <span>还没有选择题目</span>\
                    </div>\
                </div>\
                <div v-if='problem != \"\"'>\
                    <div class='option'>\
                        <button v-on:click='readCode'>查看提交情况</button>\
                    </div>\
                </div>\
            </div>\
        </div>";
    source = source.replace("groupid", groupid);
    $('#add_problem_student').after(source);
    if (groupsVue.has(groupid))
    {
        alert("已经有了小组: " + groupid);
        throw "小组重复";
    }
    groupsVue.set(groupid, new Vue({
        el: '#group-' + groupid,
        data: {
            leader: leader + "的小组",
            members: members,
            problem: problem,
        },
        methods: {
            readCode: function() {
                var url = "/code_week/teacher-read-code-" + $("#course_id").text() + "-" + groupid + "/";
                window.open(url);
            }
        }
    }));
}

function handleFirstMsg(data) { // 用于处理以打开页面就获得的数据
    name = data.name;
    max = data.max;
    nowid = data.id;
    groups = data.groups;
    for (var i = 0; i < groups.length; ++i)
    {
        var problem = '';
        if (groups[i]["problem"])
        {
            problem = groups[i]["problem"];
        }
        addGroup(groups[i]["groupid"], groups[i]["leader"], groups[i]["members"], problem);
    }
}

function handleMessage(message) { // 用于处理websocket收到的消息
    var data = JSON.parse(message.data);
    if (data['msg'])  // 操作的返回消息
    {
        if (data['msg'] == 'success')
            alert("成功操作");
        else
            alert(data['info']);
        return;
    }
    if (data['operationId'] != nowid + 1) // 如果没有递增，中间丢失
    {
        retryData(data['operationId']);
    }
    else
    {
        nowid = data['operationId'];
    }
    if (data['action'] == 'c')  // 收到消息新建一个组
    {
        addGroup(data['groupId'], data['leader'], new Array(), "");
        // 调用addGroup会设置globalgroupid
    }
    else if (data['action'] == 'j') // 收到消息有同学加入分组
    {
        groupsVue.get(data['groupId']).members.push(data['student']);
    }
    else if (data['action'] == 'd') // 收到消息删除分组
    {
        var groupid = '#group-' + data['groupId'];
        $(groupid).remove();
        groupsVue.delete(data['groupId'])
    }
    else if (data['action'] == 'r') // 收到消息删除
    {
        var groupid = data['groupId'];
        var ms = groupsVue.get(groupid).members;
        var i = 0;
        for (; i < ms.length; ++i)
        {
            if (ms[i] == data['member'])
            {
                break;
            }
        }
        if (i < ms.length)
        {
            ms.splice(i, 1);
        }
    }
    else if (data['action'] == 'choose') // 收到消息有小组选择了题目
    {
        var groupid = data['groupId'];
        groupsVue.get(groupid).problem = data['title'];
    }
}