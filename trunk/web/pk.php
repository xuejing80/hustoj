<?php
  require_once('./include/db_info.inc.php');
  ini_set("display_errors","On");

  if(!isset($_SESSION['user_id'])) return;
  if(!isset($_GET['pk'])) return;
  $pk=intval($_GET['pk']);
  
  if($pk==0){

	  $problem_id=intval($_GET['problem_id']);
          if($problem_id==0) return;
          $from= $_SESSION['user_id'];  
          $to=$_GET['to'];
          if (get_magic_quotes_gpc ()) {
                   $to = stripslashes ( $to);
          }
	  if($to==$from){
       	     echo "请勿自残！";
	     return;
          }
          $from_mysql=mysql_real_escape_string($from);
          $to_mysql=mysql_real_escape_string($to);
          $sql="select 1 from solution where user_id='$from_mysql' and problem_id=$problem_id and result=4";
          $result=mysql_query($sql);
          $row=mysql_fetch_object($result);
          if($row){
              echo "不能用已经做对的题来挑战别人";
              return;
          }
          $sql="select 1 from solution where user_id='$to_mysql' and problem_id=$problem_id and result=4";
          $result=mysql_query($sql);
          $row=mysql_fetch_object($result);
          if($row){
              echo "人家已经做对这个题目了，你是找死么?";
              return;
          }

          $sql="select 1 from pk where `from`='$from_mysql' and `to`='$to_mysql' and problem_id=$problem_id";
          $result=mysql_query($sql);
          $row=mysql_fetch_object($result);
          if($row){
              echo "挑战已经发起过";
              return;
          }
  
          $sql="insert into pk(problem_id,`from`,`to`,money,status) values($problem_id,'$from_mysql','$to_mysql',100,0)"; 
          mysql_query($sql);
	      echo "挑战请求中...";
	  return;
   }
   if(!isset($_GET['pk_id'])) return;
   $pk_id=intval($_GET['pk_id']); 
   $sql="select * from pk where id=$pk_id";
   $result= mysql_query($sql);
   $row=mysql_fetch_object($result);
   if(!$row){
       echo "挑战$pk_id不存在！";
       return;
   }
   $from=$row->from;
   $to=$row->to;
   $from_mysql=mysql_real_escape_string($from);
   $to_mysql=mysql_real_escape_string($to);
   $status=$row->status;
   $problem_id=$row->problem_id; 
   $money=$row->money;
   $winner=$row->winner;
   if($pk==-1){
      if($_SESSION['user_id']!=$to){
		echo "该挑战不属于你";
		 return;
      }
      if($status!=0){
                echo "挑战重复拒绝！";
                return;
      }
      $sql="update pk set status=-1 where id=$pk_id";
       mysql_query($sql);
      $sql="update users set money=money-$money/2 where user_id='$to_mysql'";
       mysql_query($sql);
      echo "<script>alert('挑战拒绝成功,遭到系统鄙视，扣除一半挑战金$".($money/2)."');</script>";
      return ;
   }
   if($pk==1){
      if($_SESSION['user_id']!=$to){
		echo "该挑战不属于你";
		 return;
      }
      if($status!=0){
                echo "挑战重复接受！";
                return;
      }
      $sql="update pk set status=1 where id=$pk_id";
       mysql_query($sql);
      $sql="update users set money=money-$money where user_id='$to_mysql' or user_id='$from_mysql'";
       mysql_query($sql);
      echo "挑战接受成功,押金已经扣除";
      return ;
   }
   if($pk==2){
      if($_SESSION['user_id']!=$to&&$_SESSION['user_id']!=$from){
                echo "该挑战不属于你";
                 return;
      }
      if($status!=1){
                echo "挑战未被接受,或奖金已经领取！";
                return;
      }
      $sql="select user_id from solution where problem_id=$problem_id and result=4 and user_id in ('$from_mysql','$to_mysql') order by solution_id desc limit 1";     
      $result= mysql_query($sql);
      $row=mysql_fetch_object($result);
      if(!$row){
         echo "两人均没有完成，无法分配奖金";
	 return;
      }
      $winner=$row->user_id;
      $winner_mysql=mysql_real_escape_string($winner);
      $sql="update pk set status=2,winner='$winner' where id=$pk_id";
       mysql_query($sql);
      $sql="update users set money=money+2*$money where user_id='$winner'";
       mysql_query($sql);
      $sql="update pk set status=2 where id=$pk_id";
       mysql_query($sql);
      echo "<script>alert('".$winner."先完成题目，奖金已经发放到账户中!');</script>";
      return ;
   }

   if($pk==3){
      if($_SESSION['user_id']!=$to&&$_SESSION['user_id']!=$from){
		echo "该挑战不属于你";
		 return;
      }
      if($status!=2){
                echo "挑战没有结束或已经终止！";
                return;
      }
      $sql="update pk set status=3 where id=$pk_id";
       mysql_query($sql);
      echo "<script>alert('对方率先AC,并取走奖金');</script>";
      return ;
   }
?>
