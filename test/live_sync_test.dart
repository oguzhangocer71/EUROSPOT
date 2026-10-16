import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  test('Canli GitHub Raw JSON Veri Akisi Kontrolu', () async {
    final url = Uri.parse('https://raw.githubusercontent.com/oguzhangocer71/EUROSPOT/main/germany_deals.json');
    final response = await http.get(url);

    expect(response.statusCode, 200, reason: 'GitHub veri akisi erisilebilir olmali');
    
    final data = json.decode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
    expect(data.containsKey('deals'), isTrue, reason: 'JSON icinde deals listesi bulunmali');
    
    final deals = data['deals'] as List<dynamic>;
    expect(deals.isNotEmpty, isTrue, reason: 'En az bir adet indirimli urun olmali');

    print('Basariyla cekilen firsat sayisi: ${deals.length}');
    print('Desteklenen ulkeler alani: ${data['region']}');

    // Ornek ilk 3 urunu dogrula
    for (int i = 0; i < 3 && i < deals.length; i++) {
      final item = deals[i];
      expect(item['name'], isNotNull);
      expect(item['store'], isNotNull);
      expect(item['originalPrice'], isNotNull);
      expect(item['discountedPrice'], isNotNull);
      print('Dogrulandi: [${item['store']}] ${item['name']} -> ${item['discountedPrice']} EUR (Normal: ${item['originalPrice']} EUR)');
    }
  });
}
