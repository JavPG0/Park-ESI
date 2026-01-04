import 'package:flutter/material.dart';
import 'home.dart';
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

  Future<void> deleteConfirmation(BuildContext context) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text("Confirmar eliminación"),
        content: const Text("¿Estás seguro de que quieres eliminar este usuario?"),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text("No"),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text("Sí"),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      Navigator.pop(context);
      Navigator.pop(context);
      final success = await api.deleteUser(email);

      if (success) {
        showMessage(context, "Usuario eliminado.");
      } else {
        showMessage(context, "Error al eliminar usuario.");
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Usuario")),
      body: Container(
        width: double.infinity,
        height: double.infinity,
        decoration: const BoxDecoration(
          image: DecorationImage(
            image: AssetImage("assets/images/background.jpg"),
            fit: BoxFit.cover,
          ),
        ),
        child: Center(
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
                      style: TextStyle(fontSize:20, fontWeight: FontWeight.bold)),
                  ),
                ),

                SizedBox(height: 50),

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
                      style: TextStyle(fontSize:20, fontWeight: FontWeight.bold)),
                  ),
                ),

                SizedBox(height: 50),

                SizedBox(
                  width: 300,
                  height: 75,
                  child: ElevatedButton(
                    onPressed: () => deleteConfirmation(context),
                    child: const Text(
                      "Eliminar Usuario",
                      style: TextStyle(fontSize:20, fontWeight: FontWeight.bold)),
                  ),
                ),

                SizedBox(height: 50),

                SizedBox(
                  width: 300,
                  height: 75,
                  child: ElevatedButton(
                    onPressed: () => showMessage(context, "Función en desarrollo"),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.zero,
                      ),
                      textStyle: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 25,
                      ),
                    ),
                    child: const Text("Avisar de Bloqueo"),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
