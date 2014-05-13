<?php require_once("admin-header.php");?>
<?php if (!(isset($_SESSION['administrator'])|| isset($_SESSION['password_setter']) )){
	echo "<a href='../loginpage.php'>Please Login First!</a>";
	exit(1);
}
if(isset($_POST['do'])){
	//echo $_POST['user_id'];
	require_once("../include/check_post_key.php");
	//echo $_POST['passwd'];
	require_once("../include/my_func.inc.php");
	
	$user_id=$_POST['user_id'];
    $passwd =$_POST['passwd'];
    if (get_magic_quotes_gpc ()) {
		$user_id = stripslashes ( $user_id);
		$passwd = stripslashes ( $passwd);
	}
	$user_id=mysql_real_escape_string($user_id);
	$passwd=pwGen($passwd);
	$sql="update `users` set `password`='$passwd' where `user_id`='$user_id'  and user_id not in( select user_id from privilege where rightstr='administrator') ";
	mysql_query($sql);
	if (mysql_affected_rows()==1) echo "修改成功!";
  else echo "用户不存在，或者是管理员所以密码不能被重置。";
}
?>
<form action='changepass.php' method=post>
	<b>强制修改密码:</b><br />
	学生账号:<input type=text size=10 name="user_id"><br />
	密码重置为:<input type=text size=10 name="passwd" value="123456"><br />
	<?php require_once("../include/set_post_key.php");?>
	<input type='hidden' name='do' value='do'>
	<input type=submit value='进行重置'>
</form>
