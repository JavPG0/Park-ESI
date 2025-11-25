import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  final String baseUrl = "http://192.168.1.12:8000"; // IP del backend de Python

  Future<List<dynamic>> getVehicles() async {
    final response = await http.get(Uri.parse("$baseUrl/results"));
    return jsonDecode(response.body);
  }

  Future<List<dynamic>> getParkingSlots() async {
    final response = await http.get(Uri.parse("$baseUrl/parking"));
    return jsonDecode(response.body);
  }
}
