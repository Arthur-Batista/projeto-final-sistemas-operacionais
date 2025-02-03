import tkinter as tk
from tkinter import ttk, messagebox

class Processo:
    def __init__(self, id, chegada, execucao, deadline, paginas):
        self.id = id
        self.chegada = chegada
        self.execucao = execucao
        self.deadline = deadline
        self.paginas = paginas
        self.tempo_restante = execucao
        self.inicio = None
        self.fim = None
        self.concluido = False
        self.tempo_espera = 0

class SlotPagina:
    def __init__(self, slot, pagina, chegada, uso):
        self.slot = slot
        self.pagina = pagina
        self.chegada = chegada
        self.uso = uso

class Simulador:
    def __init__(self, master):
        self.master = master
        master.title("Simulador de Escalonamento")
        master.geometry("1200x700")  # Define o tamanho inicial da janela

        # Criar um Canvas e Scrollbar para a janela principal
        self.main_canvas = tk.Canvas(master)
        self.main_canvas.pack(side="left", fill="both", expand=True)

        self.main_scrollbar = ttk.Scrollbar(master, orient="vertical", command=self.main_canvas.yview)
        self.main_scrollbar.pack(side="right", fill="y")

        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)

        # Criar um frame dentro do Canvas para conter os widgets
        self.main_frame = ttk.Frame(self.main_canvas)
        self.main_canvas.create_window((0, 0), window=self.main_frame, anchor="n")
        
        # Labels e Entradas (usando main_frame como o frame pai)
        ttk.Label(self.main_frame, text="Número de Processos:").grid(row=0, column=0, sticky="w")
        self.num_processes_entry = ttk.Entry(self.main_frame)
        self.num_processes_entry.grid(row=0, column=1, sticky="w")

        ttk.Button(self.main_frame, text="Adicionar Processos", command=self.create_process_input_fields).grid(row=0, column=2, sticky="w")
        ttk.Label(self.main_frame, text="Separe as páginas com espaços.").grid(row=0, column=4, sticky="w")
        
         # Frame para os inputs de cada processo
        self.processes_frame = ttk.Frame(self.main_frame)
        self.processes_frame.grid(row=1, column=0, columnspan=3, sticky="w")
        
        ttk.Label(self.main_frame, text="Algoritmo de Escalonamento de Processos:").grid(row=2, column=0, sticky="e")
        self.algorithm_combobox = ttk.Combobox(self.main_frame, values=["FIFO", "SJF", "Round Robin", "EDF"])
        self.algorithm_combobox.grid(row=2, column=1, sticky="w")

        ttk.Label(self.main_frame, text="Quantum:").grid(row=2, column=2, sticky="e")
        self.quantum_entry = ttk.Entry(self.main_frame)
        self.quantum_entry.insert(0, "2") # Valor default
        self.quantum_entry.grid(row=2, column=3, sticky="w")

        ttk.Label(self.main_frame, text="Sobrecarga:").grid(row=2, column=4, sticky="e")
        self.sobrecarga_entry = ttk.Entry(self.main_frame)
        self.sobrecarga_entry.insert(0, "0") # Valor default
        self.sobrecarga_entry.grid(row=2, column=5, sticky="w", padx= 20)

        ttk.Label(self.main_frame, text="Algoritmo de Substuição de Páginas:").grid(row=3, column=0, sticky="e")
        self.algorithm_paginas_combobox = ttk.Combobox(self.main_frame, values=["FIFO", "LRU"])
        self.algorithm_paginas_combobox.grid(row=3, column=1, sticky="w")

        ttk.Button(self.main_frame, text="Iniciar Simulação", command=self.start_simulation).grid(row=3, column=2, columnspan=4, pady=10)

        # Canvas para o Gráfico de Gantt
        self.gantt_canvas = tk.Canvas(self.main_frame, width=1000, height=400, bg="white")
        self.gantt_canvas.grid(row=4, column=0, columnspan=4, sticky="w", padx=0, pady=10)

        # Scroll do Gráfico de Gantt
        yCanvasScrollbar = tk.Scrollbar(self.main_frame, orient = "vertical", command=self.gantt_canvas.yview)
        yCanvasScrollbar.grid(row=4, column=4, sticky="ns")
        xCanvasScrollbar = tk.Scrollbar(self.main_frame, orient = "horizontal", command=self.gantt_canvas.xview)
        xCanvasScrollbar.grid(row=5, column=0, columnspan=4, sticky="ew")
        self.gantt_canvas.configure(xscrollcommand=xCanvasScrollbar.set, yscrollcommand=yCanvasScrollbar.set)

        self.cpu_usage_label = ttk.Label(self.main_frame, text="Uso da CPU:")
        self.cpu_usage_label.grid(row=6, column=0, columnspan=4, sticky="w", padx=10)
        self.cpu_usage_text = tk.Text(self.main_frame, height=10, width=80)
        self.cpu_usage_text.grid(row=7, column=0, columnspan=4, sticky="w", padx=10)

        self.ram_usage_label = ttk.Label(self.main_frame, text="Uso da RAM:")
        self.ram_usage_label.grid(row=6, column=4, columnspan=4, sticky="w", padx=10)
        self.ram_canvas = tk.Canvas(self.main_frame, height=170, width=380, bg="white")
        self.ram_canvas.grid(row=7, column=4, columnspan=4, sticky="w", padx=10)
        
        self.turnaround_label = ttk.Label(self.main_frame, text="Turnaround Médio:")
        self.turnaround_label.grid(row=8, column=0, columnspan=4, sticky="w", padx=10)
        self.turnaround_text = ttk.Label(self.main_frame, text="")
        self.turnaround_text.grid(row=9, column=0, columnspan=4, sticky="w", padx=10)
        
        self.processos = []
        self.process_input_fields = []
        self.timeline = []
        self.process_start_time = {}
        self.animation_running = False
        
        self.update_scroll_region() # Atualiza o scroll region ao iniciar
    
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
               "Páginas": ("entry", "")
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
      
      self.update_scroll_region()
      
    def update_scroll_region(self):
        self.main_frame.update_idletasks()
        self.main_canvas.config(scrollregion=self.main_canvas.bbox("all"))
       

    def collect_process_data(self):
        self.processos = []
        for i, fields in enumerate(self.process_input_fields):
              try:
                chegada = int(fields["Chegada"].get())
                execucao = int(fields["Execução"].get())
                deadline = int(fields["Deadline"].get())
                paginas = [int(item) for item in fields["Páginas"].get().split()]
                
                processo = Processo(i + 1, chegada, execucao, deadline, paginas)
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
        self.ram_canvas.delete("rambox") # Limpa o canvas antigo
        self.ram_slots = []
        self.latest_filled_slot = -1
        self.latest_highlighted_slot = -1
        
        algoritmo = self.algorithm_combobox.get()
        quantum = int(self.quantum_entry.get())
        sobrecarga = int(self.sobrecarga_entry.get())
        algoritmo_paginas = self.algorithm_paginas_combobox.get()
        
        if any(len(p.paginas) > 0 for p in self.processos) and algoritmo_paginas != "FIFO" and algoritmo_paginas != "LRU":
            messagebox.showerror("Erro", "Selecione um algoritmo de substituição de Páginas.")
            self.animation_running = False
            return

        if algoritmo == "FIFO":
            self.create_ram_bars()
            self.simulate_fifo(0)
        elif algoritmo == "SJF":
            self.create_ram_bars()
            self.simulate_sjf(0)
        elif algoritmo == "Round Robin":
            self.create_ram_bars()
            self.simulate_round_robin(0, quantum, sobrecarga)
        elif algoritmo == "EDF":
            self.create_ram_bars()
            self.simulate_edf(0, quantum, sobrecarga)
        else:
            messagebox.showerror("Erro", "Selecione um algoritmo de escalonamento de Processos.")
            self.animation_running = False
        
        self.master.after(50, lambda: self.update_scroll_region())

        self.animation_running = True
        for p in self.processos:
            self.create_process_id_gantt_bar(p.id)
        self.animation_running = False

    def simulate_fifo(self, current_time):
        processos_ordenados = sorted(self.processos, key=lambda p: p.chegada)
        
        if all(p.concluido for p in processos_ordenados):
             self.calculate_and_update_results(processos_ordenados)
             self.animation_running = False
             self.fill_counter_bars(current_time)
             return

        processo = next((p for p in processos_ordenados if not p.concluido), None)

        if processo is None:
            self.fill_counter_bars(current_time)
            return
        
        if processo:
            if current_time < processo.chegada:
                self.create_gantt_bar(processo.id, current_time, processo.chegada, "wait", processo.inicio)
                current_time = processo.chegada

            processo.inicio = current_time
           
            exec_start_time = current_time
            current_time += processo.execucao
            processo.fim = current_time
            
            self.simulate_page_substitution(current_time, processo.paginas)
            wait_time = 0 if len(processo.paginas) == 0 else (500 * (len(processo.paginas) + 1)) + 500
            self.master.after(wait_time, lambda: self.create_gantt_bar(processo.id, exec_start_time, processo.fim, "execucao", processo.inicio))
            
            processo.concluido = True
            
            # Criar a barra de espera somente se não é o processo sendo executado
            for p in self.processos:
                if p != processo and p.chegada <= current_time and not p.concluido and p.tempo_restante > 0:
                     if current_time != p.inicio:
                        self.create_gantt_bar(p.id, p.chegada, current_time, 'wait', processo.inicio)
        
            wait_time = wait_time + 500
            self.master.after(wait_time, lambda: self.simulate_fifo(current_time))
    
    def simulate_sjf(self, current_time):
         processos_restantes = [p for p in self.processos if not p.concluido]
         
         if not processos_restantes:
              self.calculate_and_update_results(self.processos)
              self.animation_running = False
              self.fill_counter_bars(current_time)
              return

         processos_disponiveis = [p for p in processos_restantes if p.chegada <= current_time]
          
         if not processos_disponiveis:
              self.master.after(500, lambda: self.simulate_sjf(current_time + 1))
              return
        
         processo = min(processos_disponiveis, key=lambda p: p.execucao)

         processo.inicio = current_time
       
         exec_start_time = current_time
         current_time += processo.execucao
         processo.fim = current_time
         self.simulate_page_substitution(current_time, processo.paginas)
         wait_time = 0 if len(processo.paginas) == 0 else (500 * (len(processo.paginas) + 1)) + 500
         self.master.after(wait_time, lambda: self.create_gantt_bar(processo.id, exec_start_time, processo.fim, "execucao", processo.inicio))
               
         processo.concluido = True

         # Criar a barra de espera imediatamente para outros processos
         for p in self.processos:
              if p != processo and p.chegada <= current_time and not p.concluido and p.tempo_restante > 0:
                   if current_time != p.inicio:
                    self.create_gantt_bar(p.id, p.chegada, current_time, 'wait', processo.inicio)
         
         wait_time = wait_time + 500
         self.master.after(wait_time, lambda: self.simulate_sjf(current_time))

    def simulate_round_robin(self, current_time, quantum, sobrecarga):
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
                self.fill_counter_bars(current_time)
                return
            else:  # Aguardar o próximo instante
                self.master.after(500, lambda: self.simulate_round_robin(current_time + 1, quantum, sobrecarga))
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

        # Substitui as páginas necessárias para o processo
        self.simulate_page_substitution(current_time, processo.paginas)
        wait_time = 0 if len(processo.paginas) == 0 else (500 * (len(processo.paginas) + 1)) + 600

        # Criar barra de execução no gráfico de Gantt
        self.master.after(wait_time, lambda: self.create_gantt_bar(processo.id, start, current_time, 'execucao', processo.inicio))

        # Verificar se o processo foi concluído
        if processo.tempo_restante <= 0:
            processo.fim = current_time
            processo.concluido = True
        else:
            # Aplicar sobrecarga
            if sobrecarga > 0:
                sobrecarga_inicio = current_time
                current_time += sobrecarga
                self.master.after(wait_time + 50, lambda:self.create_gantt_bar(processo.id, sobrecarga_inicio, current_time, 'sobrecarga', processo.inicio))
        
        # Criar barra de espera imediatamente para outros processos
        for p in self.processos:
           if p != processo and p.chegada <= current_time and not p.concluido and p.tempo_restante > 0:
               wait_start_time = p.chegada if p.chegada > start else start
               self.create_gantt_bar(p.id, wait_start_time, current_time, 'wait', processo.inicio)

        # Chamar a próxima execução
        wait_time += 550
        self.master.after(wait_time, lambda: self.simulate_round_robin(current_time, quantum, sobrecarga))
       
    def simulate_edf(self, current_time, quantum, sobrecarga):
      queue = [p for p in self.processos if not p.concluido]
      if not queue:
            self.calculate_and_update_results(self.processos)
            self.animation_running = False
            self.fill_counter_bars(current_time)
            return
      
        # Filtrar processos que ja chegaram
      queue = [p for p in queue if p.chegada <= current_time]
        
       # Caso todos os processos ainda não tenham chegado espera
      if not queue:
           self.master.after(500, lambda: self.simulate_edf(current_time + 1, quantum, sobrecarga))
           return

      queue.sort(key=lambda p: p.deadline)
      processo = queue[0]

      self.simulate_page_substitution(current_time, processo.paginas)
      wait_time = 0 if len(processo.paginas) == 0 else (500 * (len(processo.paginas) + 1)) + 500
     
      if current_time < processo.chegada and not processo.concluido:
         self.create_gantt_bar(processo.id, current_time, processo.chegada, 'wait', processo.inicio)
         current_time = processo.chegada
         
      execute_time = min(quantum, processo.tempo_restante)
      start = current_time
      current_time += execute_time
      processo.tempo_restante -= execute_time
      
      if processo.inicio is None:
         processo.inicio = start
    
      execution_time_start = max(start, processo.deadline)
      execution_time_end = min(current_time, processo.deadline)
      
      if execution_time_end > start:
         self.master.after(wait_time, lambda: self.create_gantt_bar(processo.id, start, execution_time_end, 'execucao', processo.inicio))
      if current_time > processo.deadline:
         self.master.after(wait_time + 50, lambda: self.create_gantt_bar(processo.id, execution_time_start, current_time, 'deadline', processo.inicio))

      if processo.tempo_restante <= 0:
           processo.fim = current_time
           processo.concluido = True
           queue.pop(0)
      else:
           if sobrecarga > 0:
              sobrecarga_inicio = current_time
              current_time += sobrecarga
              wait_time += 50
              self.master.after(wait_time + 50, lambda: self.create_gantt_bar(processo.id, sobrecarga_inicio, current_time, 'sobrecarga', processo.inicio))
           queue.pop(0)
           queue.insert(0, processo)

      for p in self.processos:
          if p != processo and p.chegada <= current_time and not p.concluido and p.tempo_restante > 0:
              wait_start_time = p.chegada if p.chegada > start else start
              self.create_gantt_bar(p.id, wait_start_time, current_time, 'wait', processo.inicio)
       
      wait_time += 550
      self.master.after(wait_time, lambda: self.simulate_edf(current_time, quantum, sobrecarga))

    def simulate_page_substitution(self, current_time, paginas_processo):
        paginas = paginas_processo
        if len(paginas) == 0:
            return

        algoritmo = self.algorithm_paginas_combobox.get()
        primeira_pagina = paginas[0]
        paginas = paginas[1:]   # remove primeiro item

        if algoritmo == "FIFO":
            self.simulate_page_fifo(primeira_pagina, current_time)
        else:
            self.simulate_page_lru(primeira_pagina, current_time)

        self.master.after(500, lambda: self.simulate_page_substitution(current_time, paginas))

    def simulate_page_fifo(self, pagina, current_time):
        idx = -1
        for i in range(len(self.ram_slots)):
            if (self.ram_slots[i].pagina == pagina):
                idx = i
                break
    
        # remove destaque dos últimos adicionados
        self.highlight_ram_box(max(self.latest_highlighted_slot, 0), "white")
        self.highlight_ram_box(max(self.latest_filled_slot, 0), "white")

        if (idx != -1):
            # incrementar uso no lru
            self.highlight_ram_box(idx, "cyan")
            self.latest_highlighted_slot = idx
            return

        slot = SlotPagina(-1, pagina, current_time, current_time)
        if (len(self.ram_slots) < 50):
            slot.slot = len(self.ram_slots)
            self.ram_slots.append(slot)
            self.highlight_ram_box(slot.slot, "cyan")
            self.latest_filled_slot = slot.slot
            return
        
        latest_slot_idx = self.latest_filled_slot
        if (latest_slot_idx == 49):
            latest_slot_idx = -1

        slot.slot = latest_slot_idx + 1
        self.ram_slots[slot.slot] = slot
        self.highlight_ram_box(slot.slot, "cyan")
        self.latest_filled_slot = slot.slot

    def simulate_page_lru(self, pagina, current_time):
        idx = -1
        for i in range(len(self.ram_slots)):
            if (self.ram_slots[i].pagina == pagina):
                idx = i
                break
    
        # remove destaque do último destacado
        self.highlight_ram_box(max(self.latest_highlighted_slot, 0), "white")

        if (idx != -1):
            self.highlight_ram_box(idx, "cyan")
            self.latest_highlighted_slot = idx
            self.ram_slots[idx].uso = current_time
            return

        slot = SlotPagina(-1, pagina, current_time, current_time)
        slots_ordenados = sorted(self.ram_slots, key=lambda p: p.uso)

        if (len(self.ram_slots) < 50):
            slot.slot = len(self.ram_slots)
            self.ram_slots.append(slot)
            self.highlight_ram_box(slot.slot, "cyan")
            self.latest_highlighted_slot = slot.slot
            return
        
        slot.slot = slots_ordenados[0].slot
        self.ram_slots[slot.slot] = slot
        self.highlight_ram_box(slot.slot, "cyan")
        self.latest_highlighted_slot = slot.slot

    # Altera cor e texto da caixa
    def highlight_ram_box(self, identifier, color):
        if (len(self.ram_slots) <= identifier):
            return

        pagina = self.ram_slots[identifier].pagina
        self.ram_canvas.itemconfigure(f"ram_box_{identifier}", fill=color)
        self.ram_canvas.itemconfigure(f"ram_text_{identifier}", text=pagina)

    def fill_counter_bars(self, max_time):
        for start in range(max_time):
            self.create_counter_gantt_bar(start)

    def create_gantt_bar(self, process_id, start, end, tipo, start_time):
        if not start_time or process_id not in self.process_start_time:
            self.process_start_time[process_id] = start
          
        # start = self.process_start_time[process_id]
        
        largura = (end - start) * 50
        x0 = start * 50 + 30
        y0 = (process_id) * 40  # Ajustar para posicionamento vertical
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
        # self.gantt_canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=f"({start}-{end})", tags=f"processo_{process_id}")
        self.gantt_canvas.config(scrollregion=self.gantt_canvas.bbox("all"))

    def create_counter_gantt_bar(self, start):
        end = start + 1
        x0 = start * 50 + 30
        y0 = 10 # Ajustar para posicionamento vertical
        x1 = x0 + 50
        y1 = y0 + 20
        cor = "white"

        self.gantt_canvas.create_rectangle(x0, y0, x1, y1, fill=cor, tags=f"counter_bar")
        self.gantt_canvas.create_text(x1 - 3, (y0 + y1) / 2, text=f"{end}", tags=f"counter_bar", anchor="e")
        self.gantt_canvas.config(scrollregion=self.gantt_canvas.bbox("all"))

    def create_process_id_gantt_bar(self, process_id):        
        largura = 20
        x0 = 0
        y0 = (process_id) * 40
        x1 = x0 + largura
        y1 = y0 + 30
        cor = "white"

        self.gantt_canvas.create_rectangle(x0, y0, x1, y1, fill=cor, tags=f"processo_{process_id}")
        self.gantt_canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=f"P{process_id}", tags=f"processo_{process_id}")
        self.gantt_canvas.config(scrollregion=self.gantt_canvas.bbox("all"))
    
    def create_ram_bars(self):
        for x in range(10):
            for y in range(5):
                xi = (x * 37) + 5
                xf = xi + 32
                yi = (y * 34) + 5
                yf = yi + 20

                i = (x * 5) + y
                self.ram_canvas.create_rectangle(xi, yi, xf, yf, fill="white", tags=f"ram_box_{i}")
                self.ram_canvas.create_text((xi + xf)/2, (yi + yf)/2, text=f"-", tags=f"ram_text_{i}")
                self.ram_canvas.config(scrollregion=self.ram_canvas.bbox("rambox"))

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