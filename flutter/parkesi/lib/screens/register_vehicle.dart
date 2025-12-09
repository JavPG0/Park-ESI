import 'package:flutter/material.dart';
import '../services/fastapi.dart';

class RegisterVehicleScreen extends StatefulWidget {
  final String email;

  const RegisterVehicleScreen({super.key, required this.email});

  @override
  State<RegisterVehicleScreen> createState() => _RegisterVehicleScreenState();
}

class _RegisterVehicleScreenState extends State<RegisterVehicleScreen> {
  final api = ApiService();
  final plateController = TextEditingController();
  final colorController = TextEditingController();
  final brandController = TextEditingController();

  bool shared = false;

  void showMessage(BuildContext context, String msg) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(msg)),
    );
  }

  Future<void> handleRegister(BuildContext context) async {
    final plate = plateController.text.trim();
    final color = colorController.text.trim();
    final brand = brandController.text.trim();

    if (plate.isEmpty || color.isEmpty || brand.isEmpty) {
      showMessage(context, "Todos los campos son obligatorios.");
      return;
    }

    final response = await api.registerVehicle(
      email: widget.email,
      plate: plate,
      color: color,
      brand: brand,
      shared: shared,
    );

    if (response["status"] == 200) {
      showMessage(context, "Vehículo registrado correctamente.");
      Navigator.pop(context);
    } else {
      showMessage(context, "Error: ${response["data"]["detail"]}");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color.fromARGB(255, 29, 41, 107),
      appBar: AppBar(title: const Text("Registro de Vehículo")),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TextField(
              controller: plateController,
              decoration: const InputDecoration(
                labelText: "Matrícula",
                labelStyle: TextStyle(fontSize: 15, color: Colors.white),
                border: OutlineInputBorder(),
              ),
              style: const TextStyle(fontSize: 15, color: Colors.white),
            ),

            const SizedBox(height: 20),

            TextField(
              controller: colorController,
              decoration: const InputDecoration(
                labelText: "Color",
                labelStyle: TextStyle(fontSize: 15, color: Colors.white),
                border: OutlineInputBorder(),
              ),
              style: const TextStyle(fontSize: 15, color: Colors.white),
            ),

            const SizedBox(height: 20),

            TextField(
              controller: brandController,
              decoration: const InputDecoration(
                labelText: "Marca",
                labelStyle: TextStyle(fontSize: 15, color: Colors.white),
                border: OutlineInputBorder(),
              ),
              style: const TextStyle(fontSize: 15, color: Colors.white),
            ),

            const SizedBox(height: 20),

            CheckboxListTile(
              title: const Text(
                "Comparto el vehículo con algún usuario del parking",
                style: TextStyle(color: Colors.white),
              ),
              value: shared,
              onChanged: (newShared) {
                setState(() {
                  shared = newShared!;
                });
              },
            ),

            const SizedBox(height: 20),

            SizedBox(
              width: 150,
              height: 70,
              child: ElevatedButton(
                onPressed: () => handleRegister(context),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.all(20),
                ),
                child: const Text("Aceptar", style: TextStyle(fontSize: 20)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
