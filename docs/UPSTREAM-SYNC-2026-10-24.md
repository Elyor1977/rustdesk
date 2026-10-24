# Синхронизация upstream — 24 октября 2026

## Изменения

Исходный форк: `f9c98f9bc3a8d80666f2cfa9c3ac035428ddda38`. Merge `0b48176a` включает пять коммитов до `1297da6d186e58d9096be24072ae3998cdbbf8fe`:

- `4d37f00a`: состояние автоматического FPS теперь принадлежит соединению, сбрасывается при ручном изменении FPS и успешном входе; автоматическое сообщение отправляется непосредственно в stream. Возврат от custom к предустановленному качеству восстанавливает лимит 30 FPS. Добавлен upstream-тест `manual_fps_update_allows_the_same_automatic_limit_again`.
- `ed6a1acc`: кнопка веб-консоли в адресной книге для вошедшего пользователя с правом записи, вне legacy-режима; используется уже имеющийся url_launcher и существующий FFI.
- `c8a4e068`: Linux выбирает monitor текущего default sink, сохраняя прежний fallback при ошибке/отсутствии monitor и ограничивая частоту сообщений об ошибках.
- `8814503e`: pulsectl использует default source для входного аудио. Просмотрен точный диапазон из шести коммитов `aa34dde4..d2ec086b`: два файла, также обработка отсутствующих устройств, правильный mute source-output и ошибки создания property list.
- `1297da6d`: корейские переводы. Placeholders проверены по английским значениям в en.rs.

`rust-pulsectl` явно закреплён на `d2ec086b5770dce934a66956364d09df8cc9484c` в Cargo.toml. Cargo.lock обновлён штатным Cargo; в нём изменился только источник этой зависимости, остальные версии и источники сохранены.

Резервная локальная ветка: `codex/before-upstream-sync-2026-10-24-f9c98f9b`. Squash, переписывание истории, push, теги и запуски GitHub Actions не выполнялись.

## Проверки итогового дерева

| Проверка | Результат |
|---|---|
| Полный Flutter test, SDK 3.24.5 | 211 passed, один ранее существовавший skipped |
| Flutter analyze, политика CI | 0 errors / 0 warnings, 327 infos |
| Все Python-тесты .github/scripts | 20 passed, включая проверку Kotlin-дубликатов, CI, TLS и Win7 |
| TLS roots guard | passed; исключение не расширялось |
| Actionlint | passed, без ShellCheck/Pyflakes |
| cargo test --locked -p base --lib | 26 passed / 3 ignored |
| Отдельный запуск ignored-тестов base от Elyor | 3 passed; суммарно 29 тестов base |
| Rustfmt 1.88, изменённые Rust-файлы | passed |
| git diff --check | passed |
| cargo metadata --locked --offline --no-deps | passed; не является компиляцией приложения |
| Новый FPS-тест в настоящем приложении с --features flutter | **Не выполнен**: компиляция остановилась в build.rs magnum-opus из-за отсутствующего VCPKG_ROOT; локально нет C:/vcpkg |
| cargo audit со свежей базой | **Не пройден**: одна неисключённая запись crypto-bigint; дополнительно 24 unmaintained / 4 unsound предупреждения |

Никакие извлечённые копии FPS-функции не использовались как доказательство работоспособности приложения. Base-тесты подтверждают защиты передачи файлов, а не управление FPS. Полные Windows/Android/Linux сборки, открытие веб-консоли с реальным аккаунтом, Linux PulseAudio/PipeWire, Windows 7 на устройстве и восстановление качества после Режима 2 в этой работе не подтверждены. Flutter bridge codegen не запускался.

Логи сохранены локально в игнорируемом `target/integration-tools/sync-2026-10-24-*`.

## Новый блокер безопасности

База RustSec обновлена до `21d909e`. В ней появилась [RUSTSEC-2026-0387](https://github.com/rustsec/advisory-db/blob/21d909e/crates/crypto-bigint/RUSTSEC-2026-0387.md): timing variability в crypto-bigint, исправленные версии >=0.7.6. В форке остаётся 0.5.5; та же версия и checksum присутствовали до этой интеграции.

Цепочка Windows проверена штатным cargo tree:

`rustdesk → hbb_common → webrtc → webrtc-dtls → p256/p384 → elliptic-curve 0.13.8 → crypto-bigint 0.5.5`.

elliptic-curve 0.13.8 требует crypto-bigint 0.5. Поэтому простая замена номера или добавление 0.7.6 не устраняет старую зависимость. Нужна отдельная проверенная миграция криптографической цепочки либо совместимый security backport; фактическая эксплуатация side channel не воспроизводилась. Этот пакет не обновлялся в рамках согласованных пяти коммитов, audit-ignore не добавлен. Существующий guard перед исключением re-export-обёртки webpki-roots сохранён.

Новое предупреждение RUSTSEC-2026-0386 относится к Unix AsyncFd в закреплённом Tokio 1.44.2; требуется отдельная проверка и обновление вместе с security-пакетом. Полностью зелёный CI или готовность к выпуску **не заявляются**. Обычный CI с актуальной базой ожидаемо остановится на cargo audit.

## Минимизация и регрессионная поверхность

- `src/client.rs`, `src/client/io_loop.rs`, `src/ui_session_interface.rs`: только FPS-состояние соединения, порядок отправки и восстановление лимита; это необходимые изменения выбранного исправления. Сохранены проверки file-transfer и буфера обмена до входа.
- `src/platform/linux.rs`: только выбор monitor источника системного звука с прежним fallback. Кэш разрешений, shell quoting и предыдущие Linux-адаптации сохранены.
- `Cargo.toml`, `Cargo.lock`: только закреплённый pulsectl; его производственный путь ограничен Linux-аудио.
- `flutter/lib/common/widgets/peer_tab_page.dart`: только новая кнопка адресной книги; существующие UI-адаптации форка сохранены.
- `src/lang/ko.rs`: только принятые переводы.

Изменений в CI/signing workflows, .cargo/config.toml, Win7 CMake, Windows installer, custom-server parser, ключах/проверке обновлений, base/fs, Android InputService, pubspec/Flutter lockfile и submodule hbb_common нет. Новые общие интерфейсы, дополнительные состояния или посторонний рефакторинг сверх upstream не добавлялись.

## Дальше

Интеграция сохранена локально. До выпуска и ожидания зелёного CI требуется отдельно согласовать и устранить security-блокер; публикация сейчас не рекомендуется. После этого — обычный push, штатные CI и отдельные сборки ОС, затем проверки на реальных устройствах. Force push и новый тег для этой синхронизации не нужны.
