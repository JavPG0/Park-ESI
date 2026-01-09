import 'package:flutter/material.dart';
import '../services/fastapi.dart';

class ConsultScreen extends StatefulWidget {
  final String email;

  const ConsultScreen({super.key, required this.email});

  @override
  State<ConsultScreen> createState() => _ConsultScreenState();
}

class _ConsultScreenState extends State<ConsultScreen> {
  final api = ApiService();

  void showMessage(String msg) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(msg)),
    );
  }

  late Future<List<dynamic>> vehicles;

  @override
  void initState() {
    super.initState();
    vehicles = api.getVehicles(widget.email);
  }

  void refreshList() {
    setState(() {
      vehicles = api.getVehicles(widget.email);
    });
  }

  Future<void> deleteVehicle(BuildContext context, String plate) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text("Confirmar eliminación"),
        content: const Text("¿Estás seguro de que quieres eliminar este vehículo?"),
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
      final success = await api.deleteVehicle(plate);

      if (success) {
        showMessage("Vehículo eliminado.");
        refreshList();
      } else {
        showMessage("Error al eliminar vehículo.");
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Consultar Vehículos")),
      body: Container(
        width: double.infinity,
        height: double.infinity,
        decoration: const BoxDecoration(
          image: DecorationImage(
            image: AssetImage("assets/images/background.jpg"),
            fit: BoxFit.cover,
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: FutureBuilder<List<dynamic>>(
            future: vehicles,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Center(
                  child: CircularProgressIndicator(color: Colors.white),
                );
              }

              if (!snapshot.hasData || snapshot.data!.isEmpty) {
                return const Center(
                  child: Text(
                    "No se encontraron vehículos registrados.",
                    style: TextStyle(color: Colors.white, fontSize: 18),
                  ),
                );
              }

              final vehicles = snapshot.data!;

              return ListView.builder(
                itemCount: vehicles.length,
                itemBuilder: (context, index) {
                  final v = vehicles[index];
                  return Card(
                    color: Colors.white.withOpacity(0.9),
                    margin: const EdgeInsets.symmetric(vertical: 10),
                    child: ListTile(
                      title: Text("Vehículo (${index + 1})"),
                      subtitle: Text(
                        "Matrícula: ${v["plate"]}\n"
                        "Color: ${v["color"]}\n"
                        "Marca: ${v["brand"]}",
                      ),
                      trailing: IconButton(
                        icon: const Icon(Icons.delete, color: Colors.red),
                        onPressed: () => deleteVehicle(context, v["plate"]),
                      ),
                    ),
                  );
                },
              );
            },
          ),
        ),
      ),
    );
  }
}
