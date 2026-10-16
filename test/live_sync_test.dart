import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  test('Canli GitHub Raw JSON Veri Akisi Kontrolu', () async {
    final url = Uri.parse('https://raw.githubusercontent.com/oguzhangocer71/EUROSPOT/main/germany_deals.json');
    final response = await http.get(url);

    expect(response.statusCode, 200, reason: 'GitHub veri akisi erisilebilir olmali');
    
    final decoded = json.decode(utf8.decode(response.bodyBytes));
    final List<dynamic> deals = decoded is List ? decoded : (decoded['deals'] as List<dynamic>? ?? []);
    expect(deals.isNotEmpty, isTrue, reason: 'En az bir adet indirimli urun olmali');

    // Ornek ilk 3 urunu dogrula
    for (int i = 0; i < 3 && i < deals.length; i++) {
      final item = deals[i] as Map<String, dynamic>;
      final title = item['name'] ?? item['title'];
      final store = item['store'];
      final price = item['discountedPrice'] ?? item['price'];
      expect(title, isNotNull, reason: 'Urun ismi bos olamaz');
      expect(store, isNotNull, reason: 'Magaza adi bos olamaz');
      expect(price, isNotNull, reason: 'Fiyat bos olamaz');
    }
  });
}
