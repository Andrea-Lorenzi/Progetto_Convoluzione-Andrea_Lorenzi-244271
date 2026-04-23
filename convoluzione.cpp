#include <iostream>
#include <omp.h>
#include <vector>
#include <chrono>
#include <iomanip>
#include <cstdlib>
#include <string>

using namespace std;

// Variabili globali
float *immagine; 
float *output;   
float kernel[4][4];
int IMG_SIZE;
int NUM_THREAD;

int main(int argc, char* argv[]) {
    // Modalità: P (Parallelo) o S (Sequenziale)
    if (argc < 5) { 
        cout << "Uso: ./conv [dimensione] [thread] [schedule] [mode: P/S]" << endl;
        cout << "Mode: P = Parallelo (OpenMP), S = Sequenziale puro" << endl;
        return 1;
    }

    IMG_SIZE = atoi(argv[1]); 
    NUM_THREAD = atoi(argv[2]); 
    string tipo_schedule = argv[3]; 
    char mode = argv[4][0]; // P (Parallelo) o S (Sequenziale)

    immagine = new float[IMG_SIZE * IMG_SIZE];
    output = new float[IMG_SIZE * IMG_SIZE];

    // Inizializzazione
    for(int i = 0; i < IMG_SIZE * IMG_SIZE; i++) immagine[i] = 1.0f;
    for(int i = 0; i < 4; i++) {
        for(int j = 0; j < 4; j++) kernel[i][j] = 1.0f;
    }

    double tempo_esecuzione = 0.0;

    if (mode == 'P') {
        
        // --- MODALITÀ PARALLELA (Con OpenMP) ---
        omp_set_num_threads(NUM_THREAD);

        if (tipo_schedule == "static") {
            omp_set_schedule(omp_sched_static, 0); 
        } else if (tipo_schedule == "dynamic") {
            omp_set_schedule(omp_sched_dynamic, 16); 
        } else if (tipo_schedule == "guided") {
            omp_set_schedule(omp_sched_guided, 0);
        } else {
            omp_set_schedule(omp_sched_static, 0);
        }

        auto start_par = chrono::high_resolution_clock::now();

        // Blocco parallelo: ogni thread calcola una porzione dell'immagine di output
        #pragma omp parallel for default(none) shared(immagine, output, kernel, IMG_SIZE) schedule(runtime)
        for (int i = 0; i < IMG_SIZE; i++) {
            for (int j = 0; j < IMG_SIZE; j++) {
                float somma = 0.0f; // somma è dichiarata DENTRO il ciclo, quindi è automaticamente PRIVATA per ogni thread
                for (int ki = 0; ki < 4; ki++) {
                    for (int kj = 0; kj < 4; kj++) {
                        int riga_p = i + ki;
                        int col_p = j + kj;
                        if (riga_p < IMG_SIZE && col_p < IMG_SIZE) {
                            somma += immagine[riga_p * IMG_SIZE + col_p] * kernel[ki][kj];
                        }
                    }
                }
                output[i * IMG_SIZE + j] = somma;
            }
        }

        auto end_par = chrono::high_resolution_clock::now();
        tempo_esecuzione = chrono::duration<double>(end_par - start_par).count();

    } else {

        // --- MODALITÀ SEQUENZIALE ---
       
        auto start_seq = chrono::high_resolution_clock::now();

        for (int i = 0; i < IMG_SIZE; i++) { //Non c'è parallelismo, quindi non serve specificare nulla
            for (int j = 0; j < IMG_SIZE; j++) {
                float somma = 0.0f; 
                for (int ki = 0; ki < 4; ki++) {
                    for (int kj = 0; kj < 4; kj++) {
                        int riga_p = i + ki;
                        int col_p = j + kj;
                        if (riga_p < IMG_SIZE && col_p < IMG_SIZE) {
                            somma += immagine[riga_p * IMG_SIZE + col_p] * kernel[ki][kj];
                        }
                    }
                }
                output[i * IMG_SIZE + j] = somma;
            }
        }

        auto end_seq = chrono::high_resolution_clock::now();
        tempo_esecuzione = chrono::duration<double>(end_seq - start_seq).count();
    }

    cout << "Tempo (" << (mode == 'P' ? "Parallelo" : "Sequenziale") << ") = " 
         << fixed << setprecision(6) << tempo_esecuzione << endl;

    delete[] immagine;
    delete[] output;

    return 0;
}