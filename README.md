### Домашние задания по MLOps

Добавлено:

- **uv** - менеджер пакетов и виртуальных окружений для Python
- **ruff** - линтер (анализатор) и форматтер Python-кода (проверяет стиль и ошибки, умеет автоисправлять)
- **ty** - быстрый статический анализатор типов для Python (проверка аннотаций типов)

## Запуск и проверки
Запуск скрипта:
```bash
uv run .\main.py
```

Проверка форматирования (без изменений):
```bash
uv run ruff format --check .\main.py
```
Автоформатирование:
```bash
uv run ruff format .\main.py
```
Статическая проверка типов:
```bash
uv run ty check --error all
```
Добавление новой ветки:
```bash
git switch --create название
```
Текстовая схема истории коммитов всех веток репозитория:
```bash
git log --graph --oneline --all --decorate
```

## Git LFS
Инициализация LFS в репозитории (один раз):
```bash
git lfs install
```

Отслеживание .bin файлов:
```bash
git lfs track "*.bin"
```

Добавить правило в коммит:
```bash
git add .gitattributes
git commit -m "chore: configure git lfs for .bin files"
```

Добавить и закоммитить сам файл, чтобы он попал под LFS:
```bash
git add model.bin
git commit -m "feat: add model.bin via git lfs"
```

Проверка, какие файлы под LFS:
```bash
git lfs ls-files
```

## Синхронизация с GitHub
Подтянуть изменения из удалённой ветки `main` и переставить свои коммиты поверх:
```bash
git pull --rebase origin main
```

## Podman (Windows)

Podman используется для запуска контейнеров (например, S3-совместимого хранилища для DVC).
На Windows Podman работает через виртуальную машину WSL2.

Необходимо установить WSL2:
```bash
wsl --install
```

Создание и запуск виртуальной машины
```bash
podman machine init
podman machine start
```

Проверка статуса:
```bash
podman machine ls
```

Создание тома:
```bash
podman volume create s3data
```

Проверка:
```bash
podman volume ls
```

## DVC
DVC используется для версионирования больших файлов (моделей, датасетов) отдельно от Git.
### Установка
```bash
uv tool install "dvc[s3]"
```
[s3] — дополнительная зависимость для работы с S3-совместимым хранилищем (например, MinIO).

Проверка установки:
```bash
dvc doctor
```
Инициализация DVC в проекте
```bash
dvc init
```

## Данные и DVC-пайплайн
Генерация тестового файла с числами от 1 до 1000 (PowerShell):
```bash
$lines = 1..1000
[IO.File]::WriteAllLines("$PWD\data\raw.csv", $lines, (New-Object System.Text.UTF8Encoding $False))
```


Добавление файла под управление DVC:
```bash
dvc add .\data\raw.csv
```

Коммит указателя DVC в Git (сам CSV в Git не попадает - он в .gitignore):
```bash
git add 'data\raw.csv.dvc' 'data\.gitignore'
git commit -m "feat: add raw data via dvc"
```

### Параметры пайплайна
Создание params.json:
```bash
$json = '{"prepare":{"min_value":100},"split":{"test_ratio":0.2}}'
[IO.File]::WriteAllText("$PWD\params.json", $json, (New-Object System.Text.UTF8Encoding $False))
```

### S3-хранилище для DVC (RustFS в Podman)
Запуск S3-совместимого хранилища:
```bash
podman run -d --name s3 -p 9000:9000 -p 9001:9001 -v s3data:/data -e RUSTFS_ACCESS_KEY=admin -e RUSTFS_SECRET_KEY=admin12345 -e RUSTFS_CONSOLE_ENABLE=true --restart=always docker.io/rustfs/rustfs:latest
```

Настройка remote в DVC:
```bash
dvc remote add -d storage s3://test-bucket/dvc
dvc remote modify storage endpointurl http://localhost:9000
```

Учётные данные (в текущей сессии PowerShell):
```bash
$env:AWS_ACCESS_KEY_ID="admin"
$env:AWS_SECRET_ACCESS_KEY="admin12345"
```

Загрузка и скачивание данных:
```bash
dvc push
dvc pull
```

### Управление контейнером S3
Остановка контейнера (данные в томе `s3data` сохраняются):
```bash
podman stop s3
```

Запуск контейнера:
```bash
podman start s3
```

### Стадии пайплайна
```bash
dvc stage add -n prepare `
  -d .\src\prepare.py -d .\data\raw.csv `
  -p params.json:prepare.min_value `
  -o .\data\clean.csv `
  uv run python .\src\prepare.py

dvc stage add -n split `
  -d .\src\split.py -d .\data\clean.csv `
  -p params.json:split.test_ratio `
  -o .\data\train.csv -o .\data\test.csv `
  uv run python .\src\split.py

dvc stage add -n train `
  -d .\src\train.py -d .\data\train.csv `
  -o .\model.json `
  uv run python .\src\train.py

dvc stage add -n evaluate `
  -d .\src\evaluate.py -d .\model.json -d .\data\test.csv `
  -M metrics.json `
  uv run python .\src\evaluate.py
```


### Запуск и просмотр пайплайна
```bash
dvc dag
dvc dag --outs
dvc repro
```