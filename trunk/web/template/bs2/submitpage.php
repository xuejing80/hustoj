<html>
<head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <title><?php echo $view_title?></title>
        <link rel=stylesheet href='./template/<?php echo $OJ_TEMPLATE?>/<?php echo isset($OJ_CSS)?$OJ_CSS:"hoj.css" ?>' type='text/css'>
</head>
<body>
<div id="wrapper">
        <?php
        if(isset($_GET['id']))
                require_once("oj-header.php");
        else
                require_once("contest-header.php");
       
        ?>
<div id=main>
        <center>
<?php
if(strpos($_SERVER['HTTP_USER_AGENT'],'MSIE'))
{
   $OJ_EDITE_AREA=false;
}



if($OJ_EDITE_AREA){
?>
<script language="Javascript" type="text/javascript" src="edit_area/edit_area_full.js"></script>
<script language="Javascript" type="text/javascript">

editAreaLoader.init({
                id: "source"            
                ,start_highlight: true
                ,allow_resize: "both"
                ,allow_toggle: true
                ,word_wrap: true
                ,language: "en"
                ,syntax: "cpp"  
                        ,font_size: "8"
                ,syntax_selection_allow: "basic,c,cpp,java,pas,perl,php,python,ruby"
                        ,toolbar: "search, go_to_line, fullscreen, |, undo, redo, |, select_font,syntax_selection,|, change_smooth_selection, highlight, reset_highlight, word_wrap, |, help"          
        });
</script>
<?php }?>
<script src="include/checksource.js"></script>
<script src="include/jquery-latest.js"></script>
<form id=frmSolution action="submit.php" method="post"
<?php if($OJ_LANG=="cn"){?>
 onsubmit="return checksource(document.getElementById('source').value);"
<?php }?>
 >
<?php if (isset($id)){?>
Problem <span class=blue><b><?php echo $id?></b></span>
<input id=problem_id type='hidden'  value='<?php echo $id?>' name="id" ><br>
<?php }else{
$PID="ABCDEFGHIJKLMNOPQRSTUVWXYZ";
if ($pid>25) $pid=25;
?>
Problem <span class=blue><b><?php echo $PID[$pid]?></b></span> of Contest <span class=blue><b><?php echo $cid?></b></span><br>
<input id="cid" type='hidden' value='<?php echo $cid?>' name="cid">
<input id="pid" type='hidden' value='<?php echo $pid?>' name="pid">
<?php }?>
Language:
<select id="language" name="language">
<?php
$lang_count=count($language_ext);

  if(isset($_GET['langmask']))
        $langmask=$_GET['langmask'];
  else
        $langmask=$OJ_LANGMASK;
       
  $lang=(~((int)$langmask))&((1<<($lang_count))-1);
if(isset($_COOKIE['lastlang'])) $lastlang=$_COOKIE['lastlang'];
 else $lastlang=0;
 for($i=0;$i<$lang_count;$i++){
                if($lang&(1<<$i))
                 echo"<option value=$i ".( $lastlang==$i?"selected":"").">
                        ".$language_name[$i]."
                 </option>";
  }

?>
</select>
<br>

<textarea style="width:80%" cols=180 rows=20 id="source" name="source"><?php echo $view_src?></textarea><br>
<?php echo $MSG_Input?>:<textarea style="width:30%" cols=40 rows=5 id="input_text" name="input_text" ><?php echo $view_sample_input?></textarea>
<?php echo $MSG_Output?>:
  <textarea style="width:30%" cols=40 rows=5 id="out" name="out" >SHOULD BE:
<?php echo $view_sample_output?>
</textarea>

<br>

<input id=Submit class="btn btn-warning" title="裸提交，小心防火墙" type=submit value="<?php echo $MSG_SUBMIT?>"  onclick=do_submit();>
<input id=reverse class="btn btn-success" title="如果遇到提交后链接被重置，试试这个吧" name=reverse1 type=button value="保护性<?php echo $MSG_SUBMIT?>"  onclick=reverse_submit();>
<input type=hidden id=do_reverse name=reverse2 />
<input id=TestRun class="btn btn-info"  type=button value="<?php echo $MSG_TR?>" onclick=do_test_run();><span  class="btn"  id=result>状态</span>
<input type=reset  class="btn btn-danger" value="重置">
</form>

<iframe name=testRun width=0 height=0 src="about:blank"></iframe>
</center>
<script>
 var sid=0;
 var i=0;
  var judge_result=[<?php
  foreach($judge_result as $result){
    echo "'$result',";
  }
?>''];

function print_result(solution_id)
{
sid=solution_id;
$("#out").load("status-ajax.php?tr=1&solution_id="+solution_id);
}

function fresh_result(solution_id)
{
sid=solution_id;
var xmlhttp;
if (window.XMLHttpRequest)
  {// code for IE7+, Firefox, Chrome, Opera, Safari
  xmlhttp=new XMLHttpRequest();
  }
else
  {// code for IE6, IE5
  xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
  }
xmlhttp.onreadystatechange=function()
  {
  if (xmlhttp.readyState==4 && xmlhttp.status==200)
    {
     var tb=window.document.getElementById('result');
     var r=xmlhttp.responseText;
     var ra=r.split(",");
//     alert(r);
//     alert(judge_result[r]);
      var loader="<img width=18 src=image/loader.gif>";  
     var tag="span";
     if(ra[0]<4) tag="span disabled=true";
     else tag="a";
     tb.innerHTML="<"+tag+" href='reinfo.php?sid="+solution_id+"' class='badge badge-info' target=_blank>"+judge_result[ra[0]]+"</"+tag+">";
     if(ra[0]<4)tb.innerHTML+=loader;
     tb.innerHTML+="Memory:"+ra[1]+"kb&nbsp;&nbsp;";
     tb.innerHTML+="Time:"+ra[2]+"ms";
     if(ra[0]<4)
        window.setTimeout("fresh_result("+solution_id+")",4000);
     else
        window.setTimeout("print_result("+solution_id+")",2000);
    }
  }
xmlhttp.open("GET","status-ajax.php?solution_id="+solution_id,true);
xmlhttp.send();
}
function getSID(){
  var ofrm1 = document.getElementById("testRun").document;  
  var ret="0";
    if (ofrm1==undefined)
    {
        ofrm1 = document.getElementById("testRun").contentWindow.document;
        var ff = ofrm1;
       ret=ff.innerHTML;
    }
    else
    {
        var ie = document.frames["frame1"].document;
        ret=ie.innerText;
    }
  return ret+"";
}

var count=0;
function reverse_submit(){
if(typeof(eAL) != "undefined"){   eAL.toggle("source");eAL.toggle("source");}

      var mark="<?php echo isset($id)?'problem_id':'cid';?>";
        var problem_id=document.getElementById(mark);

        if(mark=='problem_id')
                problem_id.value='<?php echo $id?>';
        else
                problem_id.value='<?php echo $cid?>';

        document.getElementById("frmSolution").target="_self";
        document.getElementById("do_reverse").name="reverse";
        var source=document.getElementById("source");
        source.value=encode64(utf16to8(source.value));
//	source.value=source.value.split("").reverse().join("");
//	alert(source.value);
        document.getElementById("frmSolution").submit();

}
function do_submit(){

if(typeof(eAL) != "undefined"){   eAL.toggle("source");eAL.toggle("source");}


        var mark="<?php echo isset($id)?'problem_id':'cid';?>";
        var problem_id=document.getElementById(mark);
       
        if(mark=='problem_id')
                problem_id.value='<?php echo $id?>';
        else    
                problem_id.value='<?php echo $cid?>';
       
        document.getElementById("frmSolution").target="_self";
        <?php if($OJ_LANG=="cn") echo "if(checksource(document.getElementById('source').value))";?>
        document.getElementById("frmSolution").submit();
     }
var handler_interval;
function do_test_run(){
 if(handler_interval)window.clearTimeout(handler_interval);
          var loader="<img width=18 src=image/loader.gif>";
          var tb=window.document.getElementById('result');
          tb.innerHTML=loader;
  if(typeof(eAL) != "undefined"){   eAL.toggle("source");eAL.toggle("source");}
        

        var mark="<?php echo isset($id)?'problem_id':'cid';?>";
        var problem_id=document.getElementById(mark);
        problem_id.value=0;
        document.getElementById("frmSolution").target="testRun";
        document.getElementById("frmSolution").submit();
        document.getElementById("TestRun").disabled=true;
        document.getElementById("Submit").disabled=true;
        count=20;
handler_interval=        window.setTimeout("resume();",1000);
       
}
     
  function resume(){
  	count--;
        var s=document.getElementById('Submit');
        var t=document.getElementById('TestRun');
        if(count<0){
  		s.disabled=false;
  		t.disabled=false; 
                s.value="<?php echo $MSG_SUBMIT?>";
        	t.value="<?php echo $MSG_TR?>";
                if(handler_interval)window.clearTimeout(handler_interval);
        }else{
        	s.value="<?php echo $MSG_SUBMIT?>("+count+")";
        	t.value="<?php echo $MSG_TR?>("+count+")";
                window.setTimeout("resume();",1000);
        
        }
  }
</script>
<script type="text/javascript">
<!--
var keyStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
//将Ansi编码的字符串进行Base64编码
function encode64(input) {
var output = "";
var chr1, chr2, chr3 = "";
var enc1, enc2, enc3, enc4 = "";
var i = 0;
do {
chr1 = input.charCodeAt(i++);
chr2 = input.charCodeAt(i++);
chr3 = input.charCodeAt(i++);
enc1 = chr1 >> 2;
enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
enc4 = chr3 & 63;
if (isNaN(chr2)) {
enc3 = enc4 = 64;
} else if (isNaN(chr3)) {
enc4 = 64;
}
output = output + keyStr.charAt(enc1) + keyStr.charAt(enc2)
+ keyStr.charAt(enc3) + keyStr.charAt(enc4);
chr1 = chr2 = chr3 = "";
enc1 = enc2 = enc3 = enc4 = "";
} while (i < input.length);
return output;
}
//将Base64编码字符串转换成Ansi编码的字符串
function decode64(input) {
var output = "";
var chr1, chr2, chr3 = "";
var enc1, enc2, enc3, enc4 = "";
var i = 0;
if (input.length % 4 != 0) {
return "";
}
var base64test = /[^A-Za-z0-9\+\/\=]/g;
if (base64test.exec(input)) {
return "";
}
do {
enc1 = keyStr.indexOf(input.charAt(i++));
enc2 = keyStr.indexOf(input.charAt(i++));
enc3 = keyStr.indexOf(input.charAt(i++));
enc4 = keyStr.indexOf(input.charAt(i++));
chr1 = (enc1 << 2) | (enc2 >> 4);
chr2 = ((enc2 & 15) << 4) | (enc3 >> 2);
chr3 = ((enc3 & 3) << 6) | enc4;
output = output + String.fromCharCode(chr1);
if (enc3 != 64) {
output += String.fromCharCode(chr2);
}
if (enc4 != 64) {
output += String.fromCharCode(chr3);
}
chr1 = chr2 = chr3 = "";
enc1 = enc2 = enc3 = enc4 = "";
} while (i < input.length);
return output;
}
function utf16to8(str) {
var out, i, len, c;
out = "";
len = str.length;
for(i = 0; i < len; i++) {
c = str.charCodeAt(i);
if ((c >= 0x0001) && (c <= 0x007F)) {
out += str.charAt(i);
} else if (c > 0x07FF) {
out += String.fromCharCode(0xE0 | ((c >> 12) & 0x0F));
out += String.fromCharCode(0x80 | ((c >> 6) & 0x3F));
out += String.fromCharCode(0x80 | ((c >> 0) & 0x3F));
} else {
out += String.fromCharCode(0xC0 | ((c >> 6) & 0x1F));
out += String.fromCharCode(0x80 | ((c >> 0) & 0x3F));
}
}
return out;
}
function utf8to16(str) {
var out, i, len, c;
var char2, char3;
out = "";
len = str.length;
i = 0;
while(i < len) {
c = str.charCodeAt(i++);
switch(c >> 4) {
case 0: case 1: case 2: case 3: case 4: case 5: case 6: case 7:
// 0xxxxxxx
out += str.charAt(i-1);
break;
case 12: case 13:
// 110x xxxx 10xx xxxx
char2 = str.charCodeAt(i++);
out += String.fromCharCode(((c & 0x1F) << 6) | (char2 & 0x3F));
break;
case 14:
// 1110 xxxx 10xx xxxx 10xx xxxx
char2 = str.charCodeAt(i++);
char3 = str.charCodeAt(i++);
out += String.fromCharCode(((c & 0x0F) << 12) |
((char2 & 0x3F) << 6) |
((char3 & 0x3F) << 0));
break;
}
}
return out;
}
// 测试代码 开始
//var de = encode64(utf16to8("select 用户名 from 用户"));
//document.writeln(de+"<br>");
//var ee = utf8to16(decode64(de))
//document.writeln(ee);
// 测试代码 结束
//-->
</script>
<div id=foot>
        <?php require_once("oj-footer.php");?>

</div><!--end foot-->
</div><!--end main-->
</div><!--end wrapper-->
</body>
</html>
