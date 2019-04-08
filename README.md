# Enigmatique
Enigmatique is a generic Prometheus exporter for web applications or any other type of application that does not have a way to export Prometheus metrics on its own. It uses Redis to store counter/gauge data.

Why Enigmatique? Because metrics can be added by any app and you'll never know exactly how many metrics will be scraped by Prometheus between two run intervals. Also because I like the name.

## Data formatting
All counters/gauges exported to Redis must be prefixed with **enigmatique**. This is to isolate any other keys in the Redis DB from Enigmatique and not to require the use of a dedicated Redis DB.

For **HELP** information, the format is **enigmatique_metric_name:help "Help information for this metric"**

For **TYPE** information, the format is **enigmatique_metric_name:type** and it can have two values: **c** (counter) or **g** (gauge)

For the actual metric, the format is **enigmatique_metric_name:value:label**
* if label is set to **0**, as in **enigmatique_metric_name:value:0**, no label will be added to the metric
* if the lable is set to something else than **0** and there are at least two values, such as **enigmatique_metric_name:value:label1** and **enigmatique_matric_name:value:label2**, 
then the metric will be exported with labels, such as **enigmatique_metric_name{label="label1"}** and **enigmatique_metric_name{label="label2"}**

Note: in this version, if you add something to the **label** and there is only one label, it will not be added to the metric

## Counter/Gauge Initialization
Every app that will export data into Enigmatique, must first set the metrics into Redis.
This can be achieved using the SETNX Redis command which sets a key to a value only if that key does not exist.
An example of metric initialization:
* **SETNX enigmatique_metric_name:help "Some help information for this metrics"**
* **SETNX enigmatique_metric_name:type "c"**
* **SETNX enigmatique_metric_name:value:0 0**

If you want to add some labels to the metric:
* **SETNX enigmatique_metric_name:value:label1 0**
* **SETNX enigmatique_metric_name:value:label2 0**

## Requirements
Enigmatique has been developed on Ubuntu 18.04 and requires  *python3-yaml* and *python3-redis* Python packages.

## Examples
In the examples/ directory there is an PHP app that based on the parameters passed it increments a specific counter

## Output
```text
dev@dev-ubnt-1:~$ curl http://localhost:1337/metrics
# HELP enigmatique_metric_1 metric 1 help info
# TYPE enigmatique_metric_1 counter
enigmatique_metric_1{label="type1"} 1
enigmatique_metric_1{label="type2"} 7
# HELP enigmatique_metric_2 metric 2 help info
# TYPE enigmatique_metric_2 counter
enigmatique_metric_2 42
# HELP enigmatique_example_php_request_type This will count the request types
# TYPE enigmatique_example_php_request_type counter
enigmatique_example_php_request_type{label="type1"} 35
enigmatique_example_php_request_type{label="type2"} 58
```
