import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_hbb/common.dart';
import 'package:flutter_hbb/desktop/pages/connection_page.dart';
import 'package:flutter_hbb/generated_bridge.dart';
import 'package:flutter_hbb/models/platform_model.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';

class _Binding extends Fake implements RustdeskImpl {
  final requests = <Completer<String>>[];

  @override
  Future<String> mainGetConnectStatus({dynamic hint}) {
    final request = Completer<String>();
    requests.add(request);
    return request.future;
  }

  @override
  bool isIncomingOnly({dynamic hint}) => true;
  @override
  String translate(
          {required String name, required String locale, dynamic hint}) =>
      name;
  @override
  String mainGetLocalOption({required String key, dynamic hint}) => '';
}

void main() {
  testWidgets('slow connection status refresh does not overlap',
      (tester) async {
    isTest = true;
    final binding = _Binding();
    platformFFI.setBindingForTesting(binding);
    Get.put<RxBool>(false.obs, tag: 'stop-service');
    addTearDown(() => Get.delete<RxBool>(tag: 'stop-service'));
    await tester.pumpWidget(
        const MaterialApp(home: Scaffold(body: OnlineStatusWidget())));
    await tester.pump(const Duration(milliseconds: 1));
    expect(binding.requests.length, 1);

    await tester.pump(const Duration(seconds: 1));
    await tester.pumpWidget(const SizedBox());

    expect(binding.requests.length, 1,
        reason: 'The previous status request has not completed');
  });
}
