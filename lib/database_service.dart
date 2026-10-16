import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

class LocalDiscountItem {
  final int? id;
  final String name;
  final String store;
  final double originalPrice;
  final double discountedPrice;
  final String unit;
  final String distance;
  final bool eveningClearance;
  final bool inCart;
  final String source;

  LocalDiscountItem({
    this.id,
    required this.name,
    required this.store,
    required this.originalPrice,
    required this.discountedPrice,
    required this.unit,
    required this.distance,
    this.eveningClearance = false,
    this.inCart = false,
    this.source = '',
  });

  double get savings => originalPrice - discountedPrice;

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'name': name,
      'store': store,
      'originalPrice': originalPrice,
      'discountedPrice': discountedPrice,
      'unit': unit,
      'distance': distance,
      'eveningClearance': eveningClearance ? 1 : 0,
      'inCart': inCart ? 1 : 0,
      'source': source,
    };
  }

  factory LocalDiscountItem.fromMap(Map<String, dynamic> map) {
    return LocalDiscountItem(
      id: map['id'] as int?,
      name: map['name'] as String,
      store: map['store'] as String,
      originalPrice: (map['originalPrice'] as num).toDouble(),
      discountedPrice: (map['discountedPrice'] as num).toDouble(),
      unit: map['unit'] as String,
      distance: map['distance'] as String,
      eveningClearance: (map['eveningClearance'] as int) == 1,
      inCart: (map['inCart'] as int) == 1,
      source: (map['source'] as String?) ?? '',
    );
  }

  LocalDiscountItem copyWith({bool? inCart}) {
    return LocalDiscountItem(
      id: id,
      name: name,
      store: store,
      originalPrice: originalPrice,
      discountedPrice: discountedPrice,
      unit: unit,
      distance: distance,
      eveningClearance: eveningClearance,
      inCart: inCart ?? this.inCart,
      source: source,
    );
  }
}

class DatabaseService {
  static final DatabaseService instance = DatabaseService._init();
  static Database? _database;

  DatabaseService._init();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDB('eurospot_local.db');
    return _database!;
  }

  Future<Database> _initDB(String filePath) async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, filePath);

    return await openDatabase(
      path,
      version: 1,
      onCreate: _createDB,
    );
  }

  Future<void> _createDB(Database db, int version) async {
    await db.execute('''
      CREATE TABLE deals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        store TEXT NOT NULL,
        originalPrice REAL NOT NULL,
        discountedPrice REAL NOT NULL,
        unit TEXT NOT NULL,
        distance TEXT NOT NULL,
        eveningClearance INTEGER NOT NULL,
        inCart INTEGER NOT NULL,
        source TEXT DEFAULT ''
      )
    ''');

    // Ilk surum urunleri kaldirildi; tum veriler guncel 1000 firsatlik katalogdan alinir
    // Tablo baslangicta temiz olusur.
  }

  Future<List<LocalDiscountItem>> getAllDeals() async {
    final db = await database;
    final result = await db.query('deals', orderBy: 'id ASC');
    return result.map((json) => LocalDiscountItem.fromMap(json)).toList();
  }

  Future<int> toggleCart(int id, bool inCart) async {
    final db = await database;
    return await db.update(
      'deals',
      {'inCart': inCart ? 1 : 0},
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<int> addDeal(LocalDiscountItem item) async {
    final db = await database;
    return await db.insert('deals', item.toMap());
  }

  Future<int> deleteDeal(int id) async {
    final db = await database;
    return await db.delete('deals', where: 'id = ?', whereArgs: [id]);
  }

  Future<int> clearAllDeals() async {
    final db = await database;
    return await db.delete('deals');
  }

  Future<int> syncDeals(List<LocalDiscountItem> incomingDeals) async {
    final db = await database;
    int addedCount = 0;
    for (final deal in incomingDeals) {
      final existing = await db.query(
        'deals',
        where: 'name = ? AND store = ?',
        whereArgs: [deal.name, deal.store],
      );
      if (existing.isEmpty) {
        await db.insert('deals', deal.toMap());
        addedCount++;
      } else {
        await db.update(
          'deals',
          {
            'originalPrice': deal.originalPrice,
            'discountedPrice': deal.discountedPrice,
            'unit': deal.unit,
            'distance': deal.distance,
            'eveningClearance': deal.eveningClearance ? 1 : 0,
          },
          where: 'name = ? AND store = ?',
          whereArgs: [deal.name, deal.store],
        );
      }
    }
    return addedCount;
  }
}
