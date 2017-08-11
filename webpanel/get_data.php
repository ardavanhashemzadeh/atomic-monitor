<?php
	header('Content-Type: application/json');
	if(!isset($_GET['path']) || !isset($_GET['type'])) {
		echo json_encode(array(
			'error' => 'Invalid URL!'
		));
	}
	else {
		$url = htmlspecialchars($_GET['path']);
		$type = htmlspecialchars($_GET['type']);

		if($type == 'home') {
			echo file_get_contents($url);
		}
		else if($type == 'servers') {
			echo file_get_contents($url);
		}
		else if($type == 'logs') {
			$level = urlencode($_GET['level']);
			$id = urlencode($_GET['id']);
			$count = urlencode($_GET['count']);
			$search_for = urlencode($_GET['search_for']);
			$filter_out = urlencode($_GET['filter_out']);
			echo file_get_contents($url . "?level=$level&id=$id&count=$count&search_for=$search_for&filter_out$filter_out");
		}
	}
?>