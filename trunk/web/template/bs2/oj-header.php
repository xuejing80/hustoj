<link rel=stylesheet href='template/<?php echo $OJ_TEMPLATE?>/bootstrap.css' type='text/css'>
<script src="template/<?php echo $OJ_TEMPLATE?>/jquery-1.11.0.min.js"></script>
<script src="template/<?php echo $OJ_TEMPLATE?>/bootstrap.min.js"></script>
<div id=head>
<img id=logo src="<?php echo "template/".$OJ_TEMPLATE?>/image/logo.png"><span id="oj_name"><?php echo $OJ_NAME?></span>
<marquee scrollamount=1 direction=up scrolldelay=250 onMouseOver='this.stop()' onMouseOut='this.start()'; style='width: 600px;height: 65px'>
  <?php echo $view_marquee_msg?>
</marquee>
</div><!--end head-->
<div id=subhead>
	  <div id=menu class="navbar navbar-default navbar-fixed-top">
	  <?php $ACTIVE="btn-danger";?>
		<a  class='btn'  href="<?php echo $OJ_HOME?>"><i class="icon-home"></i>
		<?php echo $OJ_NAME?>						
		</a>
		
		<a class='btn <?php if ($url==$OJ_BBS.".php") echo " $ACTIVE";?>'  href="bbs.php">
		<i class="icon-comment"></i><?php echo $MSG_BBS?></a>
		<a class='btn <?php if ($url=="problemset.php") echo " $ACTIVE";?>' href="problemset.php">
		<i class="icon-question-sign"></i><?php echo $MSG_PROBLEMS?></a>
		
	  <!-- <a  class='btn <?php if ($url=="submitpage.php") echo " $ACTIVE";?>' href="submitpage.php">
		<i class="icon-pencil"></i><?php echo "编辑器"?></a>
		-->
		<a  class='btn <?php if ($url=="status.php") echo "  $ACTIVE";?>' href="status.php">
		<i class="icon-check"></i><?php echo $MSG_STATUS?></a>
		
		<a class='btn <?php if ($url=="ranklist.php") echo "  $ACTIVE";?>' href="ranklist.php">
		<i class="icon-signal"></i><?php echo $MSG_RANKLIST?></a>
		
		<a class='btn <?php if ($url=="moneylist.php") echo "  $ACTIVE";?>' href="moneylist.php">
		<i class=icon-fire></i>挑战者</a>
		
		<a class='btn <?php if ($url=="contest.php") echo "  $ACTIVE";?>'  href="contest.php">
		<i class="icon-fire"></i><?php echo checkcontest($MSG_CONTEST)?></a>
		
		<a class='btn <?php if ($url=="recent-contest.php") echo " $ACTIVE";?>' href="recent-contest.php">
		<i class="icon-share"></i><?php echo "$MSG_RECENT_CONTEST"?></a>
	     <span class="btn dropdown">
              <a href="#" class="dropdown-toggle" data-toggle="dropdown">帮助<b class="caret"></b></a>
              <ul class="dropdown-menu">
                <li>
		<a class='btn <?php if ($url==(isset($OJ_FAQ_LINK)?$OJ_FAQ_LINK:"faqs.php")) echo " $ACTIVE";?>' href="<?php echo isset($OJ_FAQ_LINK)?$OJ_FAQ_LINK:"faqs.php"?>">
                <i class="icon-info-sign"></i><?php echo "$MSG_FAQ"?></a>
		</li>
                <li>
                <a class='btn' href="http://linux.die.net/man/3/" target=_blank>C手册</a>
		</li>
                <li>
                <a class='btn' href="http://www.cplusplus.com/reference/" target=_blank>C++手册</a>
		</li>
                <li>
                <a class='btn' href="http://docs.oracle.com/javase/7/docs/api/index.html" target=_blank>Java手册</a>
		</li>
              </ul>
            </span>	
            <span class="btn nav navbar-nav navbar-right">
                		
		<?php if(isset($OJ_DICT)&&$OJ_DICT&&$OJ_LANG=="cn"){?>
					  
		<span div class='btn '  style="color:1a5cc8" id="dict_status"></span>
					 
					  <script src="include/underlineTranslation.js" type="text/javascript"></script>
					  <script type="text/javascript">dictInit();</script>
		<?php }?>
		<script src="include/profile.php?<?php echo rand();?>" ></script>
		<a href="#">&nbsp;</a>
	    </span>
	</div><!--end menu-->
<div id=profile >
</div><!--end profile-->
</div><!--end subhead-->
