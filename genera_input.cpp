#include <iostream>
#include <fstream>
#include <random> 
#include <iomanip>

using namespace std;

int main(int argc, char* argv[]) {
    if (argc < 2) {
        cout << "Uso: ./genera [dimensione]" << endl;
        return 1;
    }

    int dim = atoi(argv[1]);

    // Ottimizzazione per velocizzare enormemente le stampe e le scritture (I/O)
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    ofstream outfile("input.txt");

    // === Motore C++11 Mersenne Twister per numeri casuali di alta qualità ===
    random_device rd;  // Seme basato sull'hardware
    mt19937 gen(rd()); // Generatore moderno
    uniform_real_distribution<float> dis(0.0f, 1.0f); // Distribuzione uniforme tra 0 e 1

    cout << "Generazione file input.txt (Float) in corso... (" << dim << "x" << dim << " pixel)" << endl;

    for (int i = 0; i < dim * dim; i++) {
        // Genera e stampa direttamente il numero
        outfile << fixed << setprecision(4) << dis(gen) << " "; 
        
        // Va a capo alla fine di ogni riga
        if ((i + 1) % dim == 0) {
            outfile << "\n";
        }
    }

    outfile.close();
    cout << "✅ Fatto! File input.txt di " << dim << "x" << dim << " creato con successo." << endl;
    
    return 0;
}