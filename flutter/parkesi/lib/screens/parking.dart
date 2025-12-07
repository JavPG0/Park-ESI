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
    //Plazas Reales
    PlazaLayout(id: 1, x: 5, y: 670, width: 80, height: 50),
    PlazaLayout(id: 2, x: 5, y: 610, width: 80, height: 50),
    PlazaLayout(id: 3, x: 5, y: 550, width: 80, height: 50),
    PlazaLayout(id: 4, x: 5, y: 490, width: 80, height: 50),
    PlazaLayout(id: 5, x: 5, y: 430, width: 80, height: 50),
    PlazaLayout(id: 6, x: 5, y: 370, width: 80, height: 50),
    PlazaLayout(id: 7, x: 5, y: 310, width: 80, height: 50),
    PlazaLayout(id: 8, x: 5, y: 250, width: 80, height: 50),
    PlazaLayout(id: 9, x: 5, y: 190, width: 80, height: 50),
    PlazaLayout(id: 10, x: 5, y: 130, width: 80, height: 50),
    PlazaLayout(id: 11, x: 5, y: 70, width: 80, height: 50),
    PlazaLayout(id: 12, x: 5, y: 10, width: 80, height: 50),
    PlazaLayout(id: 13, x: 295, y: 670, width: 80, height: 50),
    PlazaLayout(id: 14, x: 295, y: 610, width: 80, height: 50),
    PlazaLayout(id: 15, x: 295, y: 550, width: 80, height: 50),
    PlazaLayout(id: 16, x: 295, y: 490, width: 80, height: 50),
    PlazaLayout(id: 17, x: 295, y: 430, width: 80, height: 50),
    PlazaLayout(id: 18, x: 295, y: 370, width: 80, height: 50),
    PlazaLayout(id: 19, x: 295, y: 310, width: 80, height: 50),
    PlazaLayout(id: 20, x: 295, y: 250, width: 80, height: 50),
    PlazaLayout(id: 21, x: 295, y: 190, width: 80, height: 50),
    PlazaLayout(id: 22, x: 295, y: 130, width: 80, height: 50),
    PlazaLayout(id: 23, x: 295, y: 70, width: 80, height: 50),
    PlazaLayout(id: 24, x: 295, y: 10, width: 80, height: 50),
    //Plazas De Doble Fila
    PlazaLayout(id: 25, x: 100, y: 670, width: 80, height: 50),
    PlazaLayout(id: 26, x: 100, y: 610, width: 80, height: 50),
    PlazaLayout(id: 27, x: 100, y: 550, width: 80, height: 50),
    PlazaLayout(id: 28, x: 100, y: 490, width: 80, height: 50),
    PlazaLayout(id: 29, x: 100, y: 430, width: 80, height: 50),
    PlazaLayout(id: 30, x: 100, y: 370, width: 80, height: 50),
    PlazaLayout(id: 31, x: 100, y: 310, width: 80, height: 50),
    PlazaLayout(id: 32, x: 100, y: 250, width: 80, height: 50),
    PlazaLayout(id: 33, x: 100, y: 190, width: 80, height: 50),
    PlazaLayout(id: 34, x: 100, y: 130, width: 80, height: 50),
    PlazaLayout(id: 35, x: 100, y: 70, width: 80, height: 50),
    PlazaLayout(id: 36, x: 100, y: 10, width: 80, height: 50),
    PlazaLayout(id: 37, x: 200, y: 670, width: 80, height: 50),
    PlazaLayout(id: 38, x: 200, y: 610, width: 80, height: 50),
    PlazaLayout(id: 39, x: 200, y: 550, width: 80, height: 50),
    PlazaLayout(id: 40, x: 200, y: 490, width: 80, height: 50),
    PlazaLayout(id: 41, x: 200, y: 430, width: 80, height: 50),
    PlazaLayout(id: 42, x: 200, y: 370, width: 80, height: 50),
    PlazaLayout(id: 43, x: 200, y: 310, width: 80, height: 50),
    PlazaLayout(id: 44, x: 200, y: 250, width: 80, height: 50),
    PlazaLayout(id: 45, x: 200, y: 190, width: 80, height: 50),
    PlazaLayout(id: 46, x: 200, y: 130, width: 80, height: 50),
    PlazaLayout(id: 47, x: 200, y: 70, width: 80, height: 50),
    PlazaLayout(id: 48, x: 200, y: 10, width: 80, height: 50),
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
