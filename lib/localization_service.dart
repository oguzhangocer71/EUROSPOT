class AppStrings {
  final String appTitle;
  final String dealsTab;
  final String cartTab;
  final String mapTab;
  final String assistantTab;
  final String syncTooltip;
  final String addDeal;
  final String filterAll;
  final String searchHint;
  final String eveningClearance;
  final String totalCartPrice;
  final String totalSavings;
  final String cartEmpty;
  final String licenseDisclaimer;
  final String privacyPolicy;
  final String language;
  final String selectStore;
  final String storeDetails;
  final String openNow;
  final String viewDeals;
  final String smartAssistant;
  final String askSomething;
  final String send;

  const AppStrings({
    required this.appTitle,
    required this.dealsTab,
    required this.cartTab,
    required this.mapTab,
    required this.assistantTab,
    required this.syncTooltip,
    required this.addDeal,
    required this.filterAll,
    required this.searchHint,
    required this.eveningClearance,
    required this.totalCartPrice,
    required this.totalSavings,
    required this.cartEmpty,
    required this.licenseDisclaimer,
    required this.privacyPolicy,
    required this.language,
    required this.selectStore,
    required this.storeDetails,
    required this.openNow,
    required this.viewDeals,
    required this.smartAssistant,
    required this.askSomething,
    required this.send,
  });
}

class LocalizationService {
  LocalizationService._();
  static final LocalizationService instance = LocalizationService._();

  String currentLanguage = 'TR'; // 'TR', 'EN', 'DE'

  static const Map<String, AppStrings> _translations = {
    'TR': AppStrings(
      appTitle: 'EuroSpot',
      dealsTab: 'Fırsatlar',
      cartTab: 'Sepet & Tasarruf',
      mapTab: 'Mağaza Haritası',
      assistantTab: 'Asistan',
      syncTooltip: 'Canlı Katalogları Güncelle',
      addDeal: 'Fırsat Ekle',
      filterAll: 'Tümü',
      searchHint: 'Ürün veya mağaza ara...',
      eveningClearance: 'Akşam İndirimi',
      totalCartPrice: 'Toplam Tutar',
      totalSavings: 'Cebinde Kalan',
      cartEmpty: 'Sepetiniz boş. Fırsatlar sekmesinden ürün ekleyebilirsiniz.',
      licenseDisclaimer: 'Lisans ve Yasal Uyarı',
      privacyPolicy: 'Gizlilik İlkeleri',
      language: 'Dil',
      selectStore: 'Mağaza Seç',
      storeDetails: 'Şube Bilgileri',
      openNow: 'Açık • Kapanış 21:00',
      viewDeals: 'Fırsatları Gör',
      smartAssistant: 'Alışveriş Asistanı',
      askSomething: 'Örnek: Akşam indirimi var mı?',
      send: 'Gönder',
    ),
    'EN': AppStrings(
      appTitle: 'EuroSpot',
      dealsTab: 'Deals',
      cartTab: 'Cart & Savings',
      mapTab: 'Store Map',
      assistantTab: 'Assistant',
      syncTooltip: 'Sync Live Catalogues',
      addDeal: 'Add Deal',
      filterAll: 'All',
      searchHint: 'Search product or store...',
      eveningClearance: 'Evening Clearance',
      totalCartPrice: 'Total Price',
      totalSavings: 'You Saved',
      cartEmpty: 'Your cart is empty. Add deals from the deals tab.',
      licenseDisclaimer: 'License & Disclaimer',
      privacyPolicy: 'Privacy Policy',
      language: 'Language',
      selectStore: 'Select Store',
      storeDetails: 'Store Info',
      openNow: 'Open • Closes at 21:00',
      viewDeals: 'View Deals',
      smartAssistant: 'Shopping Assistant',
      askSomething: 'e.g. Any evening clearance deals?',
      send: 'Send',
    ),
    'DE': AppStrings(
      appTitle: 'EuroSpot',
      dealsTab: 'Angebote',
      cartTab: 'Warenkorb & Sparen',
      mapTab: 'Filialfinder',
      assistantTab: 'Assistent',
      syncTooltip: 'Prospekte synchronisieren',
      addDeal: 'Angebot hinzufügen',
      filterAll: 'Alle',
      searchHint: 'Produkt oder Filiale suchen...',
      eveningClearance: 'Abend-Rabatt',
      totalCartPrice: 'Gesamtsumme',
      totalSavings: 'Ersparnis',
      cartEmpty: 'Ihr Warenkorb ist leer. Fügen Sie Angebote hinzu.',
      licenseDisclaimer: 'Lizenz & Rechtshinweis',
      privacyPolicy: 'Datenschutz',
      language: 'Sprache',
      selectStore: 'Filiale wählen',
      storeDetails: 'Filialdetails',
      openNow: 'Geöffnet • Schließt um 21:00',
      viewDeals: 'Angebote anzeigen',
      smartAssistant: 'Einkaufsassistent',
      askSomething: 'z.B. Gibt es Abendangebote?',
      send: 'Senden',
    ),
  };

  AppStrings get strings => _translations[currentLanguage] ?? _translations['EN']!;

  void setLanguage(String lang) {
    if (_translations.containsKey(lang)) {
      currentLanguage = lang;
    }
  }
}
