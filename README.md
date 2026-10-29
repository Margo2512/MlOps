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