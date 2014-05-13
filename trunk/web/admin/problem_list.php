<?php require("admin-header.php");

        if(isset($OJ_LANG)){
                require_once("../lang/$OJ_LANG.php");
        }


require_once("../include/set_get_key.php");
if (!(isset($_SESSION['administrator'])
                ||isset($_SESSION['contest_creator'])
                ||isset($_SESSION['problem_editor'])
                )){
        echo "<a href='../loginpage.php'>Please Login First!</a>";
        exit(1);
}
$keyword=$_GET['keyword'];
$keyword=mysql_real_escape_string($keyword);
$sql="SELECT max(`problem_id`) as upid FROM `problem`";
$page_cnt=50;
$result=mysql_query($sql);
echo mysql_error();
$row=mysql_fetch_object($result);
$cnt=intval($row->upid)-1000;
$cnt=intval($cnt/$page_cnt)+(($cnt%$page_cnt)>0?1:0);
if (isset($_GET['page'])){
        $page=intval($_GET['page']);
}else $page=$cnt;
$pstart=1000+$page_cnt*intval($page-1);
$pend=$pstart+$page_cnt;

echo "<title>Problem List</title>";
echo "<center><h2>Problem List</h2></center>";

for ($i=1;$i<=$cnt;$i++){
        if ($i>1) echo '&nbsp;';
        if ($i==$page) echo "<span class=red>$i</span>";
        else echo "<a href='problem_list.php?page=".$i."'>".$i."</a>";
}

$sql="select `problem_id`,`title`,`in_date`,`accepted`,`defunct` FROM `problem` where problem_id>=$pstart and problem_id<=$pend order by `problem_id` desc";
//echo $sql;
if($keyword) $sql="select `problem_id`,`title`,`in_date`,`accepted`,`defunct` FROM `problem` where title like '%$keyword%' or source like '%$keyword%'";
$result=mysql_query($sql) or die(mysql_error());
?>
<form action=problem_list.php><input name=keyword><input type=submit value="<?php echo $MSG_SEARCH?>" ></form>

<?php
echo "<center><table class='table table-striped' width=90% border=1>";
echo "<form method=post action=contest_add.php>";
echo "<tr><td colspan=8><input title='在下面的列表里选择题目' type=submit name='problem2contest' value='使用这些题目创建作业'>";
echo "<tr><td>题号<td>标题<td>日期<td>已做对";
if(isset($_SESSION['administrator'])||isset($_SESSION['problem_editor'])){
        if(isset($_SESSION['administrator']))   echo "<td>状态<td>Delete";
        echo "<td>Edit<td>TestData</tr>";
}
for (;$row=mysql_fetch_object($result);){
        echo "<tr>";
        echo "<td>".$row->problem_id;
        echo "<input type=checkbox name='pid[]' value='$row->problem_id'>";
        echo "<td><a href='../problem.php?id=$row->problem_id'>".$row->title."</a>";
        echo "<td>".$row->in_date;
        echo "<td>".$row->accepted;
        if(isset($_SESSION['administrator'])||isset($_SESSION['problem_editor'])){
                if(isset($_SESSION['administrator'])){
                        echo "<td><a href=problem_df_change.php?id=$row->problem_id&getkey=".$_SESSION['getkey'].">"
                        .($row->defunct=="N"?"<span titlc='click to reserve it' class=green>可用</span>":"<span class=red title='click to be available'>已停用</span>")."</a><td>";
                        if($OJ_SAE||function_exists("system")){
                              ?>
                              <a href=# onclick='javascript:if(confirm("Delete?")) location.href="problem_del.php?id=<?php echo $row->problem_id?>&getkey=<?php echo $_SESSION['getkey']?>";'>
                              删除</a>
                              <?php
                        }
                }
                if(isset($_SESSION['administrator'])||isset($_SESSION["p".$row->problem_id])){
                        echo "<td><a href=problem_edit.php?id=$row->problem_id&getkey=".$_SESSION['getkey'].">编辑</a>";
                        echo "<td><a href=quixplorer/index.php?action=list&dir=$row->problem_id&order=name&srt=yes>管理测试数据</a>";
                }
        }
        echo "</tr>";
}
echo "<tr><td colspan=8><input type=submit name='problem2contest' value='CheckToNewContest'>";
echo "</tr></form>";
echo "</table></center>";
require("../oj-footer.php");
?>
