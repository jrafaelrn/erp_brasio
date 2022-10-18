import 'package:flutter/material.dart';


class PaymentAutoClassification extends StatefulWidget {

  final Color? primaryColor, secondColor;
  const PaymentAutoClassification({super.key, this.primaryColor, this.secondColor});

  @override
  State<PaymentAutoClassification> createState() => _PaymentAutoClassificationState();
}

class _PaymentAutoClassificationState extends State<PaymentAutoClassification> {
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