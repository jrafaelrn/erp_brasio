import 'package:flutter/material.dart';

class ErpPendentPayment extends StatefulWidget {

  final Color? primaryColor, secondColor;
  const ErpPendentPayment({super.key, this.primaryColor, this.secondColor});

  @override
  State<ErpPendentPayment> createState() => _ErpPendentPaymentState();
}

class _ErpPendentPaymentState extends State<ErpPendentPayment> {
  @override
  Widget build(BuildContext context) {
    
    return ClipRRect(

      borderRadius: BorderRadius.circular(10),

      child: Container(

        color: widget.secondColor,
        width: 0.9 * MediaQuery.of(context).size.width,

        child: Column(

          children: [
            Text('Teste'),
          ],



        ),

      ),

    );
  }
}