# 场景库构建方案
+ ADAS基于用例测试
```text
静态场景实现 -> 自车预期行为 -> 目标行为 
```

```text
1.按照ADAS功能分类，再分子功能，列举法规/功能规范/人工经验用例场景；
2.参数交叉泛化场景用例；
3.支持扩张用例；
```
+ AD基于场景测试
```text
1.根据所测模块大功能分类，数据来源进行子分类；
2.参数交叉泛化用例/原始数据录入实现；
3.支持添加新用例；
```
+ 自动生成场景
```text
1.七层元素组合录入，组合交叉实现；
2.过滤无效组合逻辑；
3.缺少/多余元素补正；
```
# 场景库用例自动化
+ open格式导入
```text
偏重于基于用例的测试
```
+ 原始交通流数据灌入
```text
基于场景的测试
```
# 用例执行结果自动评价
```text
1.同实车/感知测试filter方案；
2.adas场景生成时自动生成判断逻辑；
```