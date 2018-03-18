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
var nowid; // 用来记录消息的id，防止中间消息没有收到
var max;   // 用来记录每组人数的最多数目
var groupsVue = new Map();

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
                    <div v-if='problem'>\
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
                    <button v-on:click='chooseP'>选题</button>\
                </div>\
                <div class='option'>\
                    <button v-on:click='dismissG'>解散</button>\
                </div>\
            </div>\
        </div>";
    if (leader == name)
        source = leadersource.replace("groupid", groupid);
    else
        source = source.replace("groupid", groupid);
    $('#leader').after(source);
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
function handleFirstMsg(data) { // 用于处理以打开页面就获得的数据
    name = data.name;
    max = data.max;
    nowid = data.id;
    groups = data.groups;
    if (max == 1) // 每个小组只有一个成员，这是不显示小组
    {
        // 只提供选择题目和提交代码按钮
    }
    else if (max > 1) {
        for (var i = 0; i < groups.length; ++i)
        {
            var problem = null
            try {
                problem = groups[i]["problem"];
            } catch (error) {
                
            }
            addGroup(groups[i]["groupid"], groups[i]["leader"], groups[i]["members"], problem);
        }
    }
    
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
                var message = {
                    action: "choose",
                    id: id,
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
        addGroup(data['groupId'], data['leader'], new Array());
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
        if (max > 1)
        {
            var groupid = data['groupId'];
            groupsVue.get(groupsVue).problem = data['problem'];
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