# zotero_collector
## web translator
用于 Zotero 客户端的 translator，目前包括：
- [小宇宙](https://github.com/dofine/zotero_collector/blob/main/translators/xiaoyuzhou.js)，能够抓取
    - 播客名称
    - 单集名称、URL、shownotes、单集时长、发布日期
    - 热门 Top3 评论（作为笔记）

使用方法参考 https://github.com/l0o0/translators_CN

## 服务端
为了方便通过手机 app 直接把当前在听的播客发送至 Zotero，用 `flask` 写了一个[简单的服务](https://github.com/dofine/zotero_collector/blob/main/app.py)运行在服务器上，配合 iOS 快捷指令使用。

1. 在 Zotero 后台获取自己的[账号和 apikey](https://www.zotero.org/settings/keys/new)，并授予读/写权限
2. 修改配置文件 [`config.json.example`](https://github.com/dofine/zotero_collector/blob/main/config.json.example) 并重命名为 `config.json`，其中 `zotero_collection` 为默认保存到的 collection ID
3. 通过 iOS 快捷指令发送 `POST` 请求

## 参考
- https://github.com/l0o0/translators_CN
