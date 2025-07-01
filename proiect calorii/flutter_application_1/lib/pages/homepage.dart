import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}



class _HomePageState extends State<HomePage> {

  final _foodController = TextEditingController();
  final _grameController=TextEditingController();

  String mancare ='';
  String grame='';
  String calorii = '';
  String test = "";

  String apiResult='';
  
   Color _buttonColor = Colors.purple;

  void _changeButtonColor(Color color) {
    setState(() {
      _buttonColor = color;
    });
  }
  
  Future<void> Istoric() async {
  final url = Uri.parse('http://127.0.0.1:8000/istoric');

  try {
    final response = await http.get(url);
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);

      showDialog(
        context: context,
        builder: (context) {
          return AlertDialog(
            title: const Text('Istoric Calorii'),
            content: SizedBox(
              width: double.maxFinite,
              child: ListView.builder(
                shrinkWrap: true,
                itemCount: data.length,
                itemBuilder: (context, index) {
                  final item = data[index];
                  return ListTile(
                    title: Text("${item['food']}"),
                    subtitle: Text("${item['gramaj']}g - ${item['kcal']} kcal"),
                  );
                },
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text("Închide"),
              )
            ],
          );
        },
      );
    } else {
      _showError("Eroare la API (cod ${response.statusCode})");
    }
  } catch (e) {
    _showError("Eroare: $e");
  }
}

void _showError(String message) {
  showDialog(
    context: context,
    builder: (context) => AlertDialog(
      title: const Text("Eroare"),
      content: Text(message),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text("OK"),
        )
      ],
    ),
  );
}

String fetchMessage(String test){
  if (test.contains("Eroare"))
  {
    test = "A aparut o eroare";
    return test;
  }
  else
  {
    test= "${mancare} are ${apiResult} calorii";
    return test;
  }
}

  Future<void> Calculeaza () async{
    final food = mancare;
    final grams = grame;
    test="";

    if ( food.isEmpty || grams.isEmpty){
      setState(() {
        apiResult = 'Nu ai pus ambele';
      });
      return;  
    }

      
    
    final url = Uri.parse('http://127.0.0.1:8000/calculeaza');

    try { 
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'name': food, 'grams': double.parse(grams)}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          apiResult = data['calorii']?.toString() ?? '--------';
        });
      }
      else {
        setState(() {
          apiResult = 'Eroare';
          test = apiResult;
          fetchMessage(test);
        });
      }

    }catch (e) {
      setState(() {
        apiResult = 'cv nu  ebn $e';
      });
    }

  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(

      appBar: AppBar(title: const Text('Sidebar')),
      drawer: Drawer(
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            const DrawerHeader(
              decoration: BoxDecoration(color: Colors.purple),
              child:Center(
              child: Text('APLICATIE CALCULAT CALORII',style: TextStyle(fontSize: 30),),),
            
              ),
              ListTile(
                title: const Text('Red'),
                onTap: (){
                  _changeButtonColor(Colors.red);
                },
              ),
              ListTile(
                title: const Text('Purple'),
                onTap: (){
                  _changeButtonColor(Colors.purple);
                },
              ),
              ListTile(
                title: const Text('ISTORIC'),
                onTap:(){
                  Istoric();
                }
              )

              
          ],
        ),
      ),

      body:Padding(

        padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 100.0),
          child: Column(
            spacing:50,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              
              Expanded(
                child: Container(
                  child:Center(
                    child:Text(
                      fetchMessage(test),style: TextStyle(fontSize: 30)
                      ),
                  ),
                ),
              ),
              
              // text input
              TextField(
                controller: _foodController,
                decoration: InputDecoration(
                  hintText: 'food',
                  border: OutlineInputBorder(),
                  suffixIcon: IconButton(
                    onPressed:() {
                      //
                      _foodController.clear();
                    },
                    icon: const Icon(Icons.clear),
                  ),
                  
                )
              ),
              TextField(
                controller: _grameController,
                decoration: InputDecoration(
                  hintText: 'grame',
                  border:OutlineInputBorder(),
                  suffixIcon: IconButton(
                    onPressed: (){
                      _grameController.clear();
                    },
                    icon: const Icon(Icons.clear),
                    ),
                ),
              ),


              //buton
              MaterialButton(
                onPressed: () {

                  //pun textu in variabila
                  setState(() {
                    mancare = _foodController.text;
                    grame=_grameController.text;

                    

                    _foodController.clear();
                    _grameController.clear();
                  });
                  
                  Calculeaza();
                },
                color:_buttonColor,
                child: const Text('Calculeaza',style: TextStyle(color:Colors.white),),
                ),
              ],
            )
          )
        );
  }
}