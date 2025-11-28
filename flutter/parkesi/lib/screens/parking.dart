import 'package:flutter/material.dart';
import '../services/fastapi.dart';
import '../classes/plaza.dart';

class ParkingScreen extends StatefulWidget {
  const ParkingScreen({super.key});

  @override
  State<ParkingScreen> createState() => _ParkingScreenState();
}

class _ParkingScreenState extends State<ParkingScreen>{
  final api = ApiService();

  final layout = [
    PlazaLayout(id: 1, x: 20, y: 30, width: 80, height: 140),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color.fromARGB(255, 29, 41, 107),
      appBar: AppBar(title: Text("Plazas del Parking")),
      body: StreamBuilder(
        stream: Stream.periodic(Duration(milliseconds: 1000))
            .asyncMap((_) => api.getParkingSlots()),
        builder: (context, snapshot) {
          if (!snapshot.hasData) {
            return Center(child: CircularProgressIndicator());
          }

          final plazasDelBackend = snapshot.data as List;

          final estados = {
            for (var p in plazasDelBackend) p['id']: p['occupied'] == true
          };

          return Stack(
            children: layout.map((plaza) {
              final ocupado = estados[plaza.id] ?? false;

              return Positioned(
                left: plaza.x,
                top: plaza.y,
                child: Transform.rotate(
                  angle: plaza.rotation * 3.1416 / 180,
                  child: Container(
                    width: plaza.width,
                    height: plaza.height,
                    decoration: BoxDecoration(
                      color: ocupado ? Colors.red : Colors.green,
                      border: Border.all(color: Colors.white, width: 3),
                    ),
                    child: Center(
                      child: Text(
                        "${plaza.id}",
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                ),
              );
            }).toList(),
          );
        },
      )
    );
  }
}
