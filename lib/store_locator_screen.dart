import 'package:flutter/material.dart';
import 'localization_service.dart';

class StoreLocation {
  final String name;
  final String chain;
  final String address;
  final String city;
  final String distance;
  final String hours;
  final double rating;

  const StoreLocation({
    required this.name,
    required this.chain,
    required this.address,
    required this.city,
    required this.distance,
    required this.hours,
    required this.rating,
  });
}

class StoreLocatorScreen extends StatefulWidget {
  final Function(String storeName)? onSelectStore;

  const StoreLocatorScreen({super.key, this.onSelectStore});

  @override
  State<StoreLocatorScreen> createState() => _StoreLocatorScreenState();
}

class _StoreLocatorScreenState extends State<StoreLocatorScreen> {
  String _selectedChain = 'Tümü';

  static const List<StoreLocation> _mockStores = [
    StoreLocation(
      name: 'Lidl - Hauptbahnhof Süd',
      chain: 'Lidl',
      address: 'Bayerstraße 12, 80335 München',
      city: 'München',
      distance: '350 m',
      hours: '07:00 - 21:00',
      rating: 4.5,
    ),
    StoreLocation(
      name: 'Rewe City Center',
      chain: 'Rewe',
      address: 'Karlsplatz 8, 80335 München',
      city: 'München',
      distance: '600 m',
      hours: '07:00 - 22:00',
      rating: 4.6,
    ),
    StoreLocation(
      name: 'Aldi Süd Ostbahnhof',
      chain: 'Aldi Süd',
      address: 'Orleansstraße 10, 81669 München',
      city: 'München',
      distance: '850 m',
      hours: '08:00 - 20:00',
      rating: 4.3,
    ),
    StoreLocation(
      name: 'Edeka Center Schwabing',
      chain: 'Edeka',
      address: 'Leopoldstraße 82, 80802 München',
      city: 'München',
      distance: '1.2 km',
      hours: '07:30 - 20:00',
      rating: 4.7,
    ),
    StoreLocation(
      name: 'Kaufland Neuperlach',
      chain: 'Kaufland',
      address: 'Albert-Schweitzer-Straße 64, 81735 München',
      city: 'München',
      distance: '2.1 km',
      hours: '07:00 - 22:00',
      rating: 4.4,
    ),
    StoreLocation(
      name: 'Penny Markt Westend',
      chain: 'Penny',
      address: 'Westendstraße 98, 80339 München',
      city: 'München',
      distance: '1.5 km',
      hours: '07:00 - 20:00',
      rating: 4.1,
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final s = LocalizationService.instance.strings;
    final chains = ['Tümü', 'Lidl', 'Rewe', 'Aldi Süd', 'Edeka', 'Kaufland', 'Penny'];

    final filtered = _mockStores.where((store) {
      if (_selectedChain != 'Tümü' && store.chain != _selectedChain) {
        return false;
      }
      return true;
    }).toList();

    return Column(
      children: [
        // Interaktif Radar / Harita Temsili Banner
        Container(
          margin: const EdgeInsets.all(12),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF003399), Color(0xFF002266)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.12),
                blurRadius: 8,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Column(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.near_me, color: Color(0xFFFFCC00), size: 24),
                      const SizedBox(width: 8),
                      Text(
                        s.mapTab,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.green.shade600,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.circle, color: Colors.white, size: 8),
                        const SizedBox(width: 4),
                        Text(
                          '${filtered.length} Aktif Şube',
                          style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              // Simüle Edilmiş Harita Göstergesi
              Container(
                height: 100,
                width: double.infinity,
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.08),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.white.withOpacity(0.2)),
                ),
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    const Icon(Icons.radar, color: Color(0xFFFFCC00), size: 64),
                    Positioned(
                      top: 15,
                      left: 40,
                      child: _buildPin('Lidl', Colors.yellow.shade700),
                    ),
                    Positioned(
                      bottom: 20,
                      right: 50,
                      child: _buildPin('Rewe', Colors.redAccent),
                    ),
                    Positioned(
                      top: 30,
                      right: 80,
                      child: _buildPin('Aldi', Colors.lightBlue),
                    ),
                    Positioned(
                      bottom: 15,
                      left: 70,
                      child: _buildPin('Edeka', Colors.blue.shade900),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),

        // Zincir Filtresi
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
          child: Row(
            children: chains.map((ch) {
              final isSel = _selectedChain == ch;
              return Padding(
                padding: const EdgeInsets.only(right: 6),
                child: FilterChip(
                  label: Text(ch == 'Tümü' ? s.filterAll : ch),
                  selected: isSel,
                  selectedColor: const Color(0xFFFFCC00),
                  onSelected: (_) => setState(() => _selectedChain = ch),
                ),
              );
            }).toList(),
          ),
        ),

        // Şube Listesi
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            itemCount: filtered.length,
            itemBuilder: (context, index) {
              final store = filtered[index];
              return Card(
                elevation: 1,
                margin: const EdgeInsets.only(bottom: 8),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                child: ListTile(
                  leading: CircleAvatar(
                    backgroundColor: const Color(0xFF003399).withOpacity(0.1),
                    child: const Icon(Icons.storefront, color: Color(0xFF003399)),
                  ),
                  title: Text(store.name, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                  subtitle: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const SizedBox(height: 4),
                      Text(store.address, style: const TextStyle(fontSize: 12, color: Colors.black87)),
                      const SizedBox(height: 2),
                      Row(
                        children: [
                          Icon(Icons.access_time, size: 12, color: Colors.green.shade700),
                          const SizedBox(width: 4),
                          Text(store.hours, style: TextStyle(fontSize: 11, color: Colors.green.shade700, fontWeight: FontWeight.w600)),
                          const SizedBox(width: 8),
                          Icon(Icons.star, size: 12, color: Colors.amber.shade700),
                          Text('${store.rating}', style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
                        ],
                      ),
                    ],
                  ),
                  trailing: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: const Color(0xFF003399),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          store.distance,
                          style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold),
                        ),
                      ),
                      const SizedBox(height: 4),
                      InkWell(
                        onTap: () {
                          if (widget.onSelectStore != null) {
                            widget.onSelectStore!(store.chain);
                          }
                        },
                        child: Text(
                          s.viewDeals,
                          style: const TextStyle(fontSize: 10, color: Color(0xFF003399), fontWeight: FontWeight.bold),
                        ),
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

  Widget _buildPin(String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(10),
        boxShadow: const [BoxShadow(color: Colors.black26, blurRadius: 4)],
      ),
      child: Text(
        label,
        style: const TextStyle(color: Colors.white, fontSize: 9, fontWeight: FontWeight.bold),
      ),
    );
  }
}
