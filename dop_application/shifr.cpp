#include <iostream>
#include <string>
#include <cstring>

//using std::literals::string_literals::operator""s;

char to_symbol_char(const char ch) noexcept{
	return (ch % 10) + 48;
}

std::string shifrovanie(const char str[]) noexcept{
	long len = std::strlen(str);

	std::string ret(str);

	// Первая кодировка
	if(len > 4){
		std::swap(ret[0], ret[3]);

		// Шифр Цезаря
		if(len > 7){
			for(int i = 4; i < 7; ++i){
				ret[i] = to_symbol_char(ret[i] + i);
			}


			// Комбинация перестановки + Цезарь
			if(len > 9){
				std::swap(ret[1], ret[9]);
				ret[9] = to_symbol_char(ret[9] - 8);

			
				//+ На биективное под мн-во.
				//Маска
				if(len > 11){
					ret.push_back(to_symbol_char(str[2] ^ ( (str[7] % (1 << 4)) >> 1)));
				}
			}
		}
	}

	return ret;
}


int main(int argc, char* argv[]){

	//if(argc <= 1)
	//	return 1; // Ошибка выполнения

	for(int i = 1; i < argc; ++i){
		std::cout << shifrovanie(argv[i]) << ' ';
	}

	return 0;
}
