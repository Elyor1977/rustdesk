# Dependency triage — 2026-11-12

## Результат и границы проверки

После точечных обновлений зависимостей сохранённый результат
`target/fixes-2026-11-12/cargo-audit.json` содержит **0 неисключённых
vulnerabilities, 25 unmaintained, 3 unsound, 0 yanked**. В итоговом снимке
после закрепления default-net — 1031 пакет, 1458 advisories. Commit базы
`fd6f39814c4d3c359fdbe223d0280dec4933f78f` от 2026-11-11 подтверждён по
Git в `target/audit-2026-11-12/advisory-db`.
Исходный снимок `target/audit-2026-11-12/cargo-audit.json`: 0/25/4/3 соответственно.

Ноль vulnerabilities относится к действующей политике исключений, а не к
отсутствию уязвимых пакетов. Сохранены два прежних исключения: `users`
RUSTSEC-2025-0040 в `.cargo/audit.toml` и условное исключение
RUSTSEC-2026-0381 в CI после проверки TLS roots. Новых исключений нет.

Для применимости проверены текущие Cargo.lock/manifests, исходники приложения,
локальные исходники build-зависимостей и опубликованные исходники glib 0.18.5 /
users 0.11.0. SHA256 последних двух `.crate` проверен против Cargo.lock.
Обратные цепочки восстановлены из lockfile; тип зависимости и платформенные
ограничения подтверждены manifests. Это статический анализ достижимости,
не доказательство отсутствия всех транзитивных вызовов. Результаты сборки и
тестов всего пакета исправлений учитываются отдельно; Linux GUI и реальные
устройства этим документом не объявляются проверенными.

## Исправлено в зависимостях

| Обновление | Причина |
|---|---|
| rustix 1.1.2 → 1.1.6 | Устранён RUSTSEC-2026-0486: неверная обработка нулевого буфера в extended-attribute API могла приводить к UB. Ветки rustix 0.37/0.38 этим advisory не затронуты. Вместе разрешились bitflags 2.9.4 и linux-raw-sys 0.12.1. |
| crypto-bigint 0.7.7 → 0.7.11 | Убрана отозванная версия в криптографическом дереве. Совместимость vendored DTLS проверяется его тестами, а не одним результатом audit. |
| clipboard-win 5.4.0 → 5.4.3 | Убрана отозванная Windows-зависимость буфера обмена. |
| spin 0.9.8 → 0.9.9 | Убрана отозванная версия синхронизации. |

Классификация rustix — **informational unsound**, хотя последствие является
ошибкой безопасности памяти. [RUSTSEC-2026-0486](https://rustsec.org/advisories/RUSTSEC-2026-0486.html).
Отзыв версии (`yanked`) сам по себе не доказывает уязвимость: он исключает её
из нового разрешения зависимостей, но не блокирует существующий lockfile.
[Cargo: yank](https://doc.rust-lang.org/cargo/commands/cargo-yank.html).

## Vulnerabilities и существующие исключения

**users 0.11.0 — RUSTSEC-2025-0040.** Ошибка добавляет группу root к спискам
групп; использование такого результата для авторизации может повысить
привилегии. В проверенном RustDesk нет вызовов `get_user_groups` /
`group_access_list` через этот пакет. Linux-зависимость осталась только в
`hbb_common`; его исходники лишь реэкспортируют `users`. Реальные клиентские
lookup используют alias `users = { package = "uzers", version = "0.12.2" }`
в корневом Cargo.toml и `libs/base/Cargo.toml`. Поэтому существующее исключение
не расширено. Сам пакет остаётся уязвимым; перед новым group/authorization
API или изменением submodule эту оценку нужно повторить.
[RUSTSEC-2025-0040](https://rustsec.org/advisories/RUSTSEC-2025-0040.html).

**webpki-roots — RUSTSEC-2026-0381.** В текущем lockfile 0.26.11 только
реэкспортирует store 1.0.11, где удалён затронутый root. Перед условным
исключением CI запускает `.github/scripts/test_tls_roots.py` и
`check_tls_roots.py`: проверяются версия, registry source, checksum обёртки и
единственная ссылка на исправленный store ≥1.0.10. Ошибка проверки прекращает
job; исключение не разрешает старые самостоятельные trust stores.
[RUSTSEC-2026-0381](https://rustsec.org/advisories/RUSTSEC-2026-0381.html).

## Оставшиеся unsound advisories

### atty 0.2.14 — RUSTSEC-2021-0145

Точная цепочка: build-dependencies `machine-uid 0.3.0`, `magnum-opus 0.4.0`,
`hwcodec 0.8.0` → `bindgen 0.59.2` → `clap 2.34.0` / `env_logger 0.9.3` →
`atty 0.2.14`. Все три manifest действительно объявляют bindgen как
build-dependency. Clap/env_logger вызывают `atty::is` при определении
терминала/цветного вывода. Runtime-потребителя atty в проверенном дереве нет.

Ошибка Windows связана с выравниванием указателя при нестандартном allocator;
системный Windows allocator предоставляет требуемое выравнивание. В production
RustDesk не найден собственный global allocator; тестовый CountingAllocator
делегирует System и не используется исполняемыми build scripts. Это снижает
практическую применимость, но не исправляет пакет.
[RUSTSEC-2021-0145](https://rustsec.org/advisories/RUSTSEC-2021-0145.html).

Решение: оставить предупреждение видимым; обновлять bindgen через его трёх
потребителей отдельным совместимым изменением с проверкой generated C bindings.
Не подменять clap major-версию и не добавлять audit-ignore.

### glib 0.18.5 — RUSTSEC-2024-0429

Linux runtime: `rustdesk → gtk 0.18.1 → glib 0.18.5`; дополнительные пути идут
через tao/GTK и tray-icon/libappindicator. Старый glib 0.10.3 в GStreamer-ветке
находится вне затронутого диапазона 0.15–0.19.

Опасный путь — `Variant::array_iter_str()` → `VariantStrIter::{next,next_back,
nth,nth_back,last}` → `impl_get`. В glib 0.18.5 `variant_iter.rs:118–130`
передаёт `&p` изменяющей его C-функции; оптимизированная сборка может упасть
на NULL. Исправленные выпуски: ≥0.20.
[RUSTSEC-2024-0429](https://rustsec.org/advisories/RUSTSEC-2024-0429.html).

В `src/` и `libs/` нет `array_iter_str`, `str_iter` или `VariantStrIter`.
Важное отличие: GNOME-layout reader
`src/server/uinput/layout/source.rs:168` вызывает `Settings::value().get()`.
`FromVariant for Vec<T>` в glib 0.18.5 (`variant.rs:1374–1390`) использует
`child_value(i).get()`, а String использует `Variant::str()`; этот проверенный
путь не проходит через опасный iterator. GTK sudo использует widgets,
сигналы и timeout, IBus — отдельный dbus crate и `glib::user_config_dir()`.

Ограничение: отсутствие прямого вызова не исключает вызов внутри всего GTK
стека. Предупреждение остаётся. Устранение требует отдельного согласованного
обновления GUI-зависимостей либо проверенного backport исправления в
контролируемую ветку; простое добавление glib 0.20 не заменит glib 0.18,
который требует GTK 0.18. Перед такой миграцией нужны Linux release-тесты
tray, GTK elevation и GNOME layout. Массовая миграция здесь не выполнялась.

### users 0.11.0 — RUSTSEC-2023-0059

Цепочка только `rustdesk/workspace → hbb_common → users 0.11.0` на Linux.
`libs/hbb_common/src/lib.rs:72` реэкспортирует пакет; вызовов его API в
исследованном submodule нет. Опасная функция `users::base::members`
(`base.rs:291–305`) разыменовывает указатели списка членов группы;
`get_group_by_gid` и преобразование group могут приводить к panic/abort или UB.
[RUSTSEC-2023-0059](https://rustsec.org/advisories/RUSTSEC-2023-0059.html),
[исходный reproducer](https://github.com/ogham/rust-users/issues/55).

Используемые здесь `src/platform/linux.rs:1494` (`get_user_by_name`) и
`libs/base/src/platform/linux.rs:494–495` (`get_current_uid`, `get_user_by_uid`)
разрешаются в **uzers 0.12.2**, а не в users 0.11.0. Не следует считать
совпадение Rust import `users::` доказательством вызова старого пакета.
Решение: сохранить предупреждение; удалять users или заменять его alias
в shared hbb_common согласованно с сервером, без скрытого локального patch
submodule и без нового исключения.

## Unmaintained: отдельный долг сопровождения

25 уведомлений не равны 25 доказанным runtime-уязвимостям. Для дальнейшей
работы пакеты сгруппированы по потребителям:

| Группа | Что проверить перед заменой |
|---|---|
| atty, ansi_term | Описанная выше build-only ветка bindgen/clap. |
| users | Описанная выше неиспользуемая клиентом зависимость hbb_common. |
| sodiumoxide | Реальная криптография hbb_common: совместимость протокола, ключей и test vectors. |
| bincode | Vendored webrtc-dtls 0.12.0: сериализация и DTLS tests, без принудительного bincode 2. |
| ttf-parser; unic-bidi, unic-char-property, unic-char-range, unic-common, unic-ucd-bidi, unic-ucd-version | fontdb/owned_ttf_parser/whiteboard и piet: внешние шрифты, Unicode/RTL и рендеринг. |
| zbus_names, zvariant, zvariant_derive | Ветка zbus 3.15.2: Linux D-Bus consumers; согласованная миграция типов и сериализации. |
| serial | portable-pty 0.8.1: запуск терминала, resize и I/O. |
| dlopen_derive | dlopen 0.1.8: загрузка FFI-символов Flutter/virtual display. |
| derivative, paste, proc-macro-error | Build macros; обновлять потребителей вместе с проверкой generated API. |
| adler | miniz_oxide 0.7.4: обновлять compression consumer, проверить чтение существующих данных. |
| instant, rand_os, pin-utils | tao/fastrand; rand 0.6.5; futures-util/hyper/nix. Обновлять родителей совместимыми версиями. |
| clipboard 0.1.0 | Совпадение имени с advisory crates.io RUSTSEC-2022-0056. В lockfile это собственный workspace `libs/clipboard` без registry source; уведомление о сопровождении чужого crate не устанавливает проблему нашего кода. |

Приоритет следующего этапа: поддерживаемое решение для Linux GTK/glib,
согласованное удаление старого users, затем build bindgen и runtime-пакеты
с внешним вводом (шрифты/сериализация/криптография). Остальные maintenance-only
миграции выполнять отдельно с проверками соответствующих функций.
Повторить triage перед ближайшим signed release и после любого изменения
этих цепочек. Известные ограничения не маскировать audit-ignore.

## Регрессионная поверхность документа

Этот документ не меняет исполняемый код, manifests, lockfile или audit policy.
Он фиксирует применимость предупреждений; точечные обновления и их тесты
оформлены отдельными изменениями. Runtime-тесты Linux, полнота транзитивной
достижимости и отсутствие ещё неизвестных advisories остаются за границей
приведённых доказательств.
