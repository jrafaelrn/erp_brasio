
import 'package:flutter/material.dart';
import 'widget_transaction.dart';
import 'widget_erp.dart';
import 'widget_auto_classification.dart';



class MyHomePage extends StatefulWidget {
  
  const MyHomePage({super.key, required this.title, this.primaryColor, this.secondColor});
  final String title;
  final Color? primaryColor, secondColor;


  @override
  State<MyHomePage> createState() => _MyHomePageState();

}



class _MyHomePageState extends State<MyHomePage> {
  
  int _counter = 0;

  void _incrementCounter() {
    setState(() {
      _counter++;
    });
  }

  @override
  Widget build(BuildContext context) {
    // This method is rerun every time setState is called, for instance as done
    // by the _incrementCounter method above.
    //
    // The Flutter framework has been optimized to make rerunning build methods
    // fast, so that you can just rebuild anything that needs updating rather
    // than having to individually change instances of widgets.
    return Scaffold(
      
      appBar: AppBar(
        title: Text(widget.title),
      ),
      
      body: Center(

        child: Column(

          mainAxisAlignment: MainAxisAlignment.center,
          children: [

            Transaction(primaryColor: widget.primaryColor, secondColor: widget.secondColor),
            SizedBox(height: 40),
            
            Row(
              children: [
                ErpPendentPayment(primaryColor: widget.primaryColor, secondColor: widget.secondColor),
                SizedBox(width: 40),
                PaymentAutoClassification(),
              ],
            ),

          ]
        ),
      ),
      
      floatingActionButton: FloatingActionButton(
        onPressed: _incrementCounter,
        tooltip: 'Increment',
        child: const Icon(Icons.add),
      ), 

    );
  }
}
