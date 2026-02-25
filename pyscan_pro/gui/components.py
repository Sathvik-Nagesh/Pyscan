import customtkinter as ctk

class CTkScrollableTable(ctk.CTkScrollableFrame):
    """
    A simple custom table implementation using CTkScrollableFrame.
    CustomTkinter doesn't have a built-in Treeview/Table yet, 
    so we build one grid-based for a premium modern look.
    """
    def __init__(self, master, columns, **kwargs):
        super().__init__(master, **kwargs)
        self.columns = columns
        self.rows = []
        
        # Configure grid columns to weigh equally conceptually, but fixed weights
        for i, col in enumerate(self.columns):
            self.grid_columnconfigure(i, weight=1)
            # Create Header
            header = ctk.CTkLabel(self, text=col, font=("Roboto", 14, "bold"), text_color="#1f6aa5")
            header.grid(row=0, column=i, padx=5, pady=(5, 10), sticky="w")
            
    def insert_row(self, values):
        """Inserts a new row into the table."""
        row_index = len(self.rows) + 1
        current_row = []
        
        for i, val in enumerate(values):
            color = "#e0e0e0"
            if i == 2: # Status column
                if val == "OPEN": color = "#2ecc71"
                elif val == "FILTERED": color = "#f39c12"
                elif val == "CLOSED": color = "#e74c3c"
                
            cell = ctk.CTkLabel(self, text=str(val), font=("Roboto", 13), text_color=color, anchor="w")
            cell.grid(row=row_index, column=i, padx=5, pady=2, sticky="w")
            current_row.append(cell)
            
        self.rows.append(current_row)

    def clear(self):
        """Clears all rows except the header."""
        for row in self.rows:
            for cell in row:
                cell.destroy()
        self.rows.clear()
