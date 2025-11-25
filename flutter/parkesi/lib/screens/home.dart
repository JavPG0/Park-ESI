import 'package:flutter/material.dart';
import '../services/fastapi.dart';

class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final api = ApiService();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Vehículos en el Parking")),
      body: FutureBuilder(
        future: api.getVehicles(),
        builder: (context, snapshot) {
          if (!snapshot.hasData) {
            return Center(child: CircularProgressIndicator());
          }

          final vehicles = snapshot.data as List;

          return ListView.builder(
            itemCount: vehicles.length,
            itemBuilder: (context, index) {
              final v = vehicles[index];
              return ListTile(
                title: Text("Vehículo ${v['vehicle_id']}"),
                subtitle: Text(
                  "Color: ${v['color'] ?? 'Desconocido'}\n"
                  "Marca: ${v['brand'] ?? 'Desconocida'}",
                ),
              );
            },
          );
        },
      ),
    );
  }
}
