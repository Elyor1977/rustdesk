# Интеграция четырёх изменений upstream — 12 ноября 2026

Исходный форк: `a3a06c09`. Объединена история upstream до
`1ac53ccb1b28e62b726db3cbd6042110349c9c2a`. Четыре исходных коммита сохранены;
конфликтов объединения не было. Резервная локальная ветка:
`codex/backup-before-upstream-1ac53ccb-2026-11-12`.
Push и запуск GitHub Actions не выполнялись.
Проверенный merge-коммит исходников: `bf9b2bed`; после проверки добавлен только этот отчёт.

| Коммит | Изменение |
|---|---|
| `bec9853f` | Диски Windows сохраняются при сортировке файлов по размеру/типу; добавлен regression-тест. |
| `66992ab7` | Clipboard объявляет размер файла без отдельного запроса; корректно обрабатывает большие/пустые файлы и первый непустой файл для аудита; Rust size_t соответствует размеру указателя. |
| `e8677cb7` | Linux сохраняет состояние развёрнутого окна при сворачивании; добавлены Linux-тест и его запуск в полной проверочной сборке. |
| `1ac53ccb` | Пароль создаваемого macOS keychain согласован с последующей разблокировкой. Это не включает подпись в unsigned workflows. |

## Сохранённые настройки

По Git blob hashes и точному diff сохранены Cargo.toml/Cargo.lock, настройки
Win7 и его отдельный workflow, Flutter 3.24.5, Windows/Android signing,
release approval/concurrency, unsigned workflows, security fixes и подмодуль
hbb_common `fae47e024dd83cef6aaecde0aa7d11731df11649`.
В общем flutter-build.yml добавлены только шесть upstream-строк; macOS
15/15-intel и собственные проверки форка сохранены.

## Проверки

| Проверка | Результат |
|---|---|
| Drive sorting regression | До исправления SortBy.type возвращал пустой список; после исправления тест прошёл |
| Flutter full suite | 260 passed, 2 skipped на Windows |
| Flutter analyze | 0 errors, 0 warnings, 338 прежних info; exit 0 |
| Native clipboard C, x64 и x86 | До исправления по 5 ошибок; после по 18/18 успешных проверок |
| Win7 imports/subsystem нового native probe | Успешно; это статическая проверка, не запуск на Win7 |
| Python CI/Win7/TLS | 27 passed |
| actionlint / Bash / Rustfmt | Успешно; проверены 58 Bash run scripts и изменённый Rust-файл |
| Полные Windows Rust release tests | 446 passed, 3 штатных ignored QoS-теста; без дополнительных исключений |
| Clipboard crate tests | 2 passed; doctests также завершились успешно |
| Windows Rust release + Flutter bundle | Обе сборки успешны; Rust DLL в bundle совпадает с новой библиотекой по SHA256 |

Bundle: `flutter/build/windows/x64/runner/Release/`.
SHA256 `librustdesk.dll`:
`6AD4378672DE0AB76C99ABEE121649283C9C7C5870F420E5A050051388925D93`.
Компилятор основного Rust crate оставляет 14 предупреждений; они не подавлялись.

Native probe включает точный полный wf_cliprdr.c и header из исходного и
обновлённого Git-снимков. Проверены настоящие файлы размером 0, 17 и
4 ГиБ + 17 байт (sparse), каталог, выбор первого непустого файла и сброс
индекса при очистке списка. Системный clipboard не инициализировался и не
изменялся. Probe не подменяет тест полного Rust→C callback на x86.
Это локальное воспроизведение в target, а не новый набор тестов CI.

Логи, исходники probe, hashes и отчёты независимой проверки:
`target/integration-1ac53ccb-2026-11-12/` (не включается в Git).

## Регрессионная поверхность

- `flutter/lib/models/file_model.dart`: только включение дисков в два фильтра сортировки; собственные исправления файловых операций не менялись.
- `flutter/lib/desktop/widgets/tabbar_widget.dart`: Linux не сбрасывает maximized при minimize; ветка Windows/Win7 сохраняет прежнее поведение.
- `libs/clipboard/src/platform/windows.rs`: исправлен ABI типа size_t на 32-битной Windows; на x64 ширина остаётся 64 бита.
- `libs/clipboard/src/windows/wf_cliprdr.c`: метаданные размера, обработка ошибок получения атрибутов/размера и индекс первого непустого файла. Недоступный файл теперь отклоняется вместо ложного пустого файла/каталога.
- `.github/workflows/flutter-build.yml`: пароль keychain macOS и Flutter-тесты Linux x86_64 при upload-artifact=false. Остальные entry points и права сохранены.
- `flutter/test/file_model_test.dart`, `flutter/test/linux_window_restore_test.dart`: только тесты двух UI-исправлений.

## Границы проверки

Linux-only restore test пропущен на Windows и включён в существующий Ubuntu
Flutter CI. Настоящий GTK minimize/restore, Windows→Windows/Linux clipboard,
полный Rust x86 callback, запуск на Windows 7, Android и production-подпись
на этом компьютере не проверялись. Полной Win7-сборки этот прогон не заменяет.
Локальная Windows-сборка использует существующие SDK/caches и generated bridge;
кодогенератор не запускался. ShellCheck/Pyflakes отдельно не запускались.
Установленная программа, сеть, сертификаты, секреты и PktMon.etl не изменялись.
