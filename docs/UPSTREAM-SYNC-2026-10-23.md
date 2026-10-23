# Синхронизация upstream — 23 октября 2026

## Состояние

- Исходный форк и origin/master: `03a0dc53c9541e7c48e3705c758dbf27bdc761aa`.
- Интегрированы все 16 коммитов после `b44b71cf` до `21c488b6ce80159484015dfd0f58ef7748a24f6c` включительно.
- Локальная резервная ветка: `codex/before-upstream-sync-2026-10-23-03a0dc53`.
- Merge: `ae5d9cec`. Отдельное исправление нового upstream-теста ACL: `52535902`.
- История upstream сохранена; squash, force push, публикация, теги и запуск Actions не выполнялись.

## Принятые изменения

| Коммит | Назначение |
|---|---|
| `2016f48d` | Клавиатурная навигация и поиск в файловом менеджере desktop |
| `ce54e33c` | Ограничение ожидания QSV, буферы кодирования, безопаснее завершение hybrid MP4 |
| `4e93a41e` | Бюджеты обновления статичного изображения MediaCodec |
| `bd926239` | Точное сопоставление имени выхода xrandr |
| `f010d33c` | Android wheel; ранее перенесённый обработчик согласован, шаг уменьшен до 90 px |
| `2b6fedfc` | Защищённые файлы установщика, handoff перед UAC, нативное управление службой |
| `d97351ad` | Порт reverse proxy WebSocket только для настроенных собственных серверов |
| `3ec04164` | Повтор ввода пароля sudo-rs и отсутствие ложной начальной ошибки |
| `828d1101` | Обновление hwcodec с исправлениями GPU и восстановимости MP4 |
| `398364fa` | Совместное воспроизведение звука с другими приложениями iOS |
| `eb6c32bd` | Турецкие переводы |
| `25d27422` | Определение казахского и грузинского языка по locale |
| `f7b0af78` | Традиционный китайский для Hong Kong, Macao и Hant |
| `106f700b` | Учет Debian GDM daemon.conf |
| `01e1323e` | Список разрешений не обрывается на interlaced-режиме |
| `21c488b6` | Распознавание greeter по известным путям false/nologin в поле shell |

## Адаптации форка

- В `build.rs` объединены новые C++17/Sciter-настройки и прежнее отдельное имя `rustdesk_windows` для Win7. Иначе собственная библиотека могла бы затенить Windows import library.
- Сохранены экранирование имени пользователя в `getent passwd`, кэш xrandr и прежние Linux-защиты. Новый шаблон interlaced используется самим кэшем; upstream-тест проверяет этот реальный путь.
- Сохранены существующие тесты локализации и проверки выбранного пользователем языка.
- `libs/scrap/Cargo.toml` явно закрепляет `hwcodec` на `ec38ebaf2454269d4c5668a57e3813c6e5541be7`. Cargo.lock обновлён штатным Cargo; сопутствующая нормализация рёбер Windows-зависимостей просмотрена, массового обновления пакетов нет.
- Диапазон hwcodec от `febec27e` до `ec38ebaf` содержит 19 коммитов; просмотрен совокупный diff GPU/AMF, декодирования, MP4 и тестов. Включены связанные патчи FFmpeg 0013–0015.
- `hbb_common`: `5d52530b` → `edefa08b`. Точный диапазон включает настройку websocket-port, ограничение её собственными серверами, throttled warning и снижение шума smithay-логов. Рабочая папка submodule чистая.
- Signing/release workflows, ключи обновлений, `.cargo/config.toml`, Windows CMake, custom-server parser, защиты file transfer и Flutter lockfile не изменены.

## Найденная ошибка upstream-теста

`staged_files_protect_contents_and_remove_unverified_data` падал на `allowed.as_bool()`: при повышенных правах владельцем созданного файла могла стать группа Administrators, тогда как AccessCheck выполнялся с отключённой группой. В обычной песочнице явное отключение отсутствующей группы дополнительно давало ERROR_INVALID_PARAMETER.

Исправлена только подготовка тестов: ограниченный токен создаётся через LUA_TOKEN, проверяемый файл создаётся при impersonation того же обычного пользователя. Возврат к исходному токену выполняется до проверки результата создания. Производственный код создания, DACL, проверки SHA-256 и удаления защищённых файлов не изменён. Исходное падение и успешный повтор сохранены в локальных логах.

## Выполненные проверки

| Проверка | Результат |
|---|---|
| Полный Flutter test, SDK 3.24.5 | 211 passed, один ранее существовавший skipped |
| Flutter analyze, политика CI | 0 errors, 0 warnings; 327 infos |
| Проверка силы тестов навигации | Инверсия направления обнаружена двумя тестами; код восстановлен, 4/4 снова passed |
| `cargo test --locked -p base --lib` | 26 passed, 3 ignored |
| Отдельный запуск трёх ignored-тестов base | 3 passed: ссылки назначения, staging и выход через symlink |
| `hbb_common` test_check_ws | 1 passed: новые собственные порты, чужие хосты, IP-совместимость |
| Изолированные installer/hash Rust-тесты | 8 passed после исправления fixture; первоначально 7 passed / 1 failed |
| Парсер xrandr и кэш | 2 upstream-теста passed на извлечённой без изменения логики реализации |
| Обработчик службы C++ | MSVC C++17, WINVER/_WIN32_WINNT=0x0601; четыре проверки отказа на неверных аргументах passed, службы не создавались |
| Android wheel | Kotlin-компиляция фактического onMouseInput со stub Android API: направления, шаг 90, zero/horizontal, legacy и верхняя граница passed |
| CI contracts / TLS guard / Win7 checker | 10 / 2 / 4 passed; guard также выполнен отдельно |
| Actionlint | passed, без интеграций ShellCheck/Pyflakes |
| Rustfmt 1.88 | Все изменённые Rust-файлы проверены; исправлен формат upstream vec для прохождения проверки |
| Cargo metadata | --locked --offline --no-deps passed; не является линковкой приложения |
| Cargo audit | 0 неисключённых уязвимостей; 24 unmaintained и 3 unsound предупреждения остаются |

RustSec DB: `f7b2f6b`. Аудит запускался после успешного fail-closed guard с существующим точечным исключением RUSTSEC-2026-0381 для проверенной re-export-обёртки. Новых исключений нет. Новое advisory Tokio 1.54.0 не затрагивает закреплённую зависимость форка.

Логи: игнорируемый `target/integration-tools/sync-2026-10-23-*`. Изолированные проверочные проекты и бинарники не входят в коммиты. Они проверяют выбранные реальные модули/функции, но не заменяют сборку и запуск всего RustDesk. `git diff --check` пройден для исходников; строки контекста с одним пробелом внутри upstream `.patch` сохранены как часть unified diff.

## Регрессионная поверхность

| Существующие файлы | Изменённый путь выполнения |
|---|---|
| `build.rs`, `src/main.rs`, `src/platform/windows.cc`, `flutter/windows/runner/main.cpp` | Компиляция и ранняя обработка service-control; Win7-имя библиотеки сохранено |
| `src/platform/windows.rs`, `src/ui_interface.rs` | Установка/удаление, запуск службы, передача и отображение ошибок установки |
| `src/platform/windows/installer_handoff.rs`, `installer_handoff/directory.rs`, `installer_shell.rs`, `verified_update.rs` | Подготовка защищённых данных, передача elevated cmd, ярлыки, проверенные EXE/MSI-обновления; новые installer_files/gate принадлежат этому пути |
| `flutter/lib/desktop/pages/file_manager_page.dart`, `flutter/lib/desktop/widgets/list_search_action_listener.dart` | Только клавиатура и поиск файлового менеджера; протокол передачи не менялся |
| `flutter/android/app/src/main/kotlin/com/carriez/flutter_hbb/InputService.kt` | Только обработка wheel типа 3; legacy-маски сохранены |
| `flutter/ios/Runner/AppDelegate.swift` | Начальная настройка аудиосессии iOS |
| `src/platform/linux.rs`, `src/platform/gtk_sudo.rs` | GDM/prelogin, выбор выхода/разрешения xrandr, диалог sudo |
| `src/server/video_service/static_refresh.rs` | Повторное кодирование статичных кадров и бюджет при смене качества |
| `libs/scrap/Cargo.toml`, `Cargo.lock`, `res/vcpkg/ffmpeg/portfile.cmake` | Закреплённая реализация GPU-кодеков и связанные FFmpeg-патчи |
| `libs/hbb_common`, `libs/base/src/config/keys.rs` | Собственные WebSocket proxy-порты, список сохраняемых настроек и фильтрация логов; без настройки остаётся прежний порт |
| `src/lang.rs`, `src/lang/tr.rs` | Выбор локали и турецкие переводы |

Эти изменения соответствуют выбранным upstream-исправлениям. Новые общие интерфейсы, состояния или рефакторинг сверх upstream не добавлялись.

## Ограничения и следующий шаг

Не выполнены полная нативная сборка RustDesk/FFmpeg, сборка APK/MSI, реальный UAC, жизненный цикл SCM-службы, Bitdefender, Windows 7 на устройстве, MediaCodec/GPU, iOS audio и Linux X11/GDM/sudo. Для полной сборки локально отсутствует в том числе vcpkg vpx.lib. Кодек, время восстановления качества после Режима 2 и аппаратная совместимость не объявляются проверенными.

Отправить обычным `git push origin master`, дождаться CI, Windows unsigned и Android unsigned. Отдельно запустить Win7 workflow и проверить установку/обновление/удаление на тестовом ПК. Signed workflows запускать отдельно при необходимости. Новый тег и force push для этой синхронизации не нужны.
