Tomara Que Caia

O código Tomara que Caia é um ataque de negação de serviço, utilizando o método "Low and Slow".

O código funciona da seguinte forma:

Começamos a fazer muitas solicitações HTTP.

Enviamos cabeçalhos periodicamente para manter as conexões abertas.

Nunca fechamos a conexão, a menos que o servidor o faça. Se o servidor fechar uma conexão, criamos uma nova e continuamos fazendo a mesma coisa.

Isso esgota o pool de threads do servidor e o servidor não consegue responder a outras pessoas.



![Screenshot 2024-06-15 225555](https://github.com/Angryduckling1337UP/tomaraquecaia3.0/assets/168230894/66185182-5775-4d68-b5ea-16fda31e8bff)


Instalações necessária para o funcionamento :

 -argparse
 
-logging
 
 -random
 
 -sys
 
 -threading
 
 -time
 
 -requests
 
 -requests.adapters import HTTPAdapter
 
 -urllib3.util.retry import Retry
 
 -pyfiglet
 
 -termcolor import colored

 Instalação:
 
git clone https://github.com/Angryduckling1337UP/tomaraquecaia3.0.git

Caso for executar no linux :

dos2unix tomaraquecaia3.0.py
 


 
