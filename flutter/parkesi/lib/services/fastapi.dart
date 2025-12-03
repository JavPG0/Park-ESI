import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  final String baseUrl = "http://192.168.1.12:8000"; // IP local
  //uvicorn src.api:app --host 192.168.1.12 --port 8000

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
    final url = Uri.parse("$baseUrl/register/user");

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

  // DELETE USER
  Future<bool> deleteUser(String email) async {
    final url = Uri.parse("$baseUrl/delete/user");

    final response = await http.post(
      url,
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"email": email}),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Error al borrar el usuario: ${response.body}");
    }
  }

  // REGISTER VEHICLE
  Future<Map<String, dynamic>> registerVehicle({
    required String email,
    required String plate,
    required String color,
    required String brand,
    required bool shared,
  }) async {
    final url = Uri.parse("$baseUrl/register/vehicle");

    final body = jsonEncode({
      "email": email,
      "plate": plate,
      "color": color,
      "brand": brand,
      "shared": shared,
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

  // GET VEHICLES
  Future<List<dynamic>> getVehicles(String email) async {
    final url = Uri.parse("$baseUrl/consult");

    final response = await http.post(
      url,
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"email": email}),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Error al consultar vehículos: ${response.body}");
    }
  }

  // DELETE VEHICLE
  Future<bool> deleteVehicle(String plate) async {
    final url = Uri.parse("$baseUrl/delete/vehicle");

    final response = await http.post(
      url,
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"plate": plate}),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Error al borrar el vehículo: ${response.body}");
    }
  }
}
