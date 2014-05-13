<?php 
if(preg_match('/[Ss]pider/',$_SERVER['HTTP_USER_AGENT'])) return;
@session_start();
	ini_set("display_errors","Off");
static 	$DB_HOST="localhost";
static 	$DB_NAME="jol";
static 	$DB_USER="root";
static 	$DB_PASS="root";
	// connect db 
static 	$OJ_NAME="浙江传媒学院在线评测系统";
static 	$OJ_HOME="./";
static 	$OJ_ADMIN="root@localhost";
static 	$OJ_DATA="/home/judge/data";
static 	$OJ_BBS="discuss";//"bbs" for phpBB3 bridge or "discuss" for mini-forum
static  $OJ_ONLINE=true;
static  $OJ_LANG="cn";
static  $OJ_SIM=true; 
static  $OJ_DICT=false;
static  $OJ_LANGMASK=0; //1mC 2mCPP 4mPascal 8mJava 16mRuby 32mBash 
static  $OJ_EDITE_AREA=true;//true: syntax highlighting is active
static  $OJ_AUTO_SHARE=true;//true: One can view all AC submit if he/she has ACed it onece.
static  $OJ_CSS="hoj.css";
static  $OJ_SAE=false; //using sina application engine
static  $OJ_VCODE=1;
static  $OJ_APPENDCODE=true;
static  $OJ_MEMCACHE=true;
static  $OJ_MEMSERVER="127.0.0.1";
static  $OJ_MEMPORT=11211;
static  $SAE_STORAGE_ROOT="http://hustoj-web.stor.sinaapp.com/";
static  $OJ_TEMPLATE="bs";
static  $OJ_LOGIN_MOD="hustoj";
static  $OJ_SHOW_DIFF=1;
static  $OJ_RANK_LOCK_PERCENT=0;
if(isset($_GET['tp'])) $OJ_TEMPLATE=$_GET['tp'];
static  $OJ_SHOW_DIFF=true;
static  $OJ_TEST_RUN=true;
//if($_SESSION['user_id']=='zhblue') $OJ_TEMPLATE="new";
if (isset($_SESSION['OJ_LANG'])) $OJ_LANG=$_SESSION['OJ_LANG'];

	if($OJ_SAE)	{
		$OJ_DATA="saestor://data/";
	//  for sae.sina.com.cn
		mysql_connect(SAE_MYSQL_HOST_M.':'.SAE_MYSQL_PORT,SAE_MYSQL_USER,SAE_MYSQL_PASS);
		$DB_NAME=SAE_MYSQL_DB;
	}else{
		//for normal install
		if(!mysql_pconnect($DB_HOST,$DB_USER,$DB_PASS)) 
			die('Could not connect: ' . mysql_error());
	}
	// use db
	mysql_query("set names utf8");
  //if(!$OJ_SAE)mysql_set_charset("utf8");
	
	if(!mysql_select_db($DB_NAME))
		die('Can\'t use foo : ' . mysql_error());
	//sychronize php and mysql server
	date_default_timezone_set("PRC");
	mysql_query("SET time_zone ='+8:00'");
if(date("G")==23&&date("i")>50) $OJ_TEMPLATE="mario";
	
?>
