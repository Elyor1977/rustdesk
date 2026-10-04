import 'dart:async';

import 'package:flutter_hbb/models/web_video_frame_queue.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('ending a session disposes an image imported by a stale generation',
      () async {
    final imported = Completer<String>();
    final closedFrames = <String>[];
    final disposedImages = <String>[];
    var delivered = false;
    final queue = WebVideoFrameQueue<String, String>(
      importFrame: (_) => imported.future,
      closeFrame: closedFrames.add,
      disposeImage: disposedImages.add,
      onImportError: (_, __) => fail('unexpected import error'),
      onCallbackError: (_, __) => fail('unexpected callback error'),
    );
    queue.beginSession((_, __, ___) async => delivered = true);

    expect(queue.submit(0, 'frame'), isTrue);
    await Future<void>.delayed(Duration.zero);
    queue.endSession();
    imported.complete('image');
    await Future<void>.delayed(Duration.zero);

    expect(closedFrames, ['frame']);
    expect(disposedImages, ['image']);
    expect(delivered, isFalse);
  });

  test('callback failure disposes the delivered image', () async {
    final callbackError = Completer<Object>();
    final disposedImages = <String>[];
    final queue = WebVideoFrameQueue<String, String>(
      importFrame: (_) async => 'image',
      closeFrame: (_) {},
      disposeImage: disposedImages.add,
      onImportError: (_, __) => fail('unexpected import error'),
      onCallbackError: (error, _) => callbackError.complete(error),
    );
    queue.beginSession((_, __, ___) async => throw StateError('closed'));

    expect(queue.submit(0, 'frame'), isTrue);
    await callbackError.future;

    expect(disposedImages, ['image']);
  });
}
