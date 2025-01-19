import tkinter as tk
from tkinter import ttk, messagebox
import time

class Processo:
    def __init__(self, id, chegada, execucao, deadline, sobrecarga, paginas):
        self.id = id
        self.chegada = chegada
        self.execucao = execucao
        self.deadline = deadline
        self.sobrecarga = sobrecarga
        self.paginas = paginas
        self.tempo_restante = execucao
        self.inicio = None
        self.fim = None
        self.concluido = False
        self.tempo_espera = 0

class Simulador:
    def __init__(self, master):
        self.master = master
        master.title("Simulador de Escalonamento")

        # Labels e Entradas
        ttk.Label(master, text="Número de Processos:").grid(row=0, column=0, sticky="w")
        self.num_processes_entry = ttk.Entry(master)
        self.num_processes_entry.grid(row=0, column=1, sticky="w")

        ttk.Button(master, text="Adicionar Processos", command=self.create_process_input_fields).grid(row=0, column=2, sticky="w")
        
         # Frame para os inputs de cada processo
        self.processes_frame = ttk.Frame(master)
        self.processes_frame.grid(row=1, column=0, columnspan=3, sticky="w")
        
        ttk.Label(master, text="Algoritmo:").grid(row=2, column=0, sticky="w")
        self.algorithm_combobox = ttk.Combobox(master, values=["FIFO", "SJF", "Round Robin", "EDF"])
        self.algorithm_combobox.grid(row=2, column=1, sticky="w")

        ttk.Label(master, text="Quantum (Round Robin):").grid(row=2, column=2, sticky="w")
        self.quantum_entry = ttk.Entry(master)
        self.quantum_entry.insert(0, "2") # Valor default
        self.quantum_entry.grid(row=2, column=3, sticky="w")

        ttk.Button(master, text="Iniciar Simulação", command=self.start_simulation).grid(row=3, column=0, columnspan=4, pady=10)
        
        # Canvas para o Gráfico de Gantt
        self.gantt_canvas = tk.Canvas(master, width=1000, height=400, bg="white")
        self.gantt_canvas.grid(row=4, column=0, columnspan=4, sticky="w", padx=10, pady=10)

        self.cpu_usage_label = ttk.Label(master, text="Uso da CPU:")
        self.cpu_usage_label.grid(row=5, column=0, columnspan=4, sticky="w", padx=10)
        self.cpu_usage_text = tk.Text(master, height=10, width=80)
        self.cpu_usage_text.grid(row=6, column=0, columnspan=4, sticky="w", padx=10)
        
        self.turnaround_label = ttk.Label(master, text="Turnaround Médio:")
        self.turnaround_label.grid(row=7, column=0, columnspan=4, sticky="w", padx=10)
        self.turnaround_text = ttk.Label(master, text="")
        self.turnaround_text.grid(row=8, column=0, columnspan=4, sticky="w", padx=10)
        
        self.processos = []
        self.process_input_fields = []
        self.timeline = []
        self.process_start_time = {}
        self.animation_running = False
        
    def create_process_input_fields(self):
      try:
            num_processes = int(self.num_processes_entry.get())
      except ValueError:
           messagebox.showerror("Erro", "Por favor, insira um número inteiro válido.")
           return

      # Apaga os campos de processos anteriores
      for widget in self.processes_frame.winfo_children():
            widget.destroy()
      self.process_input_fields = []
      
      for i in range(num_processes):
          process_frame = ttk.Frame(self.processes_frame)
          process_frame.pack(fill='x', padx=5, pady=2)
          
          ttk.Label(process_frame, text=f"Processo {i+1}:").pack(side='left', padx=5)

          fields = {
              "Chegada": ("entry", "0"),
                "Execução": ("entry", "1"),
                "Deadline": ("entry", "10"),
               "Sobrecarga": ("entry", "0"),
               "Páginas": ("entry", "1")
          }
          
          input_fields = {}
          for label, (widget_type, default_value) in fields.items():
              ttk.Label(process_frame, text=f"{label}:").pack(side='left', padx=5)
              
              if widget_type == "entry":
                 entry = ttk.Entry(process_frame)
                 entry.insert(0, default_value)
                 entry.pack(side='left', padx=5)
                 input_fields[label] = entry
              
          self.process_input_fields.append(input_fields)

    def collect_process_data(self):
        self.processos = []
        for i, fields in enumerate(self.process_input_fields):
              try:
                chegada = int(fields["Chegada"].get())
                execucao = int(fields["Execução"].get())
                deadline = int(fields["Deadline"].get())
                sobrecarga = int(fields["Sobrecarga"].get())
                paginas = int(fields["Páginas"].get())
                
                processo = Processo(i + 1, chegada, execucao, deadline, sobrecarga, paginas)
                self.processos.append(processo)
              except ValueError:
                messagebox.showerror("Erro", "Por favor, preencha todos os campos com valores inteiros válidos.")
                return None
        return self.processos

    def start_simulation(self):
        if self.animation_running:
           return
        self.animation_running = True

        self.processos = self.collect_process_data()
        if self.processos is None:
          self.animation_running = False
          return
          
        self.process_start_time = {}  # Reseta o registro de startTime
        self.timeline = []
        self.gantt_canvas.delete("all") # Limpa o canvas antigo
        self.cpu_usage_text.delete("1.0", tk.END)
        self.turnaround_text.config(text="")
        
        algoritmo = self.algorithm_combobox.get()
        quantum = int(self.quantum_entry.get())
        
        if algoritmo == "FIFO":
            self.simulate_fifo(0)
        elif algoritmo == "SJF":
            self.simulate_sjf(0)
        elif algoritmo == "Round Robin":
             self.simulate_round_robin(0, quantum)
        elif algoritmo == "EDF":
            self.simulate_edf(0, quantum)
        else:
            messagebox.showerror("Erro", "Selecione um algoritmo.")
            self.animation_running = False

    def simulate_fifo(self, current_time):
        processos_ordenados = sorted(self.processos, key=lambda p: p.chegada)
        
        if all(p.concluido for p in processos_ordenados):
             self.calculate_and_update_results(processos_ordenados)
             self.animation_running = False
             return

        processo = next((p for p in processos_ordenados if not p.concluido), None)
        
        if processo:
            if current_time < processo.chegada:
                self.create_gantt_bar(processo.id, current_time, processo.chegada, "wait", processo.inicio)
                current_time = processo.chegada

            processo.inicio = current_time
            current_time += processo.execucao
            processo.fim = current_time
            
            self.create_gantt_bar(processo.id, processo.inicio, processo.fim, "execucao", processo.inicio)
                        
            processo.concluido = True
            
            self.master.after(500, lambda: self.simulate_fifo(current_time))
    
    def simulate_sjf(self, current_time):
         processos_restantes = [p for p in self.processos if not p.concluido]
         
         if not processos_restantes:
              self.calculate_and_update_results(self.processos)
              self.animation_running = False
              return

         processos_disponiveis = [p for p in processos_restantes if p.chegada <= current_time]
          
         if not processos_disponiveis:
              self.master.after(500, lambda: self.simulate_sjf(current_time + 1))
              return
        
         processo = min(processos_disponiveis, key=lambda p: p.execucao)

         if current_time < processo.chegada:
            self.create_gantt_bar(processo.id, current_time, processo.chegada, "wait", processo.inicio)
            current_time = processo.chegada

         processo.inicio = current_time
         current_time += processo.execucao
         processo.fim = current_time
         self.create_gantt_bar(processo.id, processo.inicio, processo.fim, "execucao", processo.inicio)
               
         processo.concluido = True
        
         self.master.after(500, lambda: self.simulate_sjf(current_time))

    def simulate_round_robin(self, current_time, quantum):
        # Inicializar tempo de espera para cada processo
        for processo in self.processos:
            if not hasattr(processo, 'tempo_espera'):
                processo.tempo_espera = 0

        # Incrementar tempo de espera de processos que não estão sendo executados
        for processo in self.processos:
            if processo.chegada <= current_time and not processo.concluido and processo.tempo_restante > 0:
                processo.tempo_espera += 1

        # Selecionar o processo com maior tempo de espera disponível
        processo = max(
            (p for p in self.processos if p.chegada <= current_time and not p.concluido and p.tempo_restante > 0),
            key=lambda p: p.tempo_espera,
            default=None
        )

        # Verificar se há processos disponíveis para execução
        if processo is None:
            if all(p.concluido for p in self.processos):  # Todos os processos concluídos
                self.calculate_and_update_results(self.processos)
                self.animation_running = False
                return
            else:  # Aguardar o próximo instante
                self.master.after(500, lambda: self.simulate_round_robin(current_time + 1, quantum))
                return

        # Zerar o tempo de espera do processo selecionado
        processo.tempo_espera = 0

        # Determinar o tempo de execução
        executar_tempo = min(quantum, processo.tempo_restante)
        start = current_time
        current_time += executar_tempo
        processo.tempo_restante -= executar_tempo

        # Definir o tempo de início do processo, se necessário
        if processo.inicio is None:
            processo.inicio = start

        # Criar barra de execução no gráfico de Gantt
        self.create_gantt_bar(processo.id, start, current_time, 'execucao', processo.inicio)

        # Verificar se o processo foi concluído
        if processo.tempo_restante <= 0:
            processo.fim = current_time
            processo.concluido = True
        else:
            # Aplicar sobrecarga
            if processo.sobrecarga > 0:
                sobrecarga_inicio = current_time
                current_time += processo.sobrecarga
                self.create_gantt_bar(processo.id, sobrecarga_inicio, current_time, 'sobrecarga', processo.inicio)

        # Incrementar tempo de espera de todos os outros processos
        for p in self.processos:
            if p != processo and p.chegada <= current_time and not p.concluido and p.tempo_restante > 0:
                p.tempo_espera += current_time - start

        # Chamar a próxima execução
        self.master.after(500, lambda: self.simulate_round_robin(current_time, quantum))





       
    def simulate_edf(self, current_time, quantum):
      queue = [p for p in self.processos if not p.concluido]
      if not queue:
            self.calculate_and_update_results(self.processos)
            self.animation_running = False
            return
      
        # Filtrar processos que ja chegaram
      queue = [p for p in queue if p.chegada <= current_time]
        
       # Caso todos os processos ainda não tenham chegado espera
      if not queue:
           self.master.after(500, lambda: self.simulate_edf(current_time + 1, quantum))
           return

      queue.sort(key=lambda p: p.deadline)
      processo = queue[0]
     
      if current_time < processo.chegada and not processo.concluido:
         self.create_gantt_bar(processo.id, current_time, processo.chegada, 'wait', processo.inicio)
         current_time = processo.chegada
         
      execute_time = min(quantum, processo.tempo_restante)
      start = current_time
      current_time += execute_time
      processo.tempo_restante -= execute_time
      
      if processo.inicio is None:
         processo.inicio = start;
    
      self.create_gantt_bar(processo.id, start, current_time, 'execucao', processo.inicio)

      if processo.tempo_restante <= 0:
           processo.fim = current_time
           processo.concluido = True
           queue.pop(0)
      else:
           if processo.sobrecarga > 0:
              sobrecarga_inicio = current_time
              current_time += processo.sobrecarga
              self.create_gantt_bar(processo.id, sobrecarga_inicio, current_time, 'sobrecarga', processo.inicio)
           queue.pop(0)
           queue.insert(0, processo)
       
      self.master.after(500, lambda: self.simulate_edf(current_time, quantum))

    def create_gantt_bar(self, process_id, start, end, tipo, start_time):
        if not start_time or process_id not in self.process_start_time:
            self.process_start_time[process_id] = start
          
        start = self.process_start_time[process_id]
        
        largura = (end - start) * 50
        x0 = start * 50
        y0 = (process_id - 1) * 40 + 20 # Ajustar para posicionamento vertical
        x1 = x0 + largura
        y1 = y0 + 30
        
        if tipo == "execucao":
            cor = "green"
        elif tipo == "wait":
            cor = "yellow"
        elif tipo == "sobrecarga":
            cor = "red"
        else:
            cor = "gray"
        
        self.gantt_canvas.create_rectangle(x0, y0, x1, y1, fill=cor, tags=f"processo_{process_id}")
        self.gantt_canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=f"P{process_id} ({start}-{end})", tags=f"processo_{process_id}")
        self.gantt_canvas.config(scrollregion=self.gantt_canvas.bbox("all"))
    
    def calculate_and_update_results(self, processos):
        turnaround_total = sum((p.fim - p.chegada) for p in processos)
        turnaround_medio = turnaround_total / len(processos) if processos else 0
        self.turnaround_text.config(text=f"{turnaround_medio:.2f}")

         # Cálculo do uso da CPU
        max_time = max((p.fim for p in processos), default=0)
        cpu_usage_data = {}
        for time in range(max_time+1):
            utilization = 0
            for p in processos:
                if p.inicio is not None and time >= p.inicio and time < p.fim :
                    utilization += 1
            cpu_usage_data[time] = utilization

        # Formatação da string de uso da CPU
        cpu_usage_str = "\n".join(f"Tempo: {time}, CPU: {usage}" for time, usage in cpu_usage_data.items())
        self.cpu_usage_text.insert(tk.END, cpu_usage_str)

if __name__ == "__main__":
    root = tk.Tk()
    simulador = Simulador(root)
    root.mainloop()