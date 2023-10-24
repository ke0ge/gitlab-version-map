# gitlab-version-map
Gitlab 静态文件 hash 与版本之间的映射仓库，用于判断 Gitlab 版本。

## 原理
Gitlab 中存在形如 `/assets/application-a0c92bafde7d93e87af3bc2797125cba613018240a9f5305ff949be8a1b16528.css` 的静态文件，其 hash 可作为特征用于判断版本。通过制作每个版本与 hash 的映射表，即可从 hash 反推出版本。  

注意，经测试发现，大版本（如 13.7，13.6）之间 hash 通常都不相同，但小版本（如 13.7.3，13.7.4）之间会存在 hash 相同的情况。尽管如此，该仓库也可用于尽可能确定目标 Gitlab 版本。  

## Github Action
通过 Github Action 监控 Gitlab docker hub 更新情况，并自动 commit 新版本 hash。  

## 获取目标版本 hash
手动修改 `get_target_hashes.py` 中的 `MIN_VUL_VERSION` `MAX_VUL_VERSION`，获取指定版本内的 hash 值。注意 `if LooseVersion(min_vul_version) <= LooseVersion(version) < LooseVersion(max_vul_version):` 中的等于符号。  


