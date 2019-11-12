```
.
├── Dockerfile
├── README.md
├── docker-compose.yaml
└── work
    ├── deregister.py
    ├── reboot_register.py
    └── serverless.yaml
```
# What
Serverless Framework(in Docker)を利用して以下のlambdaファンクションをデプロイするやつ

- Cloudwatch Eventのcronを利用した特定時刻の処理
  - Target GroupからEC2を外す
  - EC2を再起動し、その後Target Groupへ登録

※ Serverless in Docker部分は汎用のため、Dockerfile及びdocker-compose.yamlは流用可
# Usage
## 1. set env
.envファイルを編集
AWS_PROFILE及び発火タイミング(cron)、その他リソース情報の環境変数を設定

## 2. docker build (only first)
```
$ docker-compose build

# 引数なしで実行するとバージョン情報
$ docker-compose run --rm sls
1.35.1

# slsに続けて引数をそのまま追加してコマンド実行
$ docker-compose run --rm sls help

Commands
* You can run commands with "serverless" or the shortcut "sls"
* Pass "--verbose" to this command to get in-depth plugin info
.
.
.
```
## 3. deploy
.env以外に変更箇所なし。そのままデプロイ
```
$ docker-compose run --rm sls deploy -v
```

## 4. remove
ロググループやiam含め、関連ファイルは全て消去される
```
$ docker-compose run --rm sls remove -v
.
.
.
Serverless: Stack removal finished...
```

# Tips
## 1. 変数の流れ
- 例：reboot_register.py内の変数 `TARGETGROUP_ARN`
  - <- TARGETGROUP_ARN = os.environ['TARGETGROUP_ARN'] としてLambda側設定の環境変数を参照
    - <- serverless.yaml 上、 `${env:TARGETGROUP_ARN}` としてdockerコンテナ内の環境変数を参照
      - <- docker-compose.yaml 上、コンテナ内の環境変数としてファイル: `.env` を参照
