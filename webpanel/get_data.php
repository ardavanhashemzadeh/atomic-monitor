<?php
	header('Content-Type: application/json');
	if(!isset($_GET['url'])) {
		echo json_encode(array(
			'error' => 'Invalid "url" input! Please add one!'
		));
	}
	else {
		$url = htmlspecialchars($_GET['url']);
		echo file_get_contents($url);
	}
?>