# 动态Web服务器

这是一个使用Flask框架创建的现代化动态Web服务器。

## 功能特点

- 实时时间显示
- 用户论坛系统
- 响应式设计
- 数据持久化存储
- 美观的Bootstrap 5界面

## 技术栈

- Python Flask
- Bootstrap 5
- HTML5 & CSS3
- JSON数据存储

## 安装说明

1. 确保已安装Python 3.7或更高版本
2. 安装依赖包：
   ```
   pip install -r requirements.txt
   ```

## 运行服务器

执行以下命令启动服务器：
```
python app.py
```

服务器将在 http://localhost:8000 上运行

## 可用路由

- `/` - 主页（显示当前时间和论坛）
- `/about` - 关于页面
- `/add_message` - 添加新留言（POST请求）

## 项目结构

```
.
├── app.py              # 主应用程序文件
├── requirements.txt    # 项目依赖
├── messages.json       # 留言数据存储
└── web/               # 模板文件夹
    ├── index.html     # 主页模板
    └── about.html     # 关于页面模板
```

## 数据持久化

所有留言数据都会保存在 `messages.json` 文件中，确保服务器重启后数据不会丢失。 