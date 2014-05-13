<?php 
	require_once("./include/my_func.inc.php");
    
	function check_login($user_id,$password){
		$user_id=mysql_escape_string($user_id);
		$pass2 = 'No Saved';
		session_destroy();
		session_start();
                 $ip = mysql_real_escape_string($_SERVER['REMOTE_ADDR']);
                if( !empty( $_SERVER['HTTP_X_FORWARDED_FOR'] ) ){

                    $REMOTE_ADDR = $_SERVER['HTTP_X_FORWARDED_FOR'];

                    $tmp_ip = explode( ',', $REMOTE_ADDR );

                    $ip = $tmp_ip[0];

                }


		$sql="INSERT INTO `loginlog` VALUES('$user_id','$pass2','".$ip."',NOW())";
		@mysql_query($sql) or die(mysql_error());
		$sql="SELECT `user_id`,`password` FROM `users` WHERE `user_id`='".$user_id."'";
		$result=mysql_query($sql);
		$row = mysql_fetch_array($result);
		if($row && pwCheck($password,$row['password'])){
			$user_id=$row['user_id'];
			mysql_free_result($result);
			return $user_id;
		}
		mysql_free_result($result);
		return false; 
	}
?>
