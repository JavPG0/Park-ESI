import 'package:flutter/material.dart';
import 'parking.dart';
import 'login.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color.fromARGB(255, 29, 41, 107),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Logo
              Image.asset(
                'assets/images/logo.png',
                width: 540,
              ),

              const SizedBox(height: 40),

              // Botón Login
              ElevatedButton(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const LoginScreen()),
                  );
                },
                child: const Text("Login"),
              ),

              const SizedBox(height: 20),

              // Botón Parking
              ElevatedButton(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const ParkingScreen()),
                  );
                },
                child: const Text("Parking"),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
