import 'package:flutter/material.dart';
import 'home.dart';
import 'consult.dart';
import 'register_vehicle.dart';
import '../services/fastapi.dart';

class UserScreen extends StatefulWidget {
  final String email;

  const UserScreen({super.key, required this.email});

  @override
  State<UserScreen> createState() => _UserScreenState();
}

class _UserScreenState extends State<UserScreen> {
  final ApiService api = ApiService();

  bool isWarningButtonEnabled = false;
  List<String> blockingEmails = [];

  @override
  void initState() {
    super.initState();
    checkVehicles();
  }

  Future<void> checkVehicles() async {
    try {
      final emails = await api.getBlockingVehicles(widget.email);

      setState(() {
        blockingEmails = emails;
        isWarningButtonEnabled = emails.isNotEmpty;
      });
    } catch (_) {
      setState(() {
        blockingEmails = [];
        isWarningButtonEnabled = false;
      });
    }
  }

  Future<void> _onWarningButtonPressed() async {
    await notificationConfirmation(context);
  }

  void showMessage(String msg) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(msg)),
    );
  }

  Future<void> deleteConfirmation() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text("Confirmar eliminación"),
        content: const Text("¿Estás seguro de que quieres eliminar este usuario?"),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text("No")),
          TextButton(onPressed: () => Navigator.pop(context, true), child: const Text("Sí")),
        ],
      ),
    );

    if (confirmed == true) {
      Navigator.pop(context);
      Navigator.pop(context);

      final success = await api.deleteUser(widget.email);
      showMessage(success ? "Usuario eliminado." : "Error al eliminar usuario.");
    }
  }

  Future<void> notificationConfirmation(BuildContext context) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text("Aviso de bloqueo"),
        content: const Text(
          "¿Quieres enviar un aviso al propietario del vehículo que te está bloqueando?",
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text("No")),
          TextButton(onPressed: () => Navigator.pop(context, true), child: const Text("Sí")),
        ],
      ),
    );

    if (confirmed == true) {
      final success = await api.sendEmails(blockingEmails);
      showMessage(success ? "Aviso enviado." : "Error al enviar el aviso.");
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
                        MaterialPageRoute(builder: (_) => ConsultScreen(email: widget.email)),
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
                        MaterialPageRoute(builder: (_) => RegisterVehicleScreen(email: widget.email)),
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
                    onPressed: () => deleteConfirmation,
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
                    onPressed: isWarningButtonEnabled ? _onWarningButtonPressed : null,
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
