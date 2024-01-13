# todolist

## todo

- [] 编写单元测试代码

## finished

- [x] 测试单核和多核性能
  - 这个算法在获得足够的CPU资源（即接近或等于1个完整核心）时表现最佳。  
  - 过低的CPU资源分配会严重影响性能，而适度的分配（如0.1核心）则能提供更合理的性能。
  - 单核和多核性能差异不大  

- [x] 测试不同cpu架构性能的差异  
  - 测试了12th Gen Intel(R) Core(TM) i5-12490F 和 rk3399两颗cpu的性能

- [x] 测试不同消息长度的时间
  - 测试了10M文本的加密速度，在1s内可以完成全部算法内容

- [x] 测试极限（1s）时的节点数  
  - 12th Gen i5 CPU大概是90多个节点时达到1s的时间上限

- [x] 非docker部署需要获取本机ip  
  - 添加了通过网卡获取ip的方法

- [x] 复习预备知识  
- [x] 准备圆场话术  