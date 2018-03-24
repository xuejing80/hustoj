/*
* 这个js文件中写的是学生课程主页分组的处理
* 1. 页面初始化时利用Ajax获取分组的数据，然后js解析json生成有关分组的前端显示
* 2. 对websocket的初始化，在这之后所有的有关分组的信息都会通过websocket传输
* 3. 对分组的点击操作的处理，例如成为组长，加入分组，解散分组
* 4. 对收到的消息进行处理，有对自己提交的操作的回应，也有广播的有关分组的消息
* 5. 处理消息的时候需要比较nowid和收到的消息id中间是否有缺少，如果有就主动获取缺少的
*/
var name;
var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
var chatsock = new WebSocket(ws_scheme + '://' + window.location.host  + window.location.pathname);
var nowid; // 用来记录消息的id，;防止中间消息没有收到
var max;   // 用来记录每组人数的最多数目
var groupsVue = new Map();
var globalgroupid;
// var chooseProblemVue;
// var reChooseProblemVue;
// var submitCodeVue;
function ifInGroup(leader, members, name) { //查看自己是否在该小组内
    if (leader == name)
        return true;
    for (var i = 0; i < members.length; ++i)
    {
        if (name == members[i])
        {
            return true;
        }
    }
    return false;
}
function addGroup(groupid, leader, members, problem){ // 测试jQuery插入dom  
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
                <div class='option'>\
                    <button v-on:click='joinG'>加入</button>\
                </div>\
            </div>\
        </div>";
    var leadersource = "\
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
                                {{ member }} <i class='fa fa-trash-o' v-on:click='removeM'></i>\
                            </li>\
                        </ol>\
                    </div>\
                </div>\
                <div class='select-problem'>\
                    <div v-if='problem'>\
                        <span>选择的题目：{{ problem }}</span>\
                    </div>\
                    <div v-else>\
                        <span>还没有选择题目</span>\
                    </div>\
                </div>\
                <div class='option'>\
                    <button v-on:click='chooseP'>\
                        <div v-if='problem'>\
                         重新选题\
                        </div>\
                        <div v-else>\
                         选题\
                        </div>\
                    </button>\
                </div>\
                <div class='option'>\
                    <button v-on:click='dismissG'>解散</button>\
                </div>\
            </div>\
        </div>";
    var ifIn = ifInGroup(leader, members, name);
    if (ifIn)
    {
        globalgroupid = groupid;
        $('#leader').remove();
        if (problem)
        {
            addProblemInfo(problem);
            if (leader == name) // 已经选择题目了,显示提交代码按钮，暂时只能组长提交代码
            {
                addSubmitButton(groupid);
            }
            else // 组员显示进入代码页面
            {
                addReadCodeButton(groupid);
            }
        }

    }
    if (leader == name)
        source = leadersource.replace("groupid", groupid);
    else
        source = source.replace("groupid", groupid);
    $('#groups').after(source);
    if (groupsVue.has(groupid))
    {
        alert("已经有了小组: " + groupid);
        throw "小组重复";
    }
    if (leader == name)
    {
        groupsVue.set(groupid, new Vue({
            el: '#group-' + groupid,
            data: {
                leader: leader + "的小组",
                members: members,
                problem: problem,
            },
            methods: {
                dismissG: function() {
                    dismissGroup();
                }, 
                removeM: function(event) {
                    // this.previousSibling;
                    if (event)
                    {
                        removeMember(event.target.previousSibling.textContent.trim());
                    }
                    else
                    {
                        alert("No event!");
                    }
                },
                chooseP: function() {
                    chooseProblem();
                }
            }
        }));
    }
    else
    {
        groupsVue.set(groupid, new Vue({
            el: '#group-' + groupid,
            data: {
                leader: leader + "的小组",
                members: members,
                problem: problem,
            },
            methods: {
                joinG: function() {
                    if (members.length > max)
                    {
                        alert("小组已满");
                        return;
                    }
                    else
                    {
                        joinGroup(groupid);
                    }
                }
            }
        }));
    }
}
function addSubmitButton(groupid) { // 用于增加组长提交代码按钮
    var submitCodeButton = '<button class="btn btn-success"\
    id="submitCode" onclick="location.href=\'/code_week/submit-code-' + getClassId() 
    + '/\'"> 提交代码</button>';
    $('#buttons').after(submitCodeButton);
}
function addReadCodeButton(groupid) { // 用于组员进入代码界面
    var submitCodeButton = '<button class="btn btn-success"\
    id="submitCode" onclick="location.href=\'/code_week/submit-code-' + getClassId() 
    + '/\'"> 进入代码界面</button>';
    $('#buttons').after(submitCodeButton);
}
function handleFirstMsg(data) { // 用于处理以打开页面就获得的数据
    name = data.name;
    max = data.max;
    nowid = data.id;
    groups = data.groups;
    if (max == 1) // 每个小组只有一个成员，这是不显示小组
    {
        // 只提供选择题目和提交代码按钮
        for (var i = 0; i < groups.length; ++i)
        {
            if (groups[i]["leader"] == name)
            {
                globalgroupid = groups[i]["groupid"];
                var problem = null;
                try {
                    problem = groups[i]["problem"];
                } catch (error) {

                }
                if (problem) // 已经选择了题目
                {
                    singleSelectedProblem(problem);
                }
                else
                {
                    singleNotSelectProblem();
                }
            }
        }
    }
    else if (max > 1) {
        // 添加成为组长按钮
        addLeaderButton();
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

}
function addLeaderButton() { // 添加成为组长按钮
    var leaderButton = '<button class="btn btn-success" id="leader" onclick="sendLeader()">成为组长</button>';
    $('#buttons').after(leaderButton);
}
function getClassId() { // 通过链接获取课程id
    var url = window.location.pathname;
    return url.substring(url.lastIndexOf('_')+1, url.length-1);
}
function addProblemInfo(problem) { // 添加题目信息
    var selectedProblem = '<p id="problemInfo">已经选择的题目: <a href="/code_week/download-' + getClassId()
    + '/" title="下载题目描述文件">' + problem + '</a></p>';
    $('#groupNumberLimit').after(selectedProblem);
}
function singleSelectedProblem(problem) {
    // 分组为一人的选过题目的
    // 将选择题目按钮变为重新选择题目
    // 显示已经选择的题目信息
    // 显示提交代码按钮
    $('#chooseProblem').remove();
    var reChooseProblemButton = '<button class="btn btn-success"\
    id="reChooseProblem" onclick="reChooseProblem()">\
    重新选择题目</button>';
    $('#buttons').after(reChooseProblemButton); 
    addProblemInfo(problem);
    var submitCodeButton = '<button class="btn btn-success"\
    id="submitCode" onclick="location.href=\'/code_week/submit-code-' + getClassId() 
    + '/\'"> 提交代码</button>';
    $('#reChooseProblem').after(submitCodeButton);
}
function singleNotSelectProblem() {
    // 分组为一个的还没有选过题目
    // 添加选择题目按钮
    var chooseProblemButton = '<button class="btn btn-success"\
    id="chooseProblem" onclick="chooseProblem()">\
    选择题目</button>';
    $('#buttons').after(chooseProblemButton);
}
// var b = document.getElementById("addGroup");
// b.onclick
function addG(){
    var groupid = 100;
    var leader = "B14040315 张柯";
    var members = new Array();
    members.push('测试');
    addGroup(groupid, leader, members);
}
function sendLeader(){ // 通过websocket发送成为组长的消息
    var message = {
        action: "c",
    };
    chatsock.send(JSON.stringify(message));
}
function joinGroup(groupid){  // 通过websocket发送加入分组的消息
    if (typeof(groupid) != "number") // 确保groupid是一个数字
    {
        throw "joinGroup中groupid不是一个数字";
    }
    var message = {
        action: "j",
        id: groupid,
    };
    chatsock.send(JSON.stringify(message));
}
function dismissGroup(){ // 通过websocket发送解散分组的消息
    var message = {
        action: "d",
    };
    chatsock.send(JSON.stringify(message));
}
function removeMember(memberName){
    var message = {
        action: "r",
        name: memberName,
    };
    chatsock.send(JSON.stringify(message));
}
function chooseProblem() {
    $.confirm({
        title: '选择题目',
        content: '请输入题目的序号，选取题目之后无法进行组员管理 <input class="form-control" id="problem_id" type="text" placeholder="输入题目序号"/>',
        confirmButton: '确认',
        cancelButton: '放弃',
        confirm: function () {
            id = parseInt($('#problem_id').val());
            if ($('#table').bootstrapTable("getData")[id-1])
            {
                var selectedProblemId = $('#table').bootstrapTable("getData")[id-1].pk;
                var message = {
                    action: "choose",
                    id: selectedProblemId,
                };
                chatsock.send(JSON.stringify(message));
                return true;
            }
            else
            {
                $.alert('输入的序号无效!');
                return false;
            }
        }
    });
}
function handleMessage(message) { // 用于处理websocket收到的消息
    console.log(message.data);
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
        if (data['student'] == name)
        {
            // 设置自己的globalgroupid
            globalgroupid = data['groupId'];
            // 移除成为组长按钮
            $('#leader').remove();
        }
    }
    else if (data['action'] == 'd') // 收到消息删除分组
    {
        var groupid = '#group-' + data['groupId'];
        $(groupid).remove();
        // 如果组长已经选题，移除组长的提交按钮和组员的进入代码界面按钮
        // 移除所有组员的题目信息
        // 将所有组员的组号设为undefined
        // 显示成为组长按钮
        toDGroup = groupsVue.get(data['groupId']);
        if (data['groupId'] == globalgroupid)
        {
            $("#submitCode").remove();
            $('#problemInfo').remove();
            globalgroupid = undefined;
            addLeaderButton();
        }
        // if (name == toDGroup.leader)
        // {
        //     globalgroupid = undefined;
        //     if (toDgroup.problem)
        //     {
        //         $("#submitCode").remove();
        //         $('#problemInfo').remove();
        //     }
        // }
        // else if (ifInGroup(toDGroup.leader, toDgroup.members, name))
        // {
        //     if (toDgroup.problem)
        //     {
        //         $('#problemInfo').remove();
        //     }
        //     globalgroupid = undefined;
        // }
        groupsVue.delete(data['groupId'])
    }
    else if (data['action'] == 'r') // 收到消息删除
    {
        var groupid = data['groupId'];
        var ms = groupsVue.get(groupid).members;
        var i = 0;
        // 如果是自己被移除
        // 如果已经选题，清除选题按钮并且移除进入代码界面按钮
        // 加上成为组长按钮
        // 将globalgroupid设为undefined
        if (name == data['member'])
        {
            globalgroupid = undefined;
            if (groupsVue.get(groupid).problem)
            {
                $('#problemInfo').remove();
                $('#submitCode').remove();
            }
            addLeaderButton();
        }
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
        if (max > 1)
        {
            var groupid = data['groupId'];
            groupsVue.get(groupid).problem = data['title'];
            if (groupid == globalgroupid)
            {
                addProblemInfo(data['title']);
                if (name == groupsVue.get(groupid).leader)
                {
                    addSubmitButton(groupid); 
                }
                else
                {
                    addReadCodeButton(groupid);
                }
            }
        }
        else if (max == 1)
        {
            var getGroupId = data['groupId'];
            if (getGroupId == globalgroupid)
            {
                singleSelectedProblem(data['title']);
            }
        }
    }
}
function retryData(id)  // 获取nowid到id中丢失的
{
    if (nowid + 1 == id) // 不需要重新获取
    {
        return;
    }
    else if (id < (nowid + 1)) // 有问题
    {
        throw "id对应不上";
    }
    else {
        alert("现在id是: " + nowid + " 收到的是: " + id);
    }
}
function getGroupId() // 获取组id
{
    return this.parentElement.id.split('-')[1];
}
function handleJoinClick() // 处理加入分组的点击请求
{
    var id = getGroupId();
    console.log(id);
    joinGroup(parseInt(id));
}
function handleDismissClick() // 处理解散分组请求
{
    dismissGroup();
}
function handleRemoveClick()  // 处理移除组员点击请求
{

}