<?php 


	// print exec("python predict_message.py " + $_POST["email"]);
	$cmd = "/usr/bin/python /var/www/html/cs109-hcs/predict_message.py '" . $_GET["email"] . "'";
  print `$cmd`;

?>
