#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pika
import random


number = random.randint(1, 1000)
body = 'hello world:%s' % number

# 新建连接，rabbitmq安装在本地则hostname为'localhost'
hostname = 'localhost'
parameters = pika.ConnectionParameters(hostname)
connection = pika.BlockingConnection(parameters)
# 创建通道
channel = connection.channel()
# 声明一个队列，生产者和消费者都要声明一个相同的队列，用来防止万一某一方挂了，另一方能正常运行
channel.queue_declare(queue='hello')
# 交换机; 队列名,写明将消息发往哪个队列; 消息内容
# routing_key在使用匿名交换机的时候才需要指定，表示发送到哪个队列
channel.basic_publish(exchange='', routing_key='hello_002', body=body)
connection.close()

print (" [x] Sent "+ body)
