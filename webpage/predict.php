<?php 


	// print exec("python predict_message.py " + $_POST["email"]);
	$cmd = "/usr/bin/python predict_message.py '" + $_POST["email"] + "'";
  print `$cmd`;

?>
