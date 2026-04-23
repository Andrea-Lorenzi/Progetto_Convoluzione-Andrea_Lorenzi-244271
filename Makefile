CXX = g++
CXXFLAGS = -Wall -O3 -fopenmp
LDFLAGS = -fopenmp
TARGET = conv
GEN_TARGET = genera

# Impostazioni Test: 100 Iterazioni
ITERATIONS = 100

.PHONY: all test init_log clean

all: $(TARGET) $(GEN_TARGET)

$(TARGET): convoluzione.cpp
	$(CXX) $(CXXFLAGS) convoluzione.cpp -o $(TARGET) $(LDFLAGS)

$(GEN_TARGET): genera_input.cpp
	$(CXX) -Wall -O3 genera_input.cpp -o $(GEN_TARGET)

init_log:
	@echo "Pulizia vecchi file e inizializzazione report..."
	@rm -f input.txt output.txt performance_log.csv temp_runs.txt
	@echo "Dimensione,Thread,Schedule,Variabili,Tempo_Seq(s),Tempo_Par(s),Varianza,Deviazione_Standard,Speedup" > performance_log.csv

test: all init_log
	@echo "=================================================="
	@echo "AVVIO TEST STATISTICO COMPLETO"
	@echo "=================================================="
	@dim=512; while [ $$dim -le 4096 ]; do \
		echo ""; \
		echo "██████████████████████████████████████████████████"; \
		echo ">>> ANALISI MATRICE $$dim x $$dim <<<"; \
		echo "██████████████████████████████████████████████████"; \
		for sched in static dynamic guided; do \
			for mode in P S; do \
				SEQ_TIME=0; \
				for t in 1 4 8 16 32 64 128; do \
					echo -n "Esecuzione Dim:$$dim, Thread:$$t, Sched:$$sched, Var:$$mode... "; \
					rm -f temp_runs.txt; \
					for i in $$(seq 1 $(ITERATIONS)); do \
						./$(TARGET) $$dim $$t $$sched $$mode | grep "Tempo" | awk -F'=' '{print $$2}' | tr -d 's ' >> temp_runs.txt; \
					done; \
					echo -n "Calcolo statistiche... "; \
					STATS=$$(awk '{sum+=$$1; sumsq+=$$1*$$1; n++} END { \
						if (n > 0) { \
							m=sum/n; v=(sumsq/n)-(m*m); \
							printf "%.6f,%.9f,%.9f", m, v, sqrt(v); \
						} else { \
							printf "ERROR,ERROR,ERROR"; \
						} \
					}' temp_runs.txt); \
					MEAN=$$(echo $$STATS | cut -d',' -f1); \
					VAR=$$(echo $$STATS | cut -d',' -f2); \
					STD=$$(echo $$STATS | cut -d',' -f3); \
					if [ "$$t" = "1" ]; then \
						SEQ_TIME=$$MEAN; \
						SPEEDUP="1.00"; \
					else \
						if [ "$$MEAN" = "ERROR" ]; then \
							SPEEDUP="ERROR"; \
						else \
							SPEEDUP=$$(awk -v seq="$$SEQ_TIME" -v par="$$MEAN" 'BEGIN { printf "%.2f", seq/par }'); \
						fi; \
					fi; \
					echo "$$dim,$$t,$$sched,$$mode,$$SEQ_TIME,$$MEAN,$$VAR,$$STD,$${SPEEDUP}x" >> performance_log.csv; \
					echo "OK. (Speedup: $${SPEEDUP}x)"; \
				done; \
			done; \
		done; \
		dim=$$((dim * 2)); \
	done
	@rm -f temp_runs.txt
	@echo ""
	@echo "=================================================="
	@echo "TEST COMPLETATO CON SUCCESSO!"
	@echo "I dati finali sono in: performance_log.csv"
	@echo "=================================================="

clean:
	rm -f $(TARGET) $(GEN_TARGET) output.txt input.txt performance_log.csv temp_runs.txt