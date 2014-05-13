<html>
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
	<title><?php echo $view_title?></title>
	<link rel=stylesheet href='./template/<?php echo $OJ_TEMPLATE?>/<?php echo isset($OJ_CSS)?$OJ_CSS:"hoj.css" ?>' type='text/css'>
</head>
<body>
<div id="wrapper">
	<?php require_once("oj-header.php");?>
<div id=main>
 <div id='source'></div>
<div id='source'>
<iframe width=100% height=240  src="showsource-mini.php?id=<?php echo $id?>"></iframe>
</div>
<pre id='errtxt' class="alert alert-error"><?php echo $view_reinfo?></pre>
<div id='errexp' class="alert">Explain:</div>

<div id=foot>
	<?php require_once("oj-footer.php");?>
</div><!--end foot-->
<script>
   var pats=new Array();
   var exps=new Array();
<?php
   $sql = "select * from ErrFeature where type=1;";
   $result = mysql_query($sql);
   $ix = 0;
   while($row = mysql_fetch_object($result))
   {
        $pat = $row->regex;
        echo "\npats[$ix]=/$pat/";
        $exp = $row->info;
        echo "\nexps[$ix]=\"$exp\";";
        $ix++;
   }
   ?>

   function explain(){
     //alert("asdf");
       var errmsg=document.getElementById("errtxt").innerHTML;
           var expmsg="辅助解释：<br>";
           for(var i=0;i<pats.length;i++){
                   var pat=pats[i];
                   var exp=exps[i];
                   var ret=pat.exec(errmsg);
                   if(ret){
                      expmsg+="<strong>"+ret+":</strong>"+exp+"<br>";
                   }
           }
           document.getElementById("errexp").innerHTML=expmsg;
     //alert(expmsg);
   }
   explain();

 </script>
<script src=include/jquery-latest.js></script>
<script>
 $("#source").load("showsource.php?id=<?php echo $id?> #main");

</div><!--end main-->
</div><!--end wrapper-->
</body>
</html>
