# 用Python客户端测试RabbitMQ.

1. 安装
brew install rabbitmq

## 进入安装目录
cd /usr/local/Cellar/rabbitmq/3.7.5

# 启动
brew services start rabbitmq
# 当前窗口启动
rabbitmq-server
启动控制台之前需要先开启插件

./rabbitmq-plugins enable rabbitmq_management
进入控制台: http://localhost:15672/

用户名和密码：guest,guest

RabbitMQ提供了6种模式，分别是HelloWorld，Work Queue，Publish/Subscribe，Routing，Topics，RPC Request/reply，本文详细讲述了前5种，并给出代码实现和思路。其中Publish/Subscribe，Routing，Topics三种模式可以统一归为Exchange模式，只是创建时交换机的类型不一样，分别是fanout、direct、topic。Spring提供了rabbitmq的一个实现，所以集成起来很方便，文章第4章给出了订阅者模式的一种spring配置。


https://www.jianshu.com/p/b7cc32b94d2a
RabbitMQ 的4种集群架构
1. 主备模式
2. 远程模式
    远程模式可以实现双活的一种模式，简称 shovel 模式，所谓的 shovel 就是把消息进行不同数据中心的复制工作，可以跨地域的让两个 MQ 集群互联，远距离通信和复制。

    Shovel 就是我们可以把消息进行数据中心的复制工作，我们可以跨地域的让两个 MQ 集群互联。
3. 镜像模式
    非常经典的 mirror 镜像模式，保证 100% 数据不丢失。在实际工作中也是用得最多的，并且实现非常的简单，一般互联网大厂都会构建这种镜像集群模式。
    mirror 镜像队列，目的是为了保证 rabbitMQ 数据的高可靠性解决方案，主要就是实现数据的同步，一般来讲是 2 - 3 个节点实现数据同步。对于 100% 数据可靠性解决方案，一般是采用 3 个节点。

4. 多活模式
    也是实现异地数据复制的主流模式，因为 shovel 模式配置比较复杂，所以一般来说，实现异地集群的都是采用这种双活 或者 多活模型来实现的。这种模式需要依赖 rabbitMQ 的 federation 插件，可以实现持续的，可靠的 AMQP 数据通信，多活模式在实际配置与应用非常的简单。

    rabbitMQ 部署架构采用双中心模式(多中心)，那么在两套(或多套)数据中心各部署一套 rabbitMQ 集群，各中心的rabbitMQ 服务除了需要为业务提供正常的消息服务外，中心之间还需要实现部分队列消息共享。







1.1 简单模式Hello World
功能：一个生产者P发送消息到队列Q,一个消费者C接收
生产者实现思路：

创建连接工厂ConnectionFactory，设置服务地址127.0.0.1，端口号5672，设置用户名、密码、virtual host，从连接工厂中获取连接connection，使用连接创建通道channel，使用通道channel创建队列queue，使用通道channel向队列中发送消息，关闭通道和连接。

消费者实现思路

创建连接工厂ConnectionFactory，设置服务地址127.0.0.1，端口号5672，设置用户名、密码、virtual host，从连接工厂中获取连接connection，使用连接创建通道channel，使用通道channel创建队列queue, 创建消费者并监听队列，从队列中读取消息。
---

1.2 工作队列模式Work Queue
功能：一个生产者，多个消费者，每个消费者获取到的消息唯一，多个消费者只有一个队列
任务队列：避免立即做一个资源密集型任务，必须等待它完成，而是把这个任务安排到稍后再做。我们将任务封装为消息并将其发送给队列。后台运行的工作进程将弹出任务并最终执行作业。当有多个worker同时运行时，任务将在它们之间共享。

生产者实现思路：

创建连接工厂ConnectionFactory，设置服务地址127.0.0.1，端口号5672，设置用户名、密码、virtual host，从连接工厂中获取连接connection，使用连接创建通道channel，使用通道channel创建队列queue，使用通道channel向队列中发送消息，2条消息之间间隔一定时间，关闭通道和连接。

消费者实现思路：

创建连接工厂ConnectionFactory，设置服务地址127.0.0.1，端口号5672，设置用户名、密码、virtual host，从连接工厂中获取连接connection，使用连接创建通道channel，使用通道channel创建队列queue，创建消费者C1并监听队列，获取消息并暂停10ms，另外一个消费者C2暂停1000ms，由于消费者C1消费速度快，所以C1可以执行更多的任务。

---
1.3 发布/订阅模式Publish/Subscribe

功能：一个生产者发送的消息会被多个消费者获取。一个生产者、一个交换机、多个队列、多个消费者

生产者：可以将消息发送到队列或者是交换机。

消费者：只能从队列中获取消息。

如果消息发送到没有队列绑定的交换机上，那么消息将丢失。

交换机不能存储消息，消息存储在队列中

生产者实现思路：

创建连接工厂ConnectionFactory，设置服务地址127.0.0.1，端口号5672，设置用户名、密码、virtual host，从连接工厂中获取连接connection，使用连接创建通道channel，使用通道channel创建队列queue，使用通道channel创建交换机并指定交换机类型为fanout，使用通道向交换机发送消息，关闭通道和连接。

消费者实现思路：

创建连接工厂ConnectionFactory，设置服务地址127.0.0.1，端口号5672，设置用户名、密码、virtual host，从连接工厂中获取连接connection，使用连接创建通道channel，使用通道channel创建队列queue，绑定队列到交换机，设置Qos=1，创建消费者并监听队列，使用手动方式返回完成。可以有多个队列绑定到交换机，多个消费者进行监听。

1.4 路由模式Routing
说明：生产者发送消息到交换机并且要指定路由key，消费者将队列绑定到交换机时需要指定路由key

生产者实现思路：

创建连接工厂ConnectionFactory，设置服务地址127.0.0.1，端口号5672，设置用户名、密码、virtual host，从连接工厂中获取连接connection，使用连接创建通道channel，使用通道channel创建队列queue，使用通道channel创建交换机并指定交换机类型为direct，使用通道向交换机发送消息并指定key=b，关闭通道和连接。

消费者实现思路：

创建连接工厂ConnectionFactory，设置服务地址127.0.0.1，端口号5672，设置用户名、密码、virtual host，从连接工厂中获取连接connection，使用连接创建通道channel，使用通道channel创建队列queue，绑定队列到交换机，设置Qos=1，创建消费者并监听队列，使用手动方式返回完成。可以有多个队列绑定到交换机,但只要绑定key=b的队列key接收到消息，多个消费者进行监听。


1.5 通配符模式Topics  

说明：生产者P发送消息到交换机X，type=topic，交换机根据绑定队列的routing key的值进行通配符匹配；符号#：匹配一个或者多个词lazy.# 可以匹配lazy.irs或者lazy.irs.cor

符号*：只能匹配一个词lazy.* 可以匹配lazy.irs或者lazy.cor

生产者实现思路：

创建连接工厂ConnectionFactory，设置服务地址127.0.0.1，端口号5672，设置用户名、密码、virtual host，从连接工厂中获取连接connection，使用连接创建通道channel，使用通道channel创建队列queue，使用通道channel创建交换机并指定交换机类型为topic，使用通道向交换机发送消息并指定key=key.1，关闭通道和连接。

消费者实现思路：

创建连接工厂ConnectionFactory，设置服务地址127.0.0.1，端口号5672，设置用户名、密码、virtual host，从连接工厂中获取连接connection，使用连接创建通道channel，使用通道channel创建队列queue，绑定队列到交换机，设置Qos=1，创建消费者并监听队列，使用手动方式返回完成。可以有多个队列绑定到交换机,凡是绑定规则符合通配符规则的队列均可以接收到消息，比如key.*,key.#，多个消费者进行监听。

 
test dev 