import 'package:flutter/material.dart';
import '../services/fastapi.dart';
import 'user.dart';

class LoginScreen extends StatelessWidget {
  LoginScreen({super.key});

  final api = ApiService();

  final emailController = TextEditingController();
  final passwordController = TextEditingController();

  void showMessage(BuildContext context, String msg) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(msg)),
    );
  }

  Future<void> handleLogin(BuildContext context) async {
    final email = emailController.text.trim();
    final password = passwordController.text.trim();

    if (email.isEmpty || password.isEmpty) {
      showMessage(context, "Todos los campos son obligatorios.");
      return;
    }

    final response = await api.loginUser(
      email: email,
      password: password,
    );

    if (response["status"] == 200) {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => UserScreen(email:email)),
      );
    } else {
      showMessage(context, "Error: ${response["data"]["detail"]}");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Login")),
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
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Email
              TextField(
                controller: emailController,
                decoration: const InputDecoration(
                  labelText: "Email",
                  labelStyle: TextStyle(fontSize: 15, color: Colors.white),
                  filled: true,
                  fillColor: Colors.black,
                  border: OutlineInputBorder(),
                ),
                style: const TextStyle(fontSize: 20, color: Colors.white),
              ),

              const SizedBox(height: 30),

              // Contraseña
              TextField(
                controller: passwordController,
                obscureText: true,
                decoration: const InputDecoration(
                  labelText: "Contraseña",
                  labelStyle: TextStyle(fontSize: 15, color: Colors.white),
                  filled: true,
                  fillColor: Colors.black,
                  border: OutlineInputBorder(),
                ),
                style: const TextStyle(fontSize: 20, color: Colors.white),
              ),

              const SizedBox(height: 50),

              SizedBox(
                width: 150,
                height: 75,
                child: ElevatedButton(
                  onPressed: () => handleLogin(context),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.all(20),
                  ),
                  child: const Text(
                    "Login",
                    style: TextStyle(fontSize: 25, fontWeight: FontWeight.bold),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
