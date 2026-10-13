# Подписанные обновления форка

Windows PFX и Android-keystore остаются прежними. Для проверки метаданных
обновлений нужен отдельный ключ Ed25519. Ключ оригинального проекта не используется.

Без нового ключа сборки работают, но встроенная проверка обновлений отключена.
Пакеты можно скачать из Actions и установить вручную.

## Создание ключа на своём компьютере

В PowerShell выполните по отдельности:

```powershell
python -m pip install cryptography==50.0.0
```

```powershell
$updateKeyDir = Join-Path $env:LOCALAPPDATA 'RustDeskSigning'
New-Item -ItemType Directory -Path $updateKeyDir -Force
icacls $updateKeyDir /inheritance:r /grant:r "$($env:USERNAME):(OI)(CI)F"
```

```powershell
python -c "import os,base64; from pathlib import Path; from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey; from cryptography.hazmat.primitives.serialization import Encoding,PrivateFormat,PublicFormat,NoEncryption; d=Path(os.environ['LOCALAPPDATA'])/'RustDeskSigning'; k=Ed25519PrivateKey.generate(); seed=k.private_bytes(Encoding.Raw,PrivateFormat.Raw,NoEncryption()); public=k.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw); (d/'update-seed.txt').open('x').write(base64.b64encode(seed).decode()); (d/'update-public.txt').open('x').write(base64.b64encode(public).decode())"
```

Если файлы уже существуют, команда откажется их перезаписывать. Сохраните
резервную копию приватного ключа в защищённом месте. Не присылайте его в чат
и не добавляйте в Git. Не меняйте ключ для каждой сборки.

## Настройка GitHub

В `Elyor1977/rustdesk` откройте **Settings → Secrets and variables → Actions**.

1. **Secrets → New repository secret**:
   имя `RUSTDESK_UPDATE_ED25519_SEED`, значение — содержимое `update-seed.txt`.
2. **Variables → New repository variable**:
   имя `RUSTDESK_UPDATE_ED25519_PUBLIC_KEY`, значение — содержимое `update-public.txt`.
3. **Variables → New repository variable**:
   имя `ENABLE_SIGNED_UPDATE_METADATA`, значение `true`.

Не создавайте одноимённые переопределения в Environment: сборка и публикация
должны получать один и тот же публичный ключ из Repository Variables.

Публичный ключ встраивается при компиляции. Пересоберите клиент после настройки:
уже выпущенный клиент без ключа не получит его из GitHub автоматически.
Необходимые Windows/Android-секреты и подтверждение Environment `release`
настраиваются отдельно по [SIGNING.md](SIGNING.md).

## Выпуск

Создайте новый тег, совпадающий с версией в `Cargo.toml`, например `v1.5.1`.
Запустится **Signed release**. После проверок подтвердите Environment `release`.
При включённой настройке workflow проверит пару ключей до сборки, затем создаст
и проверит `rustdesk-update.json` и `rustdesk-update.json.sig` для Windows x64
EXE/MSI. Эти файлы публикуются вместе с пакетами.

Не заменяйте пакеты уже подписанного выпуска: workflow откажется повторно
публиковать такой тег. Для исправлений нужна новая версия и новый тег.

Встроенный обновлятор принимает только выпуски `Elyor1977/rustdesk` и этот ключ.
Он проверяет подпись метаданных, размер и SHA-256 пакета перед установкой.
При отсутствии или неправильной подписи обновление не устанавливается.

## Ограничения

- Отдельные **Windows signed/unsigned** создают артефакты Actions, а не
  опубликованный выпуск с метаданными. Их следует устанавливать вручную.
- Windows 7-сборки не используют встроенный обновлятор: общий выпуск содержит
  Windows 10+ пакеты. Windows 7 обновляйте отдельной совместимой сборкой вручную.
- Автообновление Android этим механизмом не добавлено; APK устанавливается вручную.
- Публикация метаданных Windows ARM64/macOS в форке пока не настроена.
- При смене ключа старые клиенты перестанут доверять новым обновлениям.
