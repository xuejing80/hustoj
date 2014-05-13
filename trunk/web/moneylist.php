<?php
        $OJ_CACHE_SHARE=false;
        $cache_time=30;
        require_once('./include/cache_start.php');
    require_once('./include/db_info.inc.php');
        require_once('./include/setlang.php');
        $view_title= $MSG_RANKLIST;

        $scope="";
        if(isset($_GET['scope']))
                $scope=$_GET['scope'];
        if($scope!=""&&$scope!='d'&&$scope!='w'&&$scope!='m')
                $scope='y';

        $rank = 0;
        if(isset( $_GET ['start'] ))
                $rank = intval ( $_GET ['start'] );

                if(isset($OJ_LANG)){
                        require_once("./lang/$OJ_LANG.php");
                }
                $page_size=50;
                //$rank = intval ( $_GET ['start'] );
                if ($rank < 0)
                        $rank = 0;

                $sql = "SELECT `user_id`,`nick`,`solved`,`submit`,`money`, win FROM `users` right join (select count(1) as win,winner from pk where status>1 group by winner)
			 pk on user_id=pk.winner 
			 where nick not like '*%' ORDER BY win desc,`money` DESC,submit,reg_time  LIMIT  " . strval ( $rank ) . ",$page_size";



       //         $result = mysql_query ( $sql ); //mysql_error();
        if($OJ_MEMCACHE){
                require("./include/memcache.php");
                $result = mysql_query_cache($sql) ;//or die("Error! ".mysql_error());
                if($result) $rows_cnt=count($result);
                else $rows_cnt=0;
        }else{

                $result = mysql_query($sql) or die("Error! ".mysql_error());
                if($result) $rows_cnt=mysql_num_rows($result);
                else $rows_cnt=0;
        }
                $view_rank=Array();
                $i=0;
                for ( $i=0;$i<$rows_cnt;$i++ ) {
                        if($OJ_MEMCACHE)
                                $row=$result[$i];
                        else
                                $row=mysql_fetch_array($result);
                        $rank ++;

                        $view_rank[$i][0]= $rank;
                        $view_rank[$i][1]=  "<div class=center><a href='userinfo.php?user=" . $row['user_id'] . "                                                            '>" . $row['user_id'] . "</a>" ."</div>";
                        $view_rank[$i][2]=  "<div class=center>" . htmlspecialchars ( $row['nick'] ) ." </div>";
                        $view_rank[$i][3]=  "<div class=center><a href='status.php?user_id=" . $row['user_id'] .                                                             "&jresult=4'>" . $row['win'] . "</a>" ."</div>";
                        $view_rank[$i][4]=  "<div class=center><a href='status.php?user_id=" . $row['user_id'] .                                                             "'>" . $row['money'] . "</a>" ."</div>";

                        if ($row['money'] == 0)
                                $view_rank[$i][5]= "0.000%";
                        else
                                $view_rank[$i][5]= sprintf ( "%.03lf%%", 10000 * $row['win'] / $row['money'] );

//                      $i++;
                }

if(!$OJ_MEMCACHE)mysql_free_result($result);

                $sql = "SELECT count(distinct winner) as `mycount` FROM `pk`";
        //        $result = mysql_query ( $sql );
        if($OJ_MEMCACHE){
          // require("./include/memcache.php");
                $result = mysql_query_cache($sql);// or die("Error! ".mysql_error());
                if($result) $rows_cnt=count($result);
                else $rows_cnt=0;
        }else{

                $result = mysql_query($sql);// or die("Error! ".mysql_error());
                if($result) $rows_cnt=mysql_num_rows($result);
                else $rows_cnt=0;
        }
        if($OJ_MEMCACHE)
                $row=$result[0];
        else
                $row=mysql_fetch_array($result);
                echo mysql_error ();
  //$row = mysql_fetch_object ( $result );
                $view_total=$row['mycount'];

  //              mysql_free_result ( $result );

if(!$OJ_MEMCACHE)  mysql_free_result($result);


/////////////////////////Template
require("template/".$OJ_TEMPLATE."/moneylist.php");
/////////////////////////Common foot
if(file_exists('./include/cache_end.php'))
        require_once('./include/cache_end.php');
?>
