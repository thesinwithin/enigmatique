<?php
	// Initialize a connection to Redis
	$redis = new Redis();
	$redis->connect('127.0.0.1', 6379);

	// Set the default values for Enigmatique metrics import
	$redis->setnx("enigmatique_example_php_request_type:help","This will count the request types");
	$redis->setnx("enigmatique_example_php_request_type:type","c");
	$redis->setnx("enigmatique_example_php_request_type:value:type1",0);
	$redis->setnx("enigmatique_example_php_request_type:value:type2",0);

	// Increment the counters based on the request type
	$req_type = $_GET['req_type'];
		if ($req_type == "type1") {
			$redis->incr("enigmatique_example_php_request_type:value:type1");
		};
		if ($req_type == "type2") {
			$redis->incr("enigmatique_example_php_request_type:value:type2");
		}

	// Get and display the Redis keys values
	$type1 = $redis->get("enigmatique_example_php_request_type:value:type1");
	$type2 = $redis->get("enigmatique_example_php_request_type:value:type2");

	printf("Redis value for enigmatique_example_php_request_type:value:type1 is %s <br/>", $type1);
	printf("Redis value for enigmatique_example_php_request_type:value:type2 is %s <br/>", $type2);
?>
