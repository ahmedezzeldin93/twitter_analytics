
import sys
import time
import json
import psutil
import logging

from pyspark import SparkContext
from pyspark.streaming import StreamingContext

from pyspark.streaming.kafka import KafkaUtils
#from websocket import create_connection


# logger = logging.getLogger('twana')
# logger_dir_path = "/work/twitter_analytics/logs"
# formatter = logging.Formatter('%(asctime)s %(levelname)s:%(message)s')
# logger.setLevel(logging.DEBUG)


def takeAndPrint(time, rdd, num=1000):
    result = []
    taken = rdd.take(num + 1)
    url = 'ws://localhost:8888/'
    print("-------------------------------------------")
    print("Time: %s" % time)
    print("-------------------------------------------")
    for record in taken[:num]:
    	print(record)
    	result.append(record)
    # ws = create_connection(url)
    # ws.send(json.dumps(result))
    # ws.close()
    if len(taken) > num:
        print("...")
    print("")


def updateFunc(new_values, last_sum):
        return sum(new_values) + (last_sum or 0)


sc = SparkContext(appName="PythonTwitterStreaming")
ssc = StreamingContext(sc, 1)

kvs = KafkaUtils.createStream(ssc, 'localhost:9092', "spark-streaming-consumer", {'my-topic': 1})
tweets = kvs.map(lambda x: x[1])

ssc.checkpoint("./checkpoint-tweet")

running_counts = tweets.flatMap(lambda line: line.split(" "))\
                    .map(lambda word: (word, 1))\
                    .updateStateByKey(updateFunc).transform(lambda rdd: rdd.sortBy(lambda x: x[1],False))


running_counts.foreachRDD(takeAndPrint)

ssc.start()
ssc.awaitTermination()