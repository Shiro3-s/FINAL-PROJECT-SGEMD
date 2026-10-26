with open('lib_js.py','r',encoding='utf-8') as f: 
    content = f.read()

# 1. Replace the fall-through group that includes registrar-avance
# Current: case "editar": ... case "registrar-avance": ... case "asignar": ... case "editar-sensores":
# New: give registrar-avance its own dedicated handler, add case "asignar-docente"

# Find and replace the specific section
old = '''      case "editar":
      case "registrar-avance":
      case "asignar":
      case "editar-sensores":
        e.preventDefault();
        abrirEditor("Editar registro", registro);
        break;'''

new = '''      case "editar":
        e.preventDefault();
        abrirEditor("Editar registro", registro);
        break;

      case "registrar-avance":
        e.preventDefault();
        var fila = filaDe(b);
        if (!fila) return;
        var cod = fila.dataset.cod;
        var emp = fila.dataset.emp;
        var estu = fila.dataset.estu;
        var etapa = fila.dataset.etapa;
        var avanceActual = Number(fila.dataset.avance || 0);
        // Llenar prefill en el formulario embebido
        document.querySelector("[name=emp]").value = emp;
        document.querySelector("[name=estu]").value = estu;
        document.querySelector("[name=etapa]").value = etapa;
        document.querySelector("[name=avance]").value = Math.round(avanceActual);
        abrirFormulario("Registrar avance", "form-avance", b, "Guardar", "Avance guardado");
        break;

      case "asignar-docente":
        e.preventDefault();
        var fila = filaDe(b);
        if (!fila) return;
        var cod = fila.dataset.cod;
        var emp = fila.dataset.emp;
        var estu = fila.dataset.estu;
        // Prefill: bloquear campos Estudiante/Emprendimiento/Correo
        var modal = document.querySelector("#form-asignar-docente");
        if (modal) {
          modal.querySelector("[name=estudiante]").value = estu;
          modal.querySelector("[name=emprendimiento]").value = emp;
          modal.querySelector("[name=correo]").value = CORREOS_EST[estu] || "";
          // Bloquear inputs
          var campos = modal.querySelectorAll("input, select");
          campos.forEach(function(c) { c.disabled = true; });
          // Mostrar badge asignado
          var badge = modal.querySelector(".badge-asignado");
          if (badge) badge.textContent = "Asignado a " + estu;
          // Refrescar vacío
          if (typeof vacioRefrescar === "function") vacioRefrescar();
          abrirModal("Asignar docente", plantillaModal("form-asignar-docente"), [
            { txt: "Cancelar", clase: "btn btn-secundario" },
            { txt: "Confirmar", clase: "btn btn-primario", alClic: function() {
              // Guardar asignación y cerrar
              toast("Docente asignado", "ok");
              if (typeof vacioRefrescar === "function") vacioRefrescar();
              cerrarModal();
            } }
          ]);
        }
        break;'''
        
if old in content:
    content = content.replace(old, new)
    with open('lib_js.py','w',encoding='utf-8') as f:
        f.write(content)
    print('Added registrar-avance dedicated + asignar-docente')
else:
    print('Old pattern not found, searching...')
    if 'case "registrar-avance"' in content:
        print('registrar-avance exists already')
    if 'case "asignar-docente"' in content:
        print('asignar-docente already exists')