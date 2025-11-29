import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  final String baseUrl = "http://192.168.5.38:8000"; // IP del backend de Python

  // GET PARKING
  Future<List<dynamic>> getParkingSlots() async {
    final response = await http.get(Uri.parse("$baseUrl/parking"));
    return jsonDecode(response.body);
  }

  // REGISTER USER
  Future<Map<String, dynamic>> registerUser({
    required String name,
    required String email,
    required String password,
  }) async {
    final url = Uri.parse("$baseUrl/register");

    final body = jsonEncode({
      "name": name,
      "email": email,
      "password": password,
    });

    final response = await http.post(
      url,
      headers: {"Content-Type": "application/json"},
      body: body,
    );

    return {
      "status": response.statusCode,
      "data": jsonDecode(response.body),
    };
  }

  // LOGIN USER
  Future<Map<String, dynamic>> loginUser({
    required String email,
    required String password,
  }) async {
    final url = Uri.parse("$baseUrl/login");

    final body = jsonEncode({
      "email": email,
      "password": password,
    });

    final response = await http.post(
      url,
      headers: {"Content-Type": "application/json"},
      body: body,
    );

    return {
      "status": response.statusCode,
      "data": jsonDecode(response.body),
    };
  }
}
