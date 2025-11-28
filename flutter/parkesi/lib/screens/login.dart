import 'package:flutter/material.dart';

class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Login")),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Usuario
            TextField(
              decoration: const InputDecoration(
                labelText: "Usuario",
                border: OutlineInputBorder(),
              ),
            ),

            const SizedBox(height: 20),

            // Contraseña
            TextField(
              obscureText: true,
              decoration: const InputDecoration(
                labelText: "Contraseña",
                border: OutlineInputBorder(),
              ),
            ),

            const SizedBox(height: 30),

            // Botón Login
            ElevatedButton(
              onPressed: () {
                // Aquí pondrás la lógica de validación
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text("Intentando iniciar sesión...")),
                );
              },
              child: const Text("Entrar"),
            ),
          ],
        ),
      ),
    );
  }
}
