<?php
        require_once('./include/db_info.inc.php');
        require_once('./include/setlang.php');
        $view_title= "Welcome To Online Judge";

require_once("./include/const.inc.php");
require_once("./include/my_func.inc.php");
$lost_user_id=$_POST['user_id'];
$lost_email=$_POST['email'];
    $vcode=trim($_POST['vcode']);
    if($lost_user_id&&($vcode!= $_SESSION["vcode"]||$vcode==""||$vcode==null) ){
                echo "<script language='javascript'>\n";
                echo "alert('Verify Code Wrong!');\n";
                echo "history.go(-1);\n";
                echo "</script>";
                exit(0);
    }
  if(get_magic_quotes_gpc()){
        $lost_user_id=stripslashes($lost_user_id);
        $lost_email=stripslashes($lost_email);
  }
  $sql="SELECT `email` FROM `users` WHERE `user_id`='".mysql_real_escape_string($lost_user_id)."'";
                $result=mysql_query($sql);
                $row = mysql_fetch_array($result);
 if($row && $row['email']==$lost_email&&strpos($lost_email,'@')){
   $_SESSION['lost_user_id']=$lost_user_id;
   $_SESSION['lost_key']=strtoupper(substr(MD5($user_id.rand(0,9999999)),0,16));

   mail($lost_email,"OJ系统密码重置激活","$lost_user_id:\n您好！\n您在OJ系统选择了找回密码服务,为了验证您的身份,请将下面字串输入口令重置页面以确认身份:".$_SESSION['lost_key']."\n\n\n浙江传媒学院在线评测系统", 'From: admin@hustoj.com' );
   require("template/".$OJ_TEMPLATE."/lostpassword2.php");

 }else{

/////////////////////////Template
   require("template/".$OJ_TEMPLATE."/lostpassword.php");

}
/////////////////////////Common foot
?>
