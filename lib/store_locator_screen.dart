import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:url_launcher/url_launcher.dart';
import 'localization_service.dart';

class StoreLocation {
  final String name;
  final String chain;
  final String address;
  final String city;
  final String distance;
  final String hours;
  final double rating;
  final double lat;
  final double lng;
  final Color markerColor;

  const StoreLocation({
    required this.name,
    required this.chain,
    required this.address,
    required this.city,
    required this.distance,
    required this.hours,
    required this.rating,
    required this.lat,
    required this.lng,
    required this.markerColor,
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
  final MapController _mapController = MapController();
  StoreLocation? _selectedStoreOnMap;

  static const List<StoreLocation> _mockStores = [
    StoreLocation(
      name: 'Lidl - Hauptbahnhof Süd',
      chain: 'Lidl',
      address: 'Bayerstraße 12, 80335 München',
      city: 'München',
      distance: '350 m',
      hours: '07:00 - 21:00',
      rating: 4.5,
      lat: 48.1395,
      lng: 11.5585,
      markerColor: Color(0xFF0050AA),
    ),
    StoreLocation(
      name: 'Rewe City Center',
      chain: 'Rewe',
      address: 'Karlsplatz 8, 80335 München',
      city: 'München',
      distance: '600 m',
      hours: '07:00 - 22:00',
      rating: 4.6,
      lat: 48.1392,
      lng: 11.5660,
      markerColor: Color(0xFFCC0000),
    ),
    StoreLocation(
      name: 'Aldi Süd Ostbahnhof',
      chain: 'Aldi Süd',
      address: 'Orleansstraße 10, 81669 München',
      city: 'München',
      distance: '850 m',
      hours: '08:00 - 20:00',
      rating: 4.3,
      lat: 48.1285,
      lng: 11.6045,
      markerColor: Color(0xFF00205B),
    ),
    StoreLocation(
      name: 'Edeka Center Schwabing',
      chain: 'Edeka',
      address: 'Leopoldstraße 82, 80802 München',
      city: 'München',
      distance: '1.2 km',
      hours: '07:30 - 20:00',
      rating: 4.7,
      lat: 48.1610,
      lng: 11.5870,
      markerColor: Color(0xFF003882),
    ),
    StoreLocation(
      name: 'Kaufland Neuperlach',
      chain: 'Kaufland',
      address: 'Albert-Schweitzer-Straße 64, 81735 München',
      city: 'München',
      distance: '2.1 km',
      hours: '07:00 - 22:00',
      rating: 4.4,
      lat: 48.1020,
      lng: 11.6460,
      markerColor: Color(0xFFD40000),
    ),
    StoreLocation(
      name: 'Penny Markt Westend',
      chain: 'Penny',
      address: 'Westendstraße 98, 80339 München',
      city: 'München',
      distance: '1.5 km',
      hours: '07:00 - 20:00',
      rating: 4.1,
      lat: 48.1360,
      lng: 11.5340,
      markerColor: Color(0xFFC00000),
    ),
    StoreLocation(
      name: 'Carrefour Express République',
      chain: 'Carrefour',
      address: 'Place de la République, 75003 Paris',
      city: 'Paris',
      distance: '2.8 km',
      hours: '08:00 - 22:00',
      rating: 4.3,
      lat: 48.8675,
      lng: 2.3638,
      markerColor: Color(0xFF004E98),
    ),
    StoreLocation(
      name: 'Albert Heijn Damrak',
      chain: 'Albert Heijn',
      address: 'Damrak 89, 1012 LP Amsterdam',
      city: 'Amsterdam',
      distance: '1.9 km',
      hours: '07:00 - 22:00',
      rating: 4.5,
      lat: 52.3738,
      lng: 4.8936,
      markerColor: Color(0xFF00A0E2),
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final s = LocalizationService.instance.strings;
    final chains = ['Tümü', 'Lidl', 'Rewe', 'Aldi Süd', 'Edeka', 'Kaufland', 'Penny', 'Carrefour', 'Albert Heijn'];

    final filtered = _mockStores.where((store) {
      if (_selectedChain != 'Tümü' && store.chain != _selectedChain) {
        return false;
      }
      return true;
    }).toList();

    return Column(
      children: [
        // Tam Aktif OpenStreetMap Canlı Harita
        Container(
          height: 250,
          margin: const EdgeInsets.fromLTRB(12, 10, 12, 6),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.15),
                blurRadius: 8,
                offset: const Offset(0, 3),
              ),
            ],
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(16),
            child: Stack(
              children: [
                FlutterMap(
                  mapController: _mapController,
                  options: MapOptions(
                    initialCenter: const LatLng(48.1375, 11.5755), // Münih Merkez
                    initialZoom: 12.5,
                  ),
                  children: [
                    TileLayer(
                      urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                      userAgentPackageName: 'com.eurospot.app',
                    ),
                    MarkerLayer(
                      markers: filtered.map((store) {
                        final isSelected = _selectedStoreOnMap == store;
                        return Marker(
                          point: LatLng(store.lat, store.lng),
                          width: 80,
                          height: 55,
                          child: GestureDetector(
                            onTap: () {
                              setState(() {
                                _selectedStoreOnMap = store;
                              });
                            },
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: isSelected ? const Color(0xFFFFCC00) : store.markerColor,
                                    borderRadius: BorderRadius.circular(8),
                                    boxShadow: const [BoxShadow(color: Colors.black38, blurRadius: 4)],
                                  ),
                                  child: Text(
                                    store.chain,
                                    style: TextStyle(
                                      color: isSelected ? Colors.black : Colors.white,
                                      fontSize: 10,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                                Icon(
                                  Icons.location_on,
                                  color: isSelected ? const Color(0xFFFFCC00) : store.markerColor,
                                  size: isSelected ? 30 : 24,
                                ),
                              ],
                            ),
                          ),
                        );
                      }).toList(),
                    ),
                  ],
                ),
                // Harita Bilgi Rozeti
                Positioned(
                  top: 10,
                  right: 10,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                    decoration: BoxDecoration(
                      color: const Color(0xFF003399).withOpacity(0.9),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.location_searching, color: Color(0xFFFFCC00), size: 14),
                        const SizedBox(width: 4),
                        Text(
                          '${filtered.length} Şube Haritada',
                          style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold),
                        ),
                      ],
                    ),
                  ),
                ),
                // Haritada Seçili Şube Kartı
                if (_selectedStoreOnMap != null)
                  Positioned(
                    bottom: 10,
                    left: 10,
                    right: 10,
                    child: Card(
                      color: Colors.white,
                      elevation: 6,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      child: Padding(
                        padding: const EdgeInsets.all(8.0),
                        child: Row(
                          children: [
                            CircleAvatar(
                              backgroundColor: _selectedStoreOnMap!.markerColor,
                              radius: 16,
                              child: const Icon(Icons.store, color: Colors.white, size: 16),
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Text(
                                    _selectedStoreOnMap!.name,
                                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                  Text(
                                    '${_selectedStoreOnMap!.address} • ${_selectedStoreOnMap!.hours}',
                                    style: const TextStyle(fontSize: 10, color: Colors.grey),
                                    maxLines: 1,
                                  ),
                                ],
                              ),
                            ),
                            IconButton(
                              icon: const Icon(Icons.directions, color: Color(0xFF003399)),
                              onPressed: () async {
                                final uri = Uri.parse(
                                  'https://www.google.com/maps/search/?api=1&query=${_selectedStoreOnMap!.lat},${_selectedStoreOnMap!.lng}',
                                );
                                await launchUrl(uri, mode: LaunchMode.externalApplication);
                              },
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
              ],
            ),
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
