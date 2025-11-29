import 'package:flutter/material.dart';

class RegisterScreen extends StatelessWidget {
  const RegisterScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color.fromARGB(255, 29, 41, 107),
      appBar: AppBar(title: const Text("Login")),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Nombre
            TextField(
              decoration: const InputDecoration(
                labelText: "Nombre",
                labelStyle: TextStyle(fontSize: 15, color: Colors.white),
                border: OutlineInputBorder(),
                focusColor: Colors.white,
              ),
              style: TextStyle(fontSize: 20, color: Colors.white),
            ),

            const SizedBox(height: 30),

            // Email
            TextField(
              decoration: const InputDecoration(
                labelText: "Email",
                labelStyle: TextStyle(fontSize: 15, color: Colors.white),
                border: OutlineInputBorder(),
                focusColor: Colors.white,
              ),
              style: TextStyle(fontSize: 20, color: Colors.white),
            ),

            const SizedBox(height: 30),

            // Contraseña
            TextField(
              obscureText: true,
              decoration: const InputDecoration(
                labelText: "Contraseña",
                labelStyle: TextStyle(fontSize: 15, color: Colors.white),
                border: OutlineInputBorder(),
                focusColor: Colors.white,
              ),
              style: TextStyle(fontSize: 20, color: Colors.white),
            ),

            const SizedBox(height: 30),

            // Confirmar Contraseña
            TextField(
              obscureText: true,
              decoration: const InputDecoration(
                labelText: "Confirmar Contraseña",
                labelStyle: TextStyle(fontSize: 15, color: Colors.white),
                border: OutlineInputBorder(),
                focusColor: Colors.white,
              ),
              style: TextStyle(fontSize: 20, color: Colors.white),
            ),

            const SizedBox(height: 50),

            SizedBox(
              width: 150,
              height: 75,
              child: ElevatedButton(
                onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text("Intentando nuevo registro...")),
                );
              },
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.all(20),
              ),
              child: const Text(
                "Registrar",
                style: TextStyle(fontSize:25)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
