# Dependency triage — 2026-10-05

## Исправлено

`Cargo update --offline --precise` обновил только `rand 0.8.5 → 0.8.6` и
`rand 0.9.2 → 0.9.3`, их checksum и ссылки потребителей. Обе версии исправляют
[RUSTSEC-2026-0097](https://rustsec.org/advisories/RUSTSEC-2026-0097.html).
Формат lockfile автоматически обновлён Cargo 1.88 с 3 до 4; CI использует
совместимые современные toolchain. API приложения и manifest не изменены.

Исключение: отключённые по умолчанию Sciter jobs с Rust 1.75 и
`ENABLE_LEGACY_SCITER` уже требуют отдельного старого dependency graph;
этот современный lockfile для них не предназначен. Windows 7 использует
nightly 2025-06-25, а не Rust 1.75. [Формат lockfile и совместимость Cargo](https://doc.rust-lang.org/cargo/CHANGELOG.html).

## Проверено

- SHA256 скачанных `.crate` совпадает с Cargo.lock.
- `cargo metadata --offline --locked --no-deps` прошёл.
- `cargo tree --offline -i atty` подтвердил build-only цепочку ниже.
- `cargo audit 0.22.0`, база RustSec `ef6173cbc5c50ec8166f9a5b28f07834144373ee`
  (2026-10-03): exit 0, 0 неисключённых vulnerability, 21 unmaintained,
  3 unsound. Два предупреждения rand устранены.
- Это не доказательство отсутствия неизвестных уязвимостей. Полная сборка и
  тесты Windows/Linux/Android здесь не выполнены. Online Cargo заблокирован
  локальной ошибкой Schannel; обновление использовало существующий index cache.

## Отложено: применимость и причина

Для всех строк следующая проверка — **2026-11-05 или перед ближайшим signed
release, что наступит раньше**. Не добавлены новые audit-ignore: предупреждения
остаются видимыми. Замена пакета требует отдельной совместимой миграции и CI.

| Пакет / advisory | Достижимость и решение |
|---|---|
| atty 0.2.14, RUSTSEC-2021-0145 / 2024-0375 | Windows, только bindgen 0.59.2 → clap 2.34 / env_logger 0.9.3 → atty в build-dependencies machine-uid и magnum-opus. Нет runtime-пути atty в исследованном Windows дереве. Условие unaligned-read связано с allocator; production global allocator не найден, test allocator делегирует System. Пересмотреть при обновлении bindgen/upstream зависимостей. |
| glib 0.18.5, RUSTSEC-2024-0429 | Linux GTK runtime. В src/libs не найдены вызовы VariantStrIter/str_iter; это не доказывает отсутствие транзитивного вызова в GTK. Патч требует glib ≥0.20 и согласованной миграции GTK/gio/gdk; не обновлять glib отдельно. Нужны Linux GTK/UAC integration tests. |
| users 0.11, RUSTSEC-2023-0059 / 2023-0040 | hbb_common лишь re-export users; его исходники не вызывают user/group API. Клиентские Linux lookup импортируют uzers 0.12.2 из Cargo manifests. Не обнаружен вызов уязвимого group-member API. Не менять shared submodule ради неиспользуемого dependency без upstream coordination. |
| users, RUSTSEC-2025-0040 | Существующее исключение .cargo/audit.toml сохранено только при отсутствии group-list API. При любом новом использовании users/groups проверить исключение заново; vulnerability не исчезла из самого старого пакета. |
| clipboard 0.1.0, RUSTSEC-2022-0056 | Совпадение имени с чужим crates.io clipboard: в lockfile это локальный workspace crate без registry source. Не свидетельствует об этой уязвимости в libs/clipboard. |
| sodiumoxide 0.2.7 | Реальные runtime crypto/signing вызовы в client/common/custom_server/hbb_common. Unmaintained не означает доказанный взлом. Замена требует совместимости протокола, ключей и криптографических test vectors; не заменять вслепую. |
| bincode 1.3.3 | Транзитивный runtime webrtc-dtls. Менять вместе с проверкой WebRTC wire/data compatibility, не принудительно на bincode 2. |
| ttf-parser 0.25.1 | Runtime whiteboard и fontdb/owned_ttf_parser. Проверить поддерживаемую замену и загрузку/рендеринг шрифтов; есть обработка внешнего font input, поэтому выше остальных maintenance-only миграций. |
| adler 1.0.2 | miniz_oxide 0.7.4: compression dependency; проверять decompression consumers и совместимое обновление miniz, не подменять adler вручную. |
| derivative 2.2, paste 1, proc-macro-error 1 | Макросы zbus / GTK / gstreamer / netlink / nokhwa; выполнение при сборке. Обновлять потребителей, не ломать их macro API. |
| ansi_term 0.12.1 | bindgen → clap 2: build-only исследованный Windows путь. Устраняется миграцией bindgen/clap, не влияет на runtime rendering. |
| dlopen_derive 0.1.4 | derive через dlopen 0.1.8; loader реально используется Flutter и virtual_display. Миграция должна проверить FFI symbol loading. |
| instant 0.1.13 | fastrand 1.9 / tao 0.25; platform UI/timing dependency. Обновлять родителей с GUI regression tests. |
| rand_os 0.1.3 | Старый rand 0.6.5, отдельная от исправленных rand 0.8/0.9 ветка. Maintenance-only; обновлять её непосредственного потребителя, не объединять несовместимые rand API. |
| serial 0.4.0 | portable-pty 0.8.1: terminal/PTY dependency. Нужны terminal spawn, resize и IO tests перед заменой. |
| unic-bidi / unic-char-property / unic-char-range / unic-common / unic-ucd-bidi / unic-ucd-version 0.9 | piet text/bidi stack, runtime UI rendering. Миграция совместно с piet; проверить RTL, смешанный текст и Unicode shaping. |

## Регрессионная поверхность

Существующий изменённый файл — только Cargo.lock. Изменённые runtime пути:
все потребители rand 0.8/0.9 используют patch-исправление RNG, включая common,
WebRTC, QUIC и WebSocket зависимости. Новых runtime зависимостей не добавлено.
Остальные maintenance/unsound проблемы не замаскированы массовыми исключениями.
