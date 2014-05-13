<h2>正在做题的人</h2>
<?php
  require_once('./include/db_info.inc.php');
  if(!isset($_SESSION['user_id'])) return;
  $problem_id=intval($_GET['problem_id']);
  $user_id= $_SESSION['user_id'];  
  $user_mysql=mysql_real_escape_string($user_id);

  $sql="select 1 from solution where problem_id=$problem_id and user_id='$user_mysql' and result=4";
  $result=mysql_query($sql);
  if(!mysql_fetch_object($result)){
     $sql="update users set problem_id=$problem_id where user_id='$user_mysql'"; 
     mysql_query($sql); 
  }
  $sql="select user_id,nick from users where problem_id=$problem_id and user_id not in (select user_id from solution where problem_id=$problem_id and result=4)";
  $result=mysql_query($sql);

  for (;$row=mysql_fetch_object($result);){
//     echo "<a target=_blank title='$row->user_id' href='userinfo.php?user=$row->user_id'>$row->nick</a>";
     echo "<button title='挑战$row->user_id' class='btn' onclick=\"fire('$row->user_id',$problem_id);\" >$row->nick</button>";
  }
  $sql="select * from pk where `to`='$user_mysql' and status=0";  
  $result=mysql_query($sql);
  if($row=mysql_fetch_object($result)){
     ?>
     <script>if(confirm("<?php echo $row->from; ?>就<?php echo $row->problem_id?>题向你发出挑战,是否接受挑战?")) accept(<?php echo $row->id; ?>);else reject(<?php echo $row->id; ?>);</script>

    <?php
  }
  $sql="select * from pk where `from`='$user_mysql' and status=1 and problem_id=$problem_id";  
  $result=mysql_query($sql);
  if($row=mysql_fetch_object($result)){
    echo "$row->to 已经接受你的挑战，燃烧吧！俺的CPU！";
  }
  $sql="select id from pk where (`to`='$user_mysql' or `from`='$user_mysql' ) and status=1 and problem_id in (select problem_id from solution where result=4 and user_id='$user_mysql' )";  
  $result=mysql_query($sql);
//  echo $sql;
  if($row=mysql_fetch_object($result)){
    echo "有你参与的挑战结束了，<a href=# onclick=win($row->id);>去算账吧，看看到底谁赢了!</a>";
  }
  $sql="select id from pk where (`to`='$user_mysql' or `from`='$user_mysql' ) and status=2 and winner!='$user_mysql' ";  
  $result=mysql_query($sql);
//  echo $sql;
  if($row=mysql_fetch_object($result)){
    echo "有你参与的挑战结束了，<a href=# onclick=fail($row->id);>去算账吧，看看到底谁赢了!</a>";
  }
?>...
