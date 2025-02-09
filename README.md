# RStatus

<div align="center">
    <img width="100px" src="./Client/icon.ico" align="center" alt="RStatus" />
    <h2 align="center">RStatus</h2>
    <p align="center">一套适用于站长的活动公开系统。</p>
</div>

<div align="center">
    <img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/Rise-forever/RStatus?style=for-the-badge"> 
    <img alt="GitHub" src="https://img.shields.io/github/license/Rise-forever/RStatus?style=for-the-badge"> 
    <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/Rise-forever/RStatus?style=for-the-badge"> 
</div>

> [!WARNING]
>
> ## 以下留言致以来自中国大陆的开发者：
>
> For English speakers, please ignore this message.
>
> **请不要在 issues 板块下发表任何无意义且无法促进此项目持续发展的内容**。在提交 issue 之前，请仔细思考你要发布的内容**是否合理**，如果不能，请不要浪费其他人的时间；同时请考虑**开发者能否修复/实现**，如果不能，请自己提交 PR 而不是 issue。
> 在交流时请尊重他人，不要使用不文明用语。请不要催促或强求开发者和其他贡献者，他们是一群热爱开源的志愿者，不是你的私人雇员！
>
> 尽可能在除国内社交平台外的其他地方使用英语而不是中文，我们会优先处理英文内容。

## 简介
> [!IMPORTANT]
> 以下内容于2025年2月9日撰写，本软件的实际功能可能会因新版本推送而与简介有所差异。

**RStatus**是一套网站系统，使用`易语言`与`Python`编写。其主要功能是将运行客户端的PC的`最前端活动窗口名`定时上传至服务器端，使客户能够通过浏览器来获取`活动名称`。

- 技术栈：`Python`、`易语言`
- 关键词：`B/S`、`C/S`、`监控`
- 支持的操作系统：WindowsXP以上（**客户端**）、Windows7以上（**服务器端**）

## 声明
> [!NOTE]
> 以下简称 `RStatus` 为 **本软件** 。
- 本软件的 `客户端` 使用**易语言**编写，部分反病毒软件可能会向用户报告本软件可能危害此电脑，请**忽略这一类提示并信任本软件**。
- 本软件的 `客户端` 在使用者要求时会向 `SOFTWARE\Microsoft\Windows\CurrentVersion\Run\RsvStatusClient` 中写入程序的完整路径，用于实现“**开机自启动**”功能。此操作可在 `客户端程序` 中撤销。
- 应用程序内提供的部分功能可能需要向用户申请 `管理员权限`。
- 除 `注册表项` 外，本软件 `客户端` 会在运行目录生成一个 `Config.ini` 用于保存配置项。

## 功能  

目前，该系统支持了以下功能：

### Web端
- 站长 `头像` 、 `昵称`显示
- 站长 `在线状态` 判断&显示
- 站长 `在线设备列表` 展示
- 站长 `设备前端窗口名称` 展示

### 客户端
- 上报时的 `设备名称` 修改
- 上报 `频率时间` 修改
- `开机自动启动` 、 `静默启动` 设置
- `关机` 、 `闲置` 时自动判断

##Todo List
[x]支持更改设备名称
[x]支持关机自动判断
[x]支持闲置自动判断
[]支持数据加密传输
[]支持更换自定义端口
[]服务器端支持自定义头像、昵称
[]支持自定义客户端名称

##下载
前往[Release](https://github.com/Rise-forever/RStatus/releases)页面进行下载。

## 编译

该软件采用易语言编写，如果你想要编译该软件，请准备以下环境：

- Windows 7 和以上版本的电脑
- 易语言 v5.93 或更高版本

同时，该软件引用了 [精易模块](https://ec.125.la/)，请在编辑 / 引用代码时遵守相关协议。

## 文档

[文档](https://gytxtx.github.io/Docs/#/docs/KFACBT_Toolkit/)

## 协议

本软件采用 **Apache License 2.0** 协议，在分发、修改软件时 **必须要标注** 源码来源和原作者，并且在相关的文件或页面中保留原许可证的版权声明和免责声明。此外，你可以选择修改并分发该软件的修改版本，但无需开源你的修改，只需在分发时附上适用的 **Apache License 2.0** 协议副本。

## 其它
 - [易语言官网](https://dywt.com.cn/)
 - [Apache License v2](https://www.apache.org/licenses/LICENSE-2.0)
