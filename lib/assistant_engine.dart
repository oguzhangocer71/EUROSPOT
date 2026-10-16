import 'database_service.dart';

class LocalAssistantEngine {
  static final Map<String, String> translationDictionary = {
    'vollmilch': 'Tam Yağlı Süt (İnek Sütü)',
    'fettarme milch': 'Yarım Yağlı Süt',
    'bio': 'Organik Sertifikalı Ürün',
    'haltbare milch': 'UHT Uzun Ömürlü Süt',
    'gouda': 'Hollanda Menşeli Kaşar Benzeri Sarı Peynir',
    'baguette tradition': 'Geleneksel Fransız Somun Ekmeği',
    'hähnchenbrustfilet': 'Tavuk Göğüs Fileto',
    'hackfleisch': 'Kıyma (Dana/Domuz karışımı olabilir, Rindfleisch: %100 Dana)',
    'rindfleisch': '%100 Dana Eti',
    'schweinefleisch': 'Domuz Eti',
    'eier': 'Yumurta (Freilandhaltung: Gezen Tavuk)',
    'butter': 'Tereyağı',
    'quark': 'Taze Çökelek / Labne Benzeri Süt Ürünü',
    'mineralwasser': 'Maden Suyu / Mineralli Su (Mit Kohlensäure: Gazlı, Ohne Kohlensäure: Durgun Su)',
    'apfel': 'Elma',
    'kartoffeln': 'Patates',
    'zwiebeln': 'Kuru Soğan',
  };

  static String explainGermanLabel(String label) {
    final lower = label.toLowerCase();
    for (final entry in translationDictionary.entries) {
      if (lower.contains(entry.key)) {
        return '${entry.key.toUpperCase()}: ${entry.value}';
      }
    }
    return 'Bu ürün yerel Avrupa pazarında temel gıda ürünüdür. Detaylı içerik kontrolü önerilir.';
  }

  static String generateRecommendation(List<LocalDiscountItem> deals, List<LocalDiscountItem> cart) {
    if (deals.isEmpty) {
      return 'Şu anda kayıtlı yerel fırsat bulunmuyor.';
    }

    final eveningDeals = deals.where((d) => d.eveningClearance).toList();
    final totalSavings = cart.fold(0.0, (sum, item) => sum + item.savings);

    final buffer = StringBuffer();

    if (cart.isEmpty) {
      buffer.writeln('Sepetiniz henüz boş.');
      if (eveningDeals.isNotEmpty) {
        buffer.writeln(
          'Akşam İpucu: ${eveningDeals.first.store} mağazasında ${eveningDeals.first.name} akşam indirimine girmiş durumda. İncelemenizi tavsiye ederim.',
        );
      } else {
        buffer.writeln('En yakın indirimleri Fırsatlar sekmesinden sepetinize ekleyerek tasarruf etmeye başlayabilirsiniz.');
      }
    } else {
      buffer.writeln('Mevcut sepetinizle toplam €${totalSavings.toStringAsFixed(2)} tasarruf sağlıyorsunuz!');
      final stores = cart.map((e) => e.store).toSet();
      if (stores.length > 1) {
        buffer.writeln(
          'Akıllı Rota: Sepetinizdeki ürünler ${stores.join(" ve ")} mağazalarına dağıtılmış durumda. Rotanızı bu sırayla planlarsanız en az mesafeyle alışverişi tamamlarsınız.',
        );
      }
      if (eveningDeals.any((d) => !cart.contains(d))) {
        final unadded = eveningDeals.firstWhere((d) => !cart.contains(d));
        buffer.writeln('Fırsat Radarı: ${unadded.store} mağazasındaki ${unadded.name} için akşam stok eritme indirimi devam ediyor.');
      }
    }

    return buffer.toString().trim();
  }
}
