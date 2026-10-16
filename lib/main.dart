import 'dart:io';
import 'package:flutter/material.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'database_service.dart';
import 'assistant_engine.dart';
import 'sync_service.dart';
import 'localization_service.dart';
import 'store_locator_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  if (Platform.isWindows || Platform.isLinux) {
    sqfliteFfiInit();
    databaseFactory = databaseFactoryFfi;
  }
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'EuroSpot',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF003399),
          primary: const Color(0xFF003399),
          secondary: const Color(0xFFFFCC00),
        ),
        useMaterial3: true,
      ),
      home: const EuroSpotMainScreen(),
    );
  }
}

typedef ProductItem = LocalDiscountItem;

class EuroSpotMainScreen extends StatefulWidget {
  const EuroSpotMainScreen({super.key});

  @override
  State<EuroSpotMainScreen> createState() => _EuroSpotMainScreenState();
}

class _EuroSpotMainScreenState extends State<EuroSpotMainScreen> {
  int _currentTabIndex = 0;
  List<LocalDiscountItem> _discounts = [];
  bool _isLoading = true;
  bool _isSyncing = false;
  String _selectedStore = 'Tümü';
  String _selectedCategory = 'Tümü';
  String _selectedPriceRange = 'Tümü';
  String _searchFilter = '';

  static const List<String> _priceRanges = [
    'Tümü',
    '1 - 10 €',
    '10 - 50 €',
    '50 - 100 €',
    '100 € Üstü',
  ];

  static const Map<String, List<String>> _categoryKeywords = {
    'Süt & Kahvaltılık': ['milch', 'süt', 'gouda', 'kaas', 'peynir', 'cheese', 'quark', 'fromage', 'camembert', 'twaróg', 'eier', 'yumurta', 'butter', 'nutella', 'waffle', 'stroopwafel', 'croissant', 'bergkäse', 'parmigiano'],
    'Et & Şarküteri': ['hähnchen', 'tavuk', 'fleisch', 'et', 'hackfleisch', 'kıyma', 'jamón', 'kiełbasa', 'sosis', 'rindfleisch', 'dana', 'filet'],
    'Fırın & Ekmek': ['brot', 'ekmek', 'baguette', 'croissant', 'waffle'],
    'Temel Gıda & Makarna': ['spaghetti', 'makarna', 'barilla', 'reis', 'pirinç', 'öl', 'oliva', 'zeytinyağı', 'zucker', 'şeker', 'mehl', 'un'],
    'İçecek & Kahve': ['kaffee', 'kahve', 'caffe', 'lavazza', 'espresso', 'wasser', 'su', 'mineralwasser', 'cola', 'çay', 'tee', 'saft', 'meyve suyu'],
    'Temizlik & Ev': ['ariel', 'pods', 'deterjan', 'yıkama', 'reiniger', 'sabun', 'şampuan', 'persil', 'finish'],
  };

  String _detectCategory(String productName) {
    final lower = productName.toLowerCase();
    for (final entry in _categoryKeywords.entries) {
      for (final keyword in entry.value) {
        if (lower.contains(keyword)) {
          return entry.key;
        }
      }
    }
    return 'Diğer';
  }

  Future<void> _syncDeals() async {
    setState(() => _isSyncing = true);
    final result = await SyncService.instance.fetchAndSyncDeals();
    await _loadData();
    if (mounted) {
      setState(() => _isSyncing = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(result.message),
          backgroundColor: result.success ? const Color(0xFF003399) : Colors.orange,
          duration: const Duration(seconds: 4),
        ),
      );
    }
  }

  @override
  void initState() {
    super.initState();
    _loadData();
    _autoSyncIfNeeded();
  }

  Future<void> _autoSyncIfNeeded() async {
    final result = await SyncService.instance.checkAndAutoSync();
    if (result != null && mounted) {
      await _loadData();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Haftalık Katalog Güncellendi: ${result.message}'),
          backgroundColor: const Color(0xFF003399),
          duration: const Duration(seconds: 3),
        ),
      );
    }
  }

  Future<void> _loadData() async {
    try {
      final deals = await DatabaseService.instance.getAllDeals();
      setState(() {
        _discounts = deals;
        _isLoading = false;
      });
    } catch (_) {
      setState(() {
        _isLoading = false;
      });
    }
  }

  List<LocalDiscountItem> get _cart => _discounts.where((d) => d.inCart).toList();
  double get _totalCartSavings => _cart.fold(0.0, (sum, item) => sum + item.savings);
  double get _totalCartPrice => _cart.fold(0.0, (sum, item) => sum + item.discountedPrice);

  Future<void> _toggleCart(LocalDiscountItem item) async {
    final newStatus = !item.inCart;
    if (item.id != null) {
      await DatabaseService.instance.toggleCart(item.id!, newStatus);
    }
    setState(() {
      final index = _discounts.indexWhere((d) => d.id == item.id);
      if (index != -1) {
        _discounts[index] = item.copyWith(inCart: newStatus);
      }
    });
  }

  void _showAddDealDialog() {
    final nameCtrl = TextEditingController();
    final storeCtrl = TextEditingController(text: 'Lidl');
    final origCtrl = TextEditingController();
    final discCtrl = TextEditingController();
    final unitCtrl = TextEditingController(text: '1 Adet / 1kg');
    final distCtrl = TextEditingController(text: '500m');
    bool evening = false;

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('Yeni Fırsat Ekle'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(controller: nameCtrl, decoration: const InputDecoration(labelText: 'Ürün Adı (ör. Vollmilch)')),
                TextField(controller: storeCtrl, decoration: const InputDecoration(labelText: 'Mağaza (Lidl, Aldi, Rewe)')),
                TextField(controller: origCtrl, decoration: const InputDecoration(labelText: 'Normal Fiyat (€)'), keyboardType: TextInputType.number),
                TextField(controller: discCtrl, decoration: const InputDecoration(labelText: 'İndirimli Fiyat (€)'), keyboardType: TextInputType.number),
                TextField(controller: unitCtrl, decoration: const InputDecoration(labelText: 'Birim (ör. 1L, 500g)')),
                TextField(controller: distCtrl, decoration: const InputDecoration(labelText: 'Mesafe (ör. 400m)')),
                CheckboxListTile(
                  title: const Text('Akşam Stok Eritme Fırsatı'),
                  value: evening,
                  onChanged: (val) => setDialogState(() => evening = val ?? false),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('İptal')),
            ElevatedButton(
              onPressed: () async {
                final orig = double.tryParse(origCtrl.text) ?? 0.0;
                final disc = double.tryParse(discCtrl.text) ?? 0.0;
                if (nameCtrl.text.isNotEmpty && orig > 0 && disc > 0) {
                  final newItem = LocalDiscountItem(
                    name: nameCtrl.text.trim(),
                    store: storeCtrl.text.trim(),
                    originalPrice: orig,
                    discountedPrice: disc,
                    unit: unitCtrl.text.trim(),
                    distance: distCtrl.text.trim(),
                    eveningClearance: evening,
                  );
                  await DatabaseService.instance.addDeal(newItem);
                  if (ctx.mounted) Navigator.pop(ctx);
                  await _loadData();
                }
              },
              child: const Text('Kaydet'),
            ),
          ],
        ),
      ),
    );
  }

  void _showExplainDialog(LocalDiscountItem item) {
    final explanation = LocalAssistantEngine.explainGermanLabel(item.name);
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Row(
          children: [
            const Icon(Icons.translate, color: Color(0xFF003399)),
            const SizedBox(width: 8),
            Expanded(child: Text(item.name, style: const TextStyle(fontSize: 16))),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Akıllı Etiket Açıklaması:', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Text(explanation, style: const TextStyle(fontSize: 14)),
            const SizedBox(height: 12),
            Text('Mağaza: ${item.store} • Birim: ${item.unit}', style: const TextStyle(color: Colors.grey, fontSize: 12)),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Kapat')),
        ],
      ),
    );
  }

  void _showLicenseDisclaimerDialog() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Lisans ve Yasal Uyarı'),
        content: const SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('EuroSpot v1.0.0 (Lemon Squeezy Tek Seferlik Sürüm)', style: TextStyle(fontWeight: FontWeight.bold)),
              SizedBox(height: 8),
              Text(
                '• Lisans Durumu: Ömür Boyu Aktif (Tek Seferlik 4.99 € Satın Alma)\n'
                '• Dijital Teslimat: Anında indirme ve çevrimdışı kullanım hakkı sağlandığından iade yapılamaz.\n'
                '• Sorumluluk Reddi (Disclaimer): Fiyat ve ürün bilgileri yalnızca bilgilendirme ve yerel tasarruf simülasyonu amaçlıdır. Mağazaların anlık fiyat ve stok değişikliklerinden yazılım geliştiricisi sorumlu tutulamaz.\n'
                '• Gizlilik: Tüm verileriniz cihazınızda yerel SQLite veritabanında saklanır. Hiçbir kişisel veri toplanmaz.',
                style: TextStyle(fontSize: 12, height: 1.4),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Anladım')),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.euro, color: Color(0xFFFFCC00)),
            SizedBox(width: 6),
            Text('EuroSpot', style: TextStyle(fontWeight: FontWeight.bold)),
          ],
        ),
        actions: [
          IconButton(
            icon: _isSyncing
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFFFFCC00)),
                  )
                : const Icon(Icons.sync, color: Color(0xFFFFCC00)),
            tooltip: LocalizationService.instance.strings.syncTooltip,
            onPressed: _isSyncing ? null : _syncDeals,
          ),
          PopupMenuButton<String>(
            icon: const Icon(Icons.more_vert),
            tooltip: 'Menü & Dil',
            onSelected: (value) {
              if (value.startsWith('lang_')) {
                final lang = value.replaceFirst('lang_', '');
                setState(() {
                  LocalizationService.instance.setLanguage(lang);
                });
              } else if (value == 'lisans') {
                _showLicenseDisclaimerDialog();
              } else if (value == 'gizlilik') {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Verileriniz yalnızca bu cihazda yerel saklanır. Hesap veya kimlik gerekmez.'),
                  ),
                );
              }
            },
            itemBuilder: (BuildContext context) => [
              PopupMenuItem<String>(
                value: 'lang_TR',
                child: Row(
                  children: [
                    const Text('🇹🇷  Türkçe'),
                    if (LocalizationService.instance.currentLanguage == 'TR') ...[
                      const Spacer(),
                      const Icon(Icons.check, size: 18, color: Colors.green),
                    ],
                  ],
                ),
              ),
              PopupMenuItem<String>(
                value: 'lang_EN',
                child: Row(
                  children: [
                    const Text('🇬🇧  English'),
                    if (LocalizationService.instance.currentLanguage == 'EN') ...[
                      const Spacer(),
                      const Icon(Icons.check, size: 18, color: Colors.green),
                    ],
                  ],
                ),
              ),
              PopupMenuItem<String>(
                value: 'lang_DE',
                child: Row(
                  children: [
                    const Text('🇩🇪  Deutsch'),
                    if (LocalizationService.instance.currentLanguage == 'DE') ...[
                      const Spacer(),
                      const Icon(Icons.check, size: 18, color: Colors.green),
                    ],
                  ],
                ),
              ),
              const PopupMenuDivider(),
              PopupMenuItem<String>(
                value: 'lisans',
                child: Row(
                  children: [
                    const Icon(Icons.info_outline, size: 20),
                    const SizedBox(width: 8),
                    Text(LocalizationService.instance.strings.licenseDisclaimer),
                  ],
                ),
              ),
              PopupMenuItem<String>(
                value: 'gizlilik',
                child: Row(
                  children: [
                    const Icon(Icons.shield_outlined, size: 20),
                    const SizedBox(width: 8),
                    Text(LocalizationService.instance.strings.privacyPolicy),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      body: _buildCurrentTab(),
      floatingActionButton: _currentTabIndex == 0
          ? FloatingActionButton.extended(
              onPressed: _showAddDealDialog,
              backgroundColor: const Color(0xFF003399),
              foregroundColor: Colors.white,
              icon: const Icon(Icons.add),
              label: Text(LocalizationService.instance.strings.addDeal),
            )
          : null,
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentTabIndex,
        onDestinationSelected: (index) => setState(() => _currentTabIndex = index),
        destinations: [
          NavigationDestination(icon: const Icon(Icons.local_offer), label: LocalizationService.instance.strings.dealsTab),
          NavigationDestination(
            icon: Badge(
              label: Text('${_cart.length}'),
              isLabelVisible: _cart.isNotEmpty,
              child: const Icon(Icons.shopping_bag_outlined),
            ),
            label: LocalizationService.instance.strings.cartTab,
          ),
          NavigationDestination(icon: const Icon(Icons.map_outlined), label: LocalizationService.instance.strings.mapTab),
          NavigationDestination(icon: const Icon(Icons.smart_toy_outlined), label: LocalizationService.instance.strings.assistantTab),
        ],
      ),
    );
  }

  Widget _buildCurrentTab() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }
    switch (_currentTabIndex) {
      case 0:
        return _buildDealsTab();
      case 1:
        return _buildCartTab();
      case 2:
        return StoreLocatorScreen(
          onSelectStore: (storeName) {
            setState(() {
              _selectedStore = storeName;
              _currentTabIndex = 0;
            });
          },
        );
      case 3:
        return _buildAssistantTab();
      default:
        return const SizedBox();
    }
  }

  Widget _buildDealsTab() {
    final filteredDeals = _discounts.where((d) {
      if (_selectedStore != 'Tümü' && !d.store.toLowerCase().contains(_selectedStore.toLowerCase())) {
        return false;
      }
      if (_selectedCategory != 'Tümü') {
        final cat = _detectCategory(d.name);
        if (cat != _selectedCategory) return false;
      }
      if (_selectedPriceRange != 'Tümü') {
        final price = d.discountedPrice;
        if (_selectedPriceRange == '1 - 10 €') {
          if (price < 1.0 || price > 10.0) return false;
        } else if (_selectedPriceRange == '10 - 50 €') {
          if (price < 10.0 || price > 50.0) return false;
        } else if (_selectedPriceRange == '50 - 100 €') {
          if (price < 50.0 || price > 100.0) return false;
        } else if (_selectedPriceRange == '100 € Üstü') {
          if (price <= 100.0) return false;
        }
      }
      if (_searchFilter.isNotEmpty) {
        final query = _searchFilter.toLowerCase();
        final matchName = d.name.toLowerCase().contains(query);
        final matchStore = d.store.toLowerCase().contains(query);
        final matchDist = d.distance.toLowerCase().contains(query);
        if (!matchName && !matchStore && !matchDist) return false;
      }
      return true;
    }).toList();

    final stores = ['Tümü', ..._discounts.map((d) => d.store).toSet()];
    final categories = ['Tümü', ..._categoryKeywords.keys, 'Diğer'];

    return Column(
      children: [
        Container(
          width: double.infinity,
          margin: const EdgeInsets.fromLTRB(12, 8, 12, 4),
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          decoration: BoxDecoration(
            color: const Color(0xFF003399).withValues(alpha: 0.08),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: const Color(0xFF003399).withValues(alpha: 0.2)),
          ),
          child: Row(
            children: [
              const Icon(Icons.location_on, color: Color(0xFF003399), size: 20),
              const SizedBox(width: 8),
              Expanded(
                child: TextField(
                  decoration: const InputDecoration(
                    hintText: 'Şube, Posta Kodu veya Ürün Ara... (ör. 10115, Rewe, Süt)',
                    border: InputBorder.none,
                    isDense: true,
                  ),
                  style: const TextStyle(fontSize: 13),
                  onChanged: (val) => setState(() => _searchFilter = val),
                ),
              ),
              if (_searchFilter.isNotEmpty)
                IconButton(
                  icon: const Icon(Icons.clear, size: 18),
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(),
                  onPressed: () => setState(() => _searchFilter = ''),
                ),
            ],
          ),
        ),
        // Kategori Filtreleme Çubuğu
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 2),
          child: Row(
            children: [
              const Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.category_outlined, size: 16, color: Color(0xFF003399)),
                  SizedBox(width: 4),
                  Text('Kategori:', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                  SizedBox(width: 6),
                ],
              ),
              ...categories.map((c) {
                final isSel = _selectedCategory == c;
                return Padding(
                  padding: const EdgeInsets.only(right: 6),
                  child: FilterChip(
                    label: Text(c, style: TextStyle(fontSize: 11, color: isSel ? Colors.white : Colors.black87)),
                    selected: isSel,
                    selectedColor: const Color(0xFF003399),
                    checkmarkColor: Colors.white,
                    onSelected: (selected) {
                      setState(() => _selectedCategory = selected ? c : 'Tümü');
                    },
                  ),
                );
              }),
            ],
          ),
        ),
        // Fiyat Aralığı Filtreleme Çubuğu
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 2),
          child: Row(
            children: [
              const Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.euro, size: 16, color: Colors.green),
                  SizedBox(width: 4),
                  Text('Fiyat:', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                  SizedBox(width: 6),
                ],
              ),
              ..._priceRanges.map((p) {
                final isSel = _selectedPriceRange == p;
                return Padding(
                  padding: const EdgeInsets.only(right: 6),
                  child: ChoiceChip(
                    label: Text(p, style: TextStyle(fontSize: 11, color: isSel ? Colors.white : Colors.black87)),
                    selected: isSel,
                    selectedColor: Colors.green.shade700,
                    onSelected: (selected) {
                      setState(() => _selectedPriceRange = selected ? p : 'Tümü');
                    },
                  ),
                );
              }),
            ],
          ),
        ),
        // Market Filtreleme Çubuğu
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 2),
          child: Row(
            children: [
              const Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.storefront_outlined, size: 16, color: Colors.orange),
                  SizedBox(width: 4),
                  Text('Market:', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                  SizedBox(width: 6),
                ],
              ),
              ...stores.map((s) {
                final isSel = _selectedStore == s;
                return Padding(
                  padding: const EdgeInsets.only(right: 6),
                  child: ChoiceChip(
                    label: Text(s, style: TextStyle(fontSize: 11, color: isSel ? Colors.white : Colors.black87)),
                    selected: isSel,
                    selectedColor: Colors.orange.shade800,
                    onSelected: (selected) {
                      setState(() => _selectedStore = selected ? s : 'Tümü');
                    },
                  ),
                );
              }),
            ],
          ),
        ),
        Expanded(
          child: filteredDeals.isEmpty
              ? const Center(
                  child: Text(
                    'Aradığınız kriterlere uygun şube veya fırsat bulunamadı.',
                    style: TextStyle(color: Colors.grey),
                  ),
                )
              : ListView.builder(
                  itemCount: filteredDeals.length,
                  itemBuilder: (context, index) {
                    final item = filteredDeals[index];
                    final inCart = _cart.contains(item);
                    return Card(
                      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
                      child: ListTile(
                        onTap: () => _showExplainDialog(item),
                        leading: CircleAvatar(
                          backgroundColor: item.eveningClearance ? Colors.orange.shade100 : Colors.blue.shade100,
                          child: Icon(
                            item.eveningClearance ? Icons.access_time_filled : Icons.storefront,
                            color: item.eveningClearance ? Colors.orange.shade800 : const Color(0xFF003399),
                          ),
                        ),
                        title: Row(
                          children: [
                            Expanded(child: Text(item.name, style: const TextStyle(fontWeight: FontWeight.bold))),
                            if (item.eveningClearance)
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                decoration: BoxDecoration(color: Colors.orange.shade700, borderRadius: BorderRadius.circular(4)),
                                child: const Text('Akşam İndirimi', style: TextStyle(color: Colors.white, fontSize: 10)),
                              ),
                          ],
                        ),
                        subtitle: Text('${item.store} • ${item.distance} • ${item.unit}'),
                        trailing: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              crossAxisAlignment: CrossAxisAlignment.end,
                              children: [
                                Text('€${item.originalPrice.toStringAsFixed(2)}', style: const TextStyle(decoration: TextDecoration.lineThrough, color: Colors.grey, fontSize: 12)),
                                Text('€${item.discountedPrice.toStringAsFixed(2)}', style: const TextStyle(color: Colors.green, fontWeight: FontWeight.bold, fontSize: 16)),
                              ],
                            ),
                            const SizedBox(width: 8),
                            IconButton(
                              icon: Icon(inCart ? Icons.check_circle : Icons.add_circle_outline, color: inCart ? Colors.green : const Color(0xFF003399)),
                              onPressed: () => _toggleCart(item),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
        ),
      ],
    );
  }

  Widget _buildCartTab() {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        children: [
          Card(
            color: Colors.green.shade50,
            elevation: 0,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16), side: BorderSide(color: Colors.green.shade300)),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  Column(
                    children: [
                      const Text('Toplam Tutar', style: TextStyle(color: Colors.grey, fontSize: 12)),
                      Text('€${_totalCartPrice.toStringAsFixed(2)}', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                    ],
                  ),
                  Container(height: 35, width: 1, color: Colors.green.shade300),
                  Column(
                    children: [
                      const Text('Cebinde Kalan', style: TextStyle(color: Colors.grey, fontSize: 12)),
                      Text('€${_totalCartSavings.toStringAsFixed(2)}', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.green)),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),
          Expanded(
            child: _cart.isEmpty
                ? const Center(child: Text('Sepetiniz boş. Fırsatlar sekmesinden ürün ekleyebilirsiniz.'))
                : ListView.builder(
                    itemCount: _cart.length,
                    itemBuilder: (context, index) {
                      final item = _cart[index];
                      return ListTile(
                        leading: const Icon(Icons.check, color: Colors.green),
                        title: Text(item.name),
                        subtitle: Text('${item.store} • Tasarruf: €${item.savings.toStringAsFixed(2)}'),
                        trailing: IconButton(
                          icon: const Icon(Icons.remove_circle_outline, color: Colors.red),
                          onPressed: () => _toggleCart(item),
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildAssistantTab() {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.blue.shade50,
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Row(
              children: [
                Icon(Icons.offline_bolt, color: Color(0xFF003399)),
                SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'EuroSpot Yerel Asistan: Tamamen cihaz üzerinde çevrimdışı çalışır. Verileriniz sunuculara gitmez.',
                    style: TextStyle(fontSize: 13),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          Expanded(
            child: Center(
              child: SingleChildScrollView(
                child: Text(
                  LocalAssistantEngine.generateRecommendation(_discounts, _cart),
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 15, height: 1.5),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
