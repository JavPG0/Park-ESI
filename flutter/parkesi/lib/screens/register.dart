import 'package:flutter/material.dart';
import '../services/fastapi.dart';

class RegisterScreen extends StatelessWidget {
  RegisterScreen({super.key});

  final api = ApiService();

  final nameController = TextEditingController();
  final emailController = TextEditingController();
  final passwordController = TextEditingController();
  final confirmController = TextEditingController();

  void showMessage(BuildContext context, String msg) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(msg)),
    );
  }

  Future<void> handleRegister(BuildContext context) async {
    final name = nameController.text.trim();
    final email = emailController.text.trim();
    final password = passwordController.text.trim();
    final confirm = confirmController.text.trim();

    if (name.isEmpty || email.isEmpty || password.isEmpty || confirm.isEmpty) {
      showMessage(context, "Todos los campos son obligatorios.");
      return;
    }

    if (password != confirm) {
      showMessage(context, "Las contraseñas no coinciden.");
      return;
    }

    final response = await api.registerUser(
      name: name,
      email: email,
      password: password,
    );

    if (response["status"] == 200) {
      showMessage(context, "Usuario registrado correctamente.");
      Navigator.pop(context);
    } else {
      showMessage(context, "Error: ${response["data"]["detail"]}");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color.fromARGB(255, 29, 41, 107),
      appBar: AppBar(title: const Text("Registro")),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TextField(
              controller: nameController,
              decoration: const InputDecoration(
                labelText: "Nombre",
                labelStyle: TextStyle(fontSize: 15, color: Colors.white),
                border: OutlineInputBorder(),
              ),
              style: const TextStyle(fontSize: 15, color: Colors.white),
            ),

            const SizedBox(height: 20),

            TextField(
              controller: emailController,
              decoration: const InputDecoration(
                labelText: "Email",
                labelStyle: TextStyle(fontSize: 15, color: Colors.white),
                border: OutlineInputBorder(),
              ),
              style: const TextStyle(fontSize: 15, color: Colors.white),
            ),

            const SizedBox(height: 20),

            TextField(
              controller: passwordController,
              obscureText: true,
              decoration: const InputDecoration(
                labelText: "Contraseña",
                labelStyle: TextStyle(fontSize: 15, color: Colors.white),
                border: OutlineInputBorder(),
              ),
              style: const TextStyle(fontSize: 15, color: Colors.white),
            ),

            const SizedBox(height: 20),

            TextField(
              controller: confirmController,
              obscureText: true,
              decoration: const InputDecoration(
                labelText: "Confirmar Contraseña",
                labelStyle: TextStyle(fontSize: 15, color: Colors.white),
                border: OutlineInputBorder(),
              ),
              style: const TextStyle(fontSize: 15, color: Colors.white),
            ),

            const SizedBox(height: 30),

            SizedBox(
              width: 150,
              height: 70,
              child: ElevatedButton(
                onPressed: () => handleRegister(context),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.all(20),
                ),
                child: const Text("Registrar", style: TextStyle(fontSize: 20)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
