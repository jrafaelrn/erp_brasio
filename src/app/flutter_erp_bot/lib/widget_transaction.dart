// ignore_for_file: prefer_const_constructors
import 'package:flutter/material.dart';



class Transaction extends StatefulWidget {
  
  final Color? primaryColor, secondColor;
  const Transaction({super.key, this.primaryColor, this.secondColor});

  @override
  State<Transaction> createState() => _TransactionState();

}




class _TransactionState extends State<Transaction> {
  
  @override
  Widget build(BuildContext context) {
 
    return ClipRRect(

      borderRadius: BorderRadius.circular(10),

      child: Container(
    
        color: widget.secondColor,
        width: 0.9 * MediaQuery.of(context).size.width,
    
        child: Row(
          
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
    
            Padding(
              padding: const EdgeInsets.only(left: 10.0),              
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Data:'),
                  SizedBox(height: 10),
                  Text('Conta:'),
                  SizedBox(height: 10),
                  Text('Categoria:'),
                  SizedBox(height: 10),
                  Text('Fornecedor:'),
                  SizedBox(height: 10),
                  Text('Tipo:'),
                ],
              ),
            ),
    
            Padding(
              padding: const EdgeInsets.only(left: 20.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('01/01/2021', style: TextStyle(fontWeight: FontWeight.bold)),
                  SizedBox(height: 10),
                  Text('Conta Corrente', style: TextStyle(fontWeight: FontWeight.bold)),
                  SizedBox(height: 10),
                  Text('Alimentação', style: TextStyle(fontWeight: FontWeight.bold)),
                  SizedBox(height: 10),
                  Text('Mercado', style: TextStyle(fontWeight: FontWeight.bold)),
                  SizedBox(height: 10),
                  Text('Débito', style: TextStyle(fontWeight: FontWeight.bold)),
                ],
              ),
            ),
    
            Padding(
              padding: const EdgeInsets.only(left: 100),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Valor:'),
                  SizedBox(height: 10),
                  Text('Descrição:'),
                  SizedBox(height: 10),
                  Text('Status:'),
                ],
              ),
            ),
    
            Padding(
              padding: const EdgeInsets.only(left: 20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('R\$ 100,00', style: TextStyle(fontWeight: FontWeight.bold)),
                  SizedBox(height: 10),
                  Text('Compra de alimentos', style: TextStyle(fontWeight: FontWeight.bold)),
                  SizedBox(height: 10),
                  Text('Pago', style: TextStyle(fontWeight: FontWeight.bold)),
                ],
              ),
            ),
          
          ],
    
        ),
      ),
    );
  }

}