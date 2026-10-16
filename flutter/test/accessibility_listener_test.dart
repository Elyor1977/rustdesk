import 'package:flutter/gestures.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_hbb/common.dart';
import 'package:flutter_hbb/generated_bridge.dart';
import 'package:flutter_hbb/models/platform_model.dart';
import 'package:flutter_hbb/models/server_model.dart';
import 'package:flutter_test/flutter_test.dart';

class _Binding extends Fake implements RustdeskImpl {
  @override
  String translate(
          {required String name, required String locale, dynamic hint}) =>
      name;
  @override
  String mainGetLocalOption({required String key, dynamic hint}) => '';
  @override
  String getLocalFlutterOption({required String k, dynamic hint}) => '';
  @override
  bool isDisableAb({dynamic hint}) => false;
  @override
  bool isDisableAccount({dynamic hint}) => false;
  @override
  bool isDisableGroupPanel({dynamic hint}) => false;
  @override
  bool isCustomClient({dynamic hint}) => false;
  @override
  Future<void> mainSetOption(
      {required String key, required String value, dynamic hint}) async {}
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  setUpAll(() async {
    isTest = true;
    platformFFI.setBindingForTesting(_Binding());
    await initGlobalFFI();
    gFFI.serverModel.changeStatue('input', true);
  });

  testWidgets(
      'real size-one touches without an authorized client are not mirrored',
      (tester) async {
    final mirrored = <PointerEvent>[];
    void record(PointerEvent event) {
      if (event.pointer == 101) mirrored.add(event);
    }

    GestureBinding.instance.pointerRouter.addGlobalRoute(record);
    addTearDown(
        () => GestureBinding.instance.pointerRouter.removeGlobalRoute(record));
    await tester.pumpWidget(AccessibilityListener(
        child: Listener(
      behavior: HitTestBehavior.opaque,
      child: const SizedBox.expand(),
    )));
    final client =
        Client(1, false, false, false, 'peer', '1', false, false, false);
    gFFI.serverModel.clients.add(client);
    addTearDown(gFFI.serverModel.clients.clear);
    for (final disconnected in [false, true]) {
      client.authorized = disconnected;
      client.disconnected = disconnected;
      GestureBinding.instance.handlePointerEvent(const PointerDownEvent(
          pointer: 1, position: Offset(50, 50), size: 1));
      GestureBinding.instance.handlePointerEvent(
          const PointerUpEvent(pointer: 1, position: Offset(50, 50), size: 1));
    }
    expect(mirrored, isEmpty);
  });
}
