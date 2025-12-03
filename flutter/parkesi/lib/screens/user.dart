import 'package:flutter/material.dart';
import 'consult.dart';
import 'register_vehicle.dart';
import '../services/fastapi.dart';

class UserScreen extends StatelessWidget {
  final String email;

  UserScreen({super.key, required this.email});

  final api = ApiService();

  void showMessage(BuildContext context, String msg) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(msg)),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color.fromARGB(255, 29, 41, 107),
      appBar: AppBar(title: const Text("Usuario")),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              SizedBox(
                width: 300,
                height: 75,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => ConsultScreen(email:email)),
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.all(20),
                  ),
                  child: const Text(
                    "Consultar Vehículos",
                    style: TextStyle(fontSize:20)),
                ),
              ),

              const SizedBox(width: 30),

              SizedBox(
                width: 300,
                height: 75,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => RegisterVehicleScreen(email:email)),
                    );
                  },
                  child: const Text(
                    "Registrar Vehiculo",
                    style: TextStyle(fontSize:20)),
                ),
              ),

              SizedBox(height: 100,),

              SizedBox(
                width: 300,
                height: 75,
                child: ElevatedButton(
                  onPressed: () => handleMessage(context),
                  child: const Text(
                    "Avisar de Bloqueo",
                    style: TextStyle(fontSize:25)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
