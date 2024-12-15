    document.addEventListener('DOMContentLoaded', function() {
        const dropArea = document.getElementById('drop-area');
        const fileInput = document.getElementById('excelFileInput');
        const dropText = document.getElementById('drop-text');

        // Evita el comportamiento por defecto para arrastrar y soltar
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        // Resalta el área de drag & drop cuando se arrastra un archivo
        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, function() {
                dropArea.classList.add('drag-over');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, function() {
                dropArea.classList.remove('drag-over');
            }, false);
        });

        // Maneja el evento de soltar para cargar el archivo
        dropArea.addEventListener('drop', function(e) {
            const dt = e.dataTransfer;
            const files = dt.files;

            if (files.length > 0) {
                fileInput.files = files;  // Asigna el archivo arrastrado al input de archivo

                // Actualiza el texto para mostrar el nombre del archivo seleccionado
                dropText.innerHTML = `Archivo seleccionado: ${files[0].name}`;
            }
        });

        // Habilita seleccionar el archivo al hacer clic en el área
        dropArea.addEventListener('click', function() {
            fileInput.click();
        });

        // Actualiza el texto cuando se selecciona un archivo a través del input
        fileInput.addEventListener('change', function() {
            if (fileInput.files.length > 0) {
                dropText.innerHTML = `Archivo seleccionado: ${fileInput.files[0].name}`;
            }
        });
    });

    document.getElementById("excelUploadForm").onsubmit = function() {
        document.querySelector("button[type='submit']").disabled = true;
    };
    



    <div class="excel-upload-section mt-4">
        <h4>Cargar artículos desde Excel</h4>
        <form id="excelUploadForm" action="{% url 'cargar_desde_excel' %}" method="post" enctype="multipart/form-data">
            {% csrf_token %}
        </form>        
            <div id="drop-area" class="drop-area p-5 mb-3 text-center" onclick="document.getElementById('excelFileInput').click();">
                <p id="drop-text" class="text-muted">Arrastra y suelta el archivo aquí o haz clic para seleccionarlo</p>
                <input type="file" name="excel_file" id="excelFileInput" accept=".xlsx, .xls" class="form-control-file" required hidden>
            </div>
            <p id="file-name" class="text-success mt-2" style="display: none;"></p>
            <button type="submit" class="btn btn-success">Cargar</button>
        </form>
    </div>   

    {% if nombres %}
    <h5>Lista de Nombres Extraídos:</h5>
    <ul>
        {% for nombre in nombres %}
            <li>{{ nombre }}</li>
        {% endfor %}
    </ul>
    {% else %}
        <p>No se encontraron nombres en el archivo cargado.</p>
    {% endif %}


    
    <script src="{% static 'js/script.js' %}"></script>

    <script>
    document.addEventListener("DOMContentLoaded", function() {
        const form = document.getElementById("excelUploadForm");
        const submitButton = form.querySelector("button[type='submit']");

        form.onsubmit = function() {
            submitButton.disabled = true;  // Deshabilita el botón para evitar múltiples envíos
        };
    });
</script>


path('cargar-desde-excel/', views.cargar_desde_excel, name='cargar_desde_excel'),




def cargar_desde_excel(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        try:
            # Cargar el archivo en un DataFrame
            df = pd.read_excel(excel_file)
            if 'nombre' in df.columns:
                nombres = df['nombre'].dropna().tolist()
                print(nombres)  # Verifica que la lista se genere correctamente
                messages.success(request, "Archivo cargado exitosamente.")
                return render(request, 'cart.html', {'nombres': nombres})
            else:
                messages.error(request, "El archivo no contiene una columna llamada 'nombre'.")
        except Exception as e:
            messages.error(request, f"Error al procesar el archivo: {e}")
    return render(request, 'cart.html')

    
from django.contrib import messages
import pandas as pd