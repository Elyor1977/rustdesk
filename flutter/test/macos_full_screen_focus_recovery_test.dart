import 'package:flutter_hbb/desktop/pages/macos_full_screen_focus_recovery.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('only the latest focus recovery generation can be consumed', () {
    final recovery = MacOSFullScreenFocusRecovery();
    final stale = recovery.queue();
    final current = recovery.queue();

    expect(recovery.consume(stale), isFalse);
    expect(recovery.consume(current), isTrue);
    expect(recovery.pendingGeneration, isNull);
  });

  test('cancel invalidates pending focus recovery', () {
    final recovery = MacOSFullScreenFocusRecovery();
    final generation = recovery.queue();

    recovery.cancel();

    expect(recovery.isCurrent(generation), isFalse);
    expect(recovery.consume(generation), isFalse);
  });
}
