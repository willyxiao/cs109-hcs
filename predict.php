<?php 


	// print exec("python predict_message.py " + $_POST["email"]);
	$cmd = "/usr/bin/python predict_message.py 'hi bye hi lie hi die hi why hi sly'";
  print `$cmd`;

?>
