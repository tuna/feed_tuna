# 金枪鱼喂食计划

源于几个flag
 - [喂食.tuna.moe](https://github.com/tuna/collection/issues/44)
 - [开店卖周边](https://github.com/tuna/collection/issues/41)

i.e., TUNA 一直希望有一个小额募捐平台，及一个可以用来卖贴纸、卖 Tunaive 、卖装满镜像的硬盘的平台。[tuna/feed_tuna](https://github.com/tuna/feed_tuna)项目目前是一个利用了2017 年 5 月 18 日 Telegram Bot API 新增的 Payment 功能的 Telegram Bot, 实现了金枪鱼喂食计划部分功能。

Live Demo: (http://t.me/FeedTUNA_bot) 付款可用卡号： 4242 4242 4242 4242

## 目前实现的功能
### 商品销售
  参照已有的商品，修改`commodities.json`即可。货币的单位是0.01CNY，最低售价为1美元（等值的人民币）。标注`"virtual":true`的虚拟商品不收取运费。根据App Store的有关规定不能销售虚拟服务（如TUNA会员）。

### 配送方式
  参照已有的配送方式，修改`shipping.json`即可。有一个属性`overseas`，默认为`false`，用于区分海内海外。

### 支付与收款
  Telegram 目前与第三方支付平台 [Stripe](https://stripe.com) 合作。Stripe 理论上支持 Visa、Mastercard 和支付宝等多种支付方式，但目前 Telegram 似乎只能用信用卡。Stripe不支持中国大陆，因此收到的款项会由 Stripe 转到昌老师的香港账户上。

### 订单管理
  为减少复杂性只管理支付成功的订单，支付成功的订单保存在 SQLite。鉴于我们不会收到很多订单，未必需要订单管理的前端，一个比较简单的办法是用一个邮件列表管理订单。

## 遇到的问题

### Stripe收款问题
  Stripe 需要对我们的收款账户进行进一步认证，可能会有问题。

## 更多flag

 - RESTful API
