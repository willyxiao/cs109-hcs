<?php 


	print exec("python predict_message.py " + $_POST["email"]);

?>