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
    PlazaLayout(id: 1, x: 5, y: 670, width: 80, height: 45),
    PlazaLayout(id: 2, x: 5, y: 615, width: 80, height: 45),
    PlazaLayout(id: 3, x: 5, y: 560, width: 80, height: 45),
    PlazaLayout(id: 4, x: 5, y: 505, width: 80, height: 45),
    PlazaLayout(id: 5, x: 5, y: 450, width: 80, height: 45),
    PlazaLayout(id: 6, x: 5, y: 395, width: 80, height: 45),
    PlazaLayout(id: 7, x: 5, y: 340, width: 80, height: 45),
    PlazaLayout(id: 8, x: 5, y: 285, width: 80, height: 45),
    PlazaLayout(id: 9, x: 5, y: 230, width: 80, height: 45),
    PlazaLayout(id: 10, x: 5, y: 175, width: 80, height: 45),
    PlazaLayout(id: 11, x: 5, y: 120, width: 80, height: 45),
    PlazaLayout(id: 12, x: 5, y: 65, width: 80, height: 45),
    PlazaLayout(id: 13, x: 5, y: 10, width: 80, height: 45),
    PlazaLayout(id: 14, x: 295, y: 670, width: 80, height: 50),
    PlazaLayout(id: 15, x: 295, y: 610, width: 80, height: 50),
    PlazaLayout(id: 16, x: 295, y: 550, width: 80, height: 50),
    PlazaLayout(id: 17, x: 295, y: 490, width: 80, height: 50),
    PlazaLayout(id: 18, x: 295, y: 430, width: 80, height: 50),
    PlazaLayout(id: 19, x: 295, y: 370, width: 80, height: 50),
    PlazaLayout(id: 20, x: 295, y: 310, width: 80, height: 50),
    PlazaLayout(id: 21, x: 295, y: 250, width: 80, height: 50),
    PlazaLayout(id: 22, x: 295, y: 190, width: 80, height: 50),
    PlazaLayout(id: 23, x: 295, y: 130, width: 80, height: 50),
    PlazaLayout(id: 24, x: 295, y: 70, width: 80, height: 50),
    PlazaLayout(id: 25, x: 295, y: 10, width: 80, height: 50),
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

      return LayoutBuilder(
        builder: (context, constraints) {
          final screenWidth = constraints.maxWidth;
          final screenHeight = constraints.maxHeight;

          return Stack(
            children: [
              ...layout.map((plaza) {
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
                        border: Border.all(
                          color: ocupado ? Colors.red : Colors.green,
                          width: 3,
                        ),
                      ),
                    ),
                  ),
                );
              }),

              Positioned(
                bottom: 20,
                left: screenWidth / 2 - 40,
                child: Column(
                  children: const [
                    Icon(
                      Icons.arrow_upward,
                      size: 100,
                      color: Colors.white,
                    ),
                    SizedBox(height: 4),
                    Text(
                      "Entrada",
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),

              Positioned(
                top: 5,
                right: 3,
                child: SizedBox(
                  width: screenWidth * 0.5,
                  height: screenHeight * 0.5,
                  child: Stack(
                    children: [
                      Container(
                        decoration: BoxDecoration(
                          border: Border.all(
                            color: Colors.yellow,
                            width: 3,
                          ),
                        ),
                      ),

                      Positioned(
                        left: 8,
                        top: 0,
                        bottom: 0,
                        child: Center(
                          child: RotatedBox(
                            quarterTurns: 1,
                            child: Text(
                              "Módulo B",
                              style: TextStyle(
                                color: Colors.yellow,
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          );
        },
      );
        },
      )
    );
  }
}
