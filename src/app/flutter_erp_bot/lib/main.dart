import 'package:flutter/material.dart';
import 'home_page.dart';

// Constantes - Depois pegar do BD
const primaryColor = Color(0xFF62382B);
const secondColor = Color(0xFFE2CDBA);



void main() {
  runApp(const MyApp());
}


class MyApp extends StatelessWidget {

  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    
    return MaterialApp(
      title: 'Lua',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSwatch().copyWith(
          primary: primaryColor,
          secondary: secondColor,
        ),
      ),
      home: const MyHomePage(title: 'Lua & Palhadini', primaryColor: primaryColor, secondColor: secondColor),
    );
  }

}
