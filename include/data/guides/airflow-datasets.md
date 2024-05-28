TEST datasets are always yellow


### Combined dataset and time-based scheduling

In Airflow 2.9 and later, you can combine dataset-based scheduling with time-based scheduling with the `DatasetOrTimeSchedule` timetable. A DAG scheduled with this timetable will run either when its `timetable` condition is met or when its `dataset` condition is met.

The DAG shown below runs on a time-based schedule defined by the `0 0 * * *` cron expression, which is every day at midnight. The DAG also runs when either `dataset3` or `dataset4` is updated.