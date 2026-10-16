// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'dart:ui';
import 'package:flutter_test/flutter_test.dart';
import 'package:eurospot/main.dart';
import 'package:eurospot/database_service.dart';
import 'package:eurospot/assistant_engine.dart';

void main() {
  testWidgets('EuroSpot smoke test ve Coklu Dil / Magaza Haritasi Tab Testi', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());

    expect(find.text('EuroSpot'), findsOneWidget);
    expect(find.text('Fırsatlar'), findsOneWidget);
    expect(find.text('Sepet & Tasarruf'), findsOneWidget);
    expect(find.text('Mağaza Haritası'), findsOneWidget);
    expect(find.text('Asistan'), findsOneWidget);
  });

  testWidgets('Farkli Android Modelleri ve Ekran Boyutlari Testi', (WidgetTester tester) async {
    // 1. Kucuk Ekran: Bütçe Dostu Android (Samsung Galaxy A03 / Xiaomi Redmi 9A - 720x1600 @ 2.0x -> 360x800 dp)
    tester.view.physicalSize = const Size(720, 1600);
    tester.view.devicePixelRatio = 2.0;
    await tester.pumpWidget(const MyApp());
    await tester.pumpAndSettle();
    expect(find.text('EuroSpot'), findsOneWidget);
    expect(tester.takeException(), isNull); // Taşıntı (overflow) hatası yok

    // 2. Standart Orta Segment Android (Samsung Galaxy A54 / Xiaomi Redmi Note 12 - 1080x2400 @ 2.75x -> 392x872 dp)
    tester.view.physicalSize = const Size(1080, 2400);
    tester.view.devicePixelRatio = 2.75;
    await tester.pumpWidget(const MyApp());
    await tester.pumpAndSettle();
    expect(find.text('EuroSpot'), findsOneWidget);
    expect(tester.takeException(), isNull);

    // 3. Amiral Gemisi Android (Samsung Galaxy S23 Ultra / S24 Ultra - 1440x3088 @ 3.5x -> 411x882 dp)
    tester.view.physicalSize = const Size(1440, 3088);
    tester.view.devicePixelRatio = 3.5;
    await tester.pumpWidget(const MyApp());
    await tester.pumpAndSettle();
    expect(find.text('EuroSpot'), findsOneWidget);
    expect(tester.takeException(), isNull);

    // 4. Saf Android ve Google Cihazı (Google Pixel 7 / Pixel 8 - 1080x2400 @ 2.625x -> 411x914 dp)
    tester.view.physicalSize = const Size(1080, 2400);
    tester.view.devicePixelRatio = 2.625;
    await tester.pumpWidget(const MyApp());
    await tester.pumpAndSettle();
    expect(find.text('EuroSpot'), findsOneWidget);
    expect(tester.takeException(), isNull);

    // Gorunumu sifirla
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });
  });

  test('EuroSpot 100 Urun Cok Ulkeli ve Cok Magzali Test Simulasyonu', () {
    final storesByCountry = {
      'Almanya': ['Lidl DE', 'Aldi Süd DE', 'Rewe DE', 'Edeka DE', 'Kaufland DE', 'Penny DE'],
      'Fransa': ['Carrefour FR', 'Auchan FR', 'E.Leclerc FR', 'Intermarché FR', 'Monoprix FR'],
      'Hollanda': ['Albert Heijn NL', 'Jumbo NL', 'Plus NL', 'Dirk NL'],
      'Avusturya': ['Spar AT', 'Billa AT', 'Hofer AT'],
      'Belçika': ['Colruyt BE', 'Delhaize BE'],
    };

    final sampleTemplates = [
      {'name': 'Bio Vollmilch 3.8%', 'unit': '1L', 'orig': 1.49, 'disc': 0.99},
      {'name': 'Fettarme Milch 1.5%', 'unit': '1L', 'orig': 1.35, 'disc': 0.89},
      {'name': 'Butter Süßrahm', 'unit': '250g', 'orig': 2.29, 'disc': 1.49},
      {'name': 'Gouda Jong 48+', 'unit': '400g', 'orig': 3.49, 'disc': 2.19},
      {'name': 'Baguette Tradition', 'unit': '250g', 'orig': 1.20, 'disc': 0.65},
      {'name': 'Croissant Beurre', 'unit': '4x', 'orig': 2.80, 'disc': 1.80},
      {'name': 'Hähnchenbrustfilet', 'unit': '500g', 'orig': 5.99, 'disc': 3.99},
      {'name': 'Rinderhackfleisch', 'unit': '500g', 'orig': 4.99, 'disc': 3.49},
      {'name': 'Freilandeier Gr. M', 'unit': '10er', 'orig': 2.69, 'disc': 1.79},
      {'name': 'Speisequark Magerstufe', 'unit': '500g', 'orig': 1.49, 'disc': 0.99},
      {'name': 'Mineralwasser Medium', 'unit': '1.5L', 'orig': 0.79, 'disc': 0.39},
      {'name': 'Bio Bananen', 'unit': '1kg', 'orig': 1.99, 'disc': 1.29},
      {'name': 'Äpfel Elstar', 'unit': '2kg', 'orig': 3.49, 'disc': 2.29},
      {'name': 'Kartoffeln Festkochend', 'unit': '2.5kg', 'orig': 2.99, 'disc': 1.89},
      {'name': 'Speisezwiebeln', 'unit': '1kg', 'orig': 1.49, 'disc': 0.89},
      {'name': 'Pasta Spaghetti No.5', 'unit': '500g', 'orig': 1.69, 'disc': 0.89},
      {'name': 'Olivenöl Extra Vergine', 'unit': '750ml', 'orig': 8.99, 'disc': 5.99},
      {'name': 'Passierte Tomaten', 'unit': '500g', 'orig': 0.99, 'disc': 0.59},
      {'name': 'Haferflocken Zart', 'unit': '500g', 'orig': 0.89, 'disc': 0.49},
      {'name': 'Erdbeermarmelade', 'unit': '450g', 'orig': 2.49, 'disc': 1.69},
    ];

    final List<LocalDiscountItem> generatedDeals = [];
    int idCounter = 1;

    final flatStores = <Map<String, String>>[];
    storesByCountry.forEach((country, stores) {
      for (final s in stores) {
        flatStores.add({'country': country, 'store': s});
      }
    });

    for (int i = 0; i < 100; i++) {
      final tpl = sampleTemplates[i % sampleTemplates.length];
      final st = flatStores[i % flatStores.length];
      final isEvening = (i % 3 == 0);
      final dist = '${((i * 137) % 1500) + 150}m';

      generatedDeals.add(
        LocalDiscountItem(
          id: idCounter++,
          name: '${tpl['name']} (${st['country']})',
          store: st['store']!,
          originalPrice: (tpl['orig'] as double) + ((i % 5) * 0.10),
          discountedPrice: (tpl['disc'] as double),
          unit: tpl['unit'] as String,
          distance: dist,
          eveningClearance: isEvening,
          inCart: (i % 5 == 0), // %20 sepete eklensin
        ),
      );
    }

    expect(generatedDeals.length, 100);

    // Farkli ulke ve magza sayisi kontrolu
    final uniqueStores = generatedDeals.map((d) => d.store).toSet();
    expect(uniqueStores.length, greaterThanOrEqualTo(15));

    // Tasarruf ve sepet hesaplama kontrolu
    final cartItems = generatedDeals.where((d) => d.inCart).toList();
    expect(cartItems.length, 20);

    final totalOrig = cartItems.fold(0.0, (sum, d) => sum + d.originalPrice);
    final totalDisc = cartItems.fold(0.0, (sum, d) => sum + d.discountedPrice);
    final totalSavings = cartItems.fold(0.0, (sum, d) => sum + d.savings);

    expect(totalSavings, closeTo(totalOrig - totalDisc, 0.001));
    expect(totalSavings, greaterThan(10.0)); // 20 urunde belirgin tasarruf

    // Yerel Asistan Motoru Coklu Urun & Rota Oneri Kontrolu
    final recommendation = LocalAssistantEngine.generateRecommendation(generatedDeals, cartItems);
    expect(recommendation.contains('tasarruf'), isTrue);
    expect(recommendation.contains('Akıllı Rota'), isTrue);

    // Almanca etiket aciklama kontrolu
    final exp1 = LocalAssistantEngine.explainGermanLabel('Bio Vollmilch 3.8%');
    expect(exp1.contains('İnek Sütü'), isTrue);

    final exp2 = LocalAssistantEngine.explainGermanLabel('Gouda Jong');
    expect(exp2.contains('Peynir'), isTrue);
  });
}
